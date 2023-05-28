import serial, os, ast, json, datetime
import paho.mqtt.client as mqtt
from mysql_service import MySQLService

from dotenv import load_dotenv

load_dotenv()
lights_dict = {
    "1": 1,
    "Corridor": 2,
    "2": 3,
}

aircon_dict = {
    "1": 4,
    "2": 5
}

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()

def load_configs():
    with mysql:
        data = mysql.get_all("appliance_status")
        message = {
            "title": "Load Configurations",
            "sender": "Edge",
            "room1Status": data[0]["status"],
            "corridorStatus": data[1]["status"],
            "room2Status": data[2]["status"],
            "aircon": [
            {
                "status": data[3]["status"],
                "temp": data[3]["status_value"]
            },
            {
                "status": data[4]["status"],
                "temp": data[4]["status_value"]
            }
            ],
            "ventilatingFanStatus": data[5]["status"],
        }
        ser.write(str.encode(json.dumps(message)))

def read_serial_input():
    while True:
        if (ser.in_waiting > 0):
            temp = ser.readline()
            print(f"Received from Arduino {temp}")
            input = ast.literal_eval(temp.decode('utf-8').rstrip())
            if (input["title"] == "Arduino Ready"):
                load_configs()
            else:
                input["sender"] = "Edge"
                with mysql:
                    if (input["title"] == "Room Count"):
                        input["room"] = int(input["room"])
                        if (input["action"] == "Inc"):
                            mysql.increment_field("people_in_room", ["room_id"], "people_count", [input["room"]])
                        elif (input["action"] == "Dec"):
                            mysql.decrement_field("people_in_room", ["room_id"], "people_count" [input["room"]])
                    elif (input["title"] == "Lights"):
                        mysql.update("appliance_status", ["status"], ["appliance_id"], [input["status"], lights_dict[input["room"]]])
                    elif (input["title"] == "Ventilating Fan"):
                        mysql.update("appliance_status", ["status"], ["appliance_id"], [input["status"], 6])       
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
            ser.write(str.encode(json.dumps(json_message)))
            with mysql:
                if json_message["title"] == "Lights":
                    mysql.update("appliance_status", ["status"], ["appliance_id"], [json_message["status"], lights_dict[json_message["room"]]])
                elif json_message["title"] == "Ventilating Fan":
                    mysql.update("appliance_status", ["status"], ["appliance_id"], [json_message["status"], 6])
                elif json_message["title"] == "Aircon Switch":
                    mysql.update("appliance_status", ["status"], ["appliance_id"], [json_message["status"], aircon_dict[json_message["room"]]])
                elif json_message["title"] == "Aircon Temp":
                    mysql.update("appliance_status", ["status_value"], ["appliance_id"], [json_message["temp"], aircon_dict[json_message["room"]]])
        if (json_message["title"] in ["Lights", "Aircon Switch", "Ventilating Fan"]):
            appliance_id = lights_dict[json_message["room"]] if json_message["title"] == "Lights" else aircon_dict[json_message["room"]] if json_message["title"] == "Aircon Switch" else 6
            with mysql:
                data = mysql.get_by_id("appliance_uptime", ["appliance_id", "date"], [int(appliance_id), datetime.datetime.now().strftime("%Y-%m-%d")])
                message = {
                    "title": "Update Uptime",
                    "sender": "Edge",
                    "appliance_id": appliance_id,
                    "uptime": data["uptime"]
                }
                print(json.dumps(message))
            client.publish(topic, json.dumps(message))
        print("Received message: ", msg.payload.decode())
    
client = mqtt.Client()
client.username_pw_set(username=os.getenv("LOCAL_MQTT_USERNAME"), password=os.getenv("LOCAL_MQTT_PASSWORD")) # type: ignore
client.on_connect = on_connect 
client.on_publish = on_publish
client.on_message = on_message
client.connect(os.getenv("LOCAL_MQTT_HOST"), int(os.getenv("LOCAL_MQTT_PORT")), 60) # type: ignore
mysql = MySQLService(os.getenv("LOCAL_DATABASE_HOST"), os.getenv("LOCAL_DATABASE_USERNAME"), os.getenv("LOCAL_DATABASE_PASSWORD"), os.getenv("LOCAL_DATABASE_NAME"))
topic = "/john_node"
client.subscribe(topic)
client.loop_start()
read_serial_input()


