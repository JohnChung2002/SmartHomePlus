import mysql.connector
import serial
import datetime
import time
import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from threading import Thread, Timer
from mysql_service import MySQLService

device = '/dev/ttyACM0'
arduino = serial.Serial(device, 9600)

load_dotenv()

five_minute_timer = None

def every_five_minutes_function():
    #do something every minute
    with mydb:
        result = mydb.get_avg_of_environment()
        if result is not None and result["temperature"] is not None and result["brightness"] is not None and result["wetness"] is not None:
            client.publish(topic, f"{result['temperature']},{result['brightness']},{result['wetness']}")

def every_five_minutes_cron_thread():
    global five_minute_timer
    # Run the function every minute
    if five_minute_timer is not None:
        five_minute_timer.cancel()
    five_minute_timer = Timer(300, every_five_minutes_cron_thread).start()
    every_five_minutes_function()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with RC: {str(rc)}")
    pass

def on_publish(client, data, result):
    print("Message sent to MQTT broker")
    pass

def on_message(client, userdata, msg):
    message_mqtt = msg.payload.decode()
    print(message_mqtt)
    if message_mqtt == "Sprinkler Off":
        arduino.write(b"Off")
    elif message_mqtt == "Sprinkler On":
        arduino.write(b"On")           
    elif message_mqtt == "Spray at intruder":
        arduino.write(b"Spray")
    elif message_mqtt == "Gonna Rain":
        arduino.write(b"GonnaRain")
    else:
        message_mqtt = message_mqtt.split(",")
        if len(message_mqtt) == 2 and message_mqtt[0] == "Update Wetness Threshold":
            wetnessThreshold = int(message_mqtt[1])
            with mydb:
                mydb.update("system_data", ["status"], ["field"], [wetnessThreshold, "wetness_value"])
                print("Wetness Threshold Updated")
            message = f"Update|{wetnessThreshold}"
            arduino.write(str.encode(message))
    time.sleep(1)
 
client = mqtt.Client()
client.username_pw_set(username=os.getenv("LOCAL_MQTT_USERNAME"), password=os.getenv("LOCAL_MQTT_PASSWORD")) # type: ignore
client.on_connect = on_connect 
client.on_publish = on_publish
client.on_message = on_message
client.connect(os.getenv("LOCAL_MQTT_HOST"), int(os.getenv("LOCAL_MQTT_PORT")), 60) # type: ignore
topic = "/cheryl_node"
client.subscribe(topic)
client.loop_start()
mydb = MySQLService(os.getenv("LOCAL_DATABASE_HOST"), os.getenv("LOCAL_DATABASE_USERNAME"), os.getenv("LOCAL_DATABASE_PASSWORD"), os.getenv("LOCAL_DATABASE_NAME")) 
every_five_minutes_cron_thread()

while True:
    while(arduino.in_waiting == 0):
        pass
    with mydb:
        data = mydb.get_by_id("system_data", ["field"], ["wetness_value"])
        wetnessThreshold = data["status"]
        print("Wetness Threshold:", wetnessThreshold)
    data = arduino.readline().decode('utf-8').strip()
    print("Received data:", data) # Print received data for debugging
    if (data == "Sprinkler turned ON"):
        with mydb:
            mydb.update("system_data", ["status"], ["field"], [1, "water_sprinkler_status"])
    elif (data == "Sprinkler turned OFF"):
        with mydb:
            mydb.update("system_data", ["status"], ["field"], [0, "water_sprinkler_status"])
    else:
        readings = data.split(",")
        if len(readings) == 3:
            wetnessLevel = 0 if readings[0] == "" else int(readings[0])
            brightness = int(readings[1])  
            temperature = int(readings[2])
            # Parse sensor readings from received data
            print(wetnessLevel, brightness, temperature)         
            with mydb:
                mydb.insert("environment_data", ["temperature", "brightness", "wetness"], [temperature, brightness, wetnessLevel])
    time.sleep(0.1)
        
