import serial
import os
import ast
import json
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
            input["sender"] = "Edge"
            if (input["title"] in ["Room Count", "Lights", "Ventilating Fan"]):
                client.publish(topic, json.dumps(input))

def on_connect(client, userdata, flags, rc):
    print(f"Connected with RC: {str(rc)}")
    pass
    
def on_publish(client, data, result):
    print("Message sent to MQTT broker")
    pass

def on_message(client, userdata, msg):
    json_message = ast.literal_eval(msg.payload.decode())
    if (json_message["sender"] == "Cloud"):
        if (json_message["title"] in ["Lights", "Intruder", "Ventilating Fan", "Aircon Switch", "Aircon Temp", "Disengage Override"]):
            ser.write(str.encode(json.dumps(input)))
        print("Received message: ", msg.payload.decode())
    
client = mqtt.Client()
client.username_pw_set(username=os.getenv("LOCAL_MQTT_USERNAME"), password=os.getenv("LOCAL_MQTT_PASSWORD")) # type: ignore
client.on_connect = on_connect 
client.on_publish = on_publish
client.connect(os.getenv("LOCAL_MQTT_HOST"), int(os.getenv("LOCAL_MQTT_PORT")), 60) # type: ignore

topic = "/john_node"
client.subscribe(topic)

client.loop_start()
read_serial_input()


