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
        arduino.write(b"1")
    elif message_mqtt == "Sprinkler On":
        arduino.write(b"2")           
    elif message_mqtt == "Spray at intruder":
        arduino.write(b"3")
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

while True:
    
    mydb = mysql.connector.connect(host="localhost", user="hp", password="0123", database="waterSprinkler_db")

    while(arduino.in_waiting == 0):
        pass

    # Create a cursor object
    cur = mydb.cursor()

    # Execute the SQL query to retrieve data from the database
    cur.execute("SELECT wetnessValue FROM settingTable")

    # Fetch all the rows returned by the query and print out the value
    value = cur.fetchall()
    wetnessThreshold = value[0][0]
    print(wetnessThreshold)
    
    data = arduino.readline().decode('utf-8').strip()
    print("Received data:", data) # Print received data for debugging

    # Parse sensor readings from received data
    readings = data.split(",")
    
    if len(readings) == 4:
        
        systemstat = str(readings[0])
        wetnessLevel = readings[1]
        if wetnessLevel == "":
            wetnessLevel = 0
        else:
            wetnessLevel = int(readings[1])
            
        brightness = int(readings[2])
        
        temperature = int(readings[3])
        
        if wetnessLevel < wetnessThreshold :
            status = "Soil is dry"            
        else:
            status = "Soil is moist"
            
        if brightness < 450:
            status2 = "Nighttime"            
        else:
            status2 = "Daytime"
            
        if temperature < 15:
            status3 = "Cool day"            
        else:
            status3 = "Hot day"
               
                    
    print(wetnessLevel, brightness, temperature)    
    print("Soil Moisture:", status, "Time of Day:", status2, "Temperature of Day:", status3)
    print(systemstat)
        
    
    
    with mydb:      

        mycursor = mydb.cursor() 
        mycursor.execute("INSERT INTO systemData (wetnessValue, soilMoisture, brightness, timeOfDay, temperature, tempStatus, sprinklerStatus) VALUES (%s, '%s', %s, '%s', %s, '%s', '%s')" %(wetnessLevel, status, brightness, status2, temperature, status3, systemstat))        
    
        mydb.commit()
        mycursor.close()

    client.publish(topic, f"{wetnessLevel},{brightness},{temperature}")
 
