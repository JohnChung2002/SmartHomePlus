import mysql.connector
import serial
import datetime
import time
import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

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
                mycursor = mydb.cursor()
                mycursor.execute("UPDATE system_data SET status = %s WHERE field = 'wetness_value'", (wetnessThreshold))
                mydb.commit()
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

mydb = mysql.connector.connect(host="localhost", user="hp", password="0123", database="waterSprinkler_db")
while True:
    while(arduino.in_waiting == 0):
        pass
    # Create a cursor object
    cur = mydb.cursor()
    # Execute the SQL query to retrieve data from the database
    cur.execute("SELECT status FROM system_data WHERE field = 'wetness_value'")
    # Fetch all the rows returned by the query and print out the value
    value = cur.fetchall()
    wetnessThreshold = value[0][0]
    cur.close()
    print(wetnessThreshold)
    data = arduino.readline().decode('utf-8').strip()
    print("Received data:", data) # Print received data for debugging
    if (data == "Sprinkler turned ON"):
        with mydb:
            mycursor = mydb.cursor()
            mycursor.execute("UPDATE system_data SET status = 1 WHERE field = 'water_sprinkler_status'")
            mydb.commit()
            mycursor.close()
    elif (data == "Sprinkler turned OFF"):
        with mydb:
            mycursor = mydb.cursor()
            mycursor.execute("UPDATE system_data SET status = 0 WHERE field = 'water_sprinkler_status'")
            mydb.commit()
            mycursor.close()
    else:
        readings = data.split(",")
        if len(readings) == 3:
            wetnessLevel = 0 if readings[0] == "" else int(readings[0])
            brightness = int(readings[1])  
            temperature = int(readings[2])
            # Parse sensor readings from received data
            print(wetnessLevel, brightness, temperature)         
            with mydb:      
                mycursor = mydb.cursor() 
                mycursor.execute("INSERT INTO environment_data (temperature, brightness, wetness) VALUES (%s, %s, %s)" %(brightness, wetnessLevel, temperature))        
                mydb.commit()
                mycursor.close()
            client.publish(topic, f"{wetnessLevel},{brightness},{temperature}")
        
