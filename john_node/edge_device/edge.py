import serial
import os
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
            input = temp.decode('utf-8').rstrip().split("|")

def on_connect(client, userdata, flags, rc):
    print("connected with rc: "+str(rc))
    pass
    
def on_publish(client, data, result):
    print("data published")
    pass
    
client = mqtt.Client()
client.username_pw_set(username=os.getenv("MQTT_USERNAME"), password=os.getenv("MQTT_PASSWORD")) # type: ignore
client.on_connect = on_connect 
client.on_publish = on_publish
client.connect(os.getenv("MQTT_HOST"), os.getenv("MQTT_PORT"), 60) # type: ignore


topic = "/something"
value = "cool"
ret = client.publish(topic, value)
