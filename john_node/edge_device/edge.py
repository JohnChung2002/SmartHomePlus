import serial
import os
import ast
import paho.mqtt.client as mqtt

from dotenv import load_dotenv

load_dotenv()

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()

def read_serial_input():
    while True:
        if (ser.in_waiting > 0):
            temp = ser.readline()
            print(f"Received from Arduino {temp}")
            input = ast.literal_eval(temp.decode('utf-8').rstrip())
            if (input["title"] == "Room Count"):
                topic = "/john_node/room_count"
                value = input["action"]
                client.publish(topic, value)
                
def on_connect(client, userdata, flags, rc):
    print("connected with rc: "+str(rc))
    pass
    
def on_publish(client, data, result):
    print("data published")
    pass
    
client = mqtt.Client()
client.username_pw_set(username=os.getenv("LOCAL_MQTT_USERNAME"), password=os.getenv("LOCAL_MQTT_PASSWORD")) # type: ignore
client.on_connect = on_connect 
client.on_publish = on_publish
client.connect(os.getenv("LOCAL_MQTT_HOST"), int(os.getenv("LOCAL_MQTT_PORT")), 60) # type: ignore

read_serial_input()


