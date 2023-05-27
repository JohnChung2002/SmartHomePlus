import mysql.connector
import serial
import datetime
import time
import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from mysql_service import MySQLService

device = '/dev/ttyACM0'
arduino = serial.Serial(device, 9600)

load_dotenv()

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
    else:
        message_mqtt = message_mqtt.split(",")
        if len(message_mqtt) == 2 and message_mqtt[0] == "Update Wetness Threshold":
            wetnessThreshold = message_mqtt[1]
            with mydb:
                mydb.update("system_data", ["status"], ["field"], [wetnessThreshold, "wetness_value"])
                print("Wetness Threshold Updated")
                mycursor.close()
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


while True:
    while(arduino.in_waiting == 0):
        pass
    with mydb:
        data = mydb.get_by_id("system_data", ["field"], ["wetness_value"])
        wetnessThreshold = data["status"]
        print(wetnessThreshold)
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
            client.publish(topic, f"{wetnessLevel},{brightness},{temperature}")
    time.sleep(0.1)
        
