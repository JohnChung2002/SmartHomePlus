from flask import Flask, g, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
import hmac
import hashlib
import time
import ast
import json
import paho.mqtt.client as mqtt
from threading import Thread
from shared.services.mysql_service import MySQLService
from dotenv import load_dotenv

from cheryl_node import bp_cheryl
from john_node import bp_john
from timmy_node import bp_timmy
from main import bp_main

load_dotenv()

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.secret_key =  os.getenv("APP_SECRET_KEY")
jwt = JWTManager(app)

cors = CORS(app, resources={r"/api/*" : {"origins": "*"}})

app.register_blueprint(bp_cheryl, url_prefix='/api/node_1')
app.register_blueprint(bp_john, url_prefix='/api/node_2')
app.register_blueprint(bp_timmy, url_prefix='/api/node_3')
app.register_blueprint(bp_main)

@app.route('/webhook', methods=['POST'])
def webhook():
    Thread(target=lambda: [os.system("git pull")]).start()
    return "ok"


@app.errorhandler(404)
def page_not_found(e):
    return ('''
    <body><h1>Not Found</h1>
    <p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
    </body>
    '''), 404

def request_has_connection():
    return (
        ("dbconn" in g) and (g.dbconn is not None)
        and
        ("client" in g)
    )

@app.before_request
def get_request_connection():
    if not request_has_connection():
        g.dbconn = MySQLService(os.getenv("CLOUD_DATABASE_HOST"), os.getenv("CLOUD_DATABASE_USERNAME"), os.getenv("CLOUD_DATABASE_PASSWORD"), os.getenv("CLOUD_DATABASE_NAME")) # type: ignore
        g.client = client

@app.teardown_request
def close_db_connection(ex):
    if request_has_connection():
        dbconn = g.pop('dbconn', None)
        g.pop('client', None)
        if (dbconn is not None):
            dbconn.close()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with RC: {str(rc)}")
    pass
    
def on_publish(client, data, result):
    print("Message sent to MQTT broker")
    pass

def on_message(client, userdata, msg):
    json_message = ast.literal_eval(msg.payload.decode())
<<<<<<< Updated upstream
    print("Received message: ", msg.payload.decode())
=======
    print(msg.payload.decode())
>>>>>>> Stashed changes
    if msg.topic == "/john_node":
        if (json_message["sender"] == "Edge"):
            print("Received message: ", msg.payload.decode())
    if msg.topic == "/cheryl_node":
        if (json_message["sender"] == "Edge"):
            print("Received message: ", msg.payload.decode())
    if msg.topic == "/timmy_node":
        if (json_message["sender"] == "Edge"):
            print("Received message: ", msg.payload.decode())
    
client = mqtt.Client()
client.username_pw_set(username=os.getenv("CLOUD_MQTT_USERNAME"), password=os.getenv("CLOUD_MQTT_PASSWORD")) # type: ignore
client.on_connect = on_connect 
client.on_publish = on_publish
client.connect(os.getenv("CLOUD_MQTT_HOST"), int(os.getenv("CLOUD_MQTT_PORT")), 60) # type: ignore
topic = [("/john_node", 0), ("/cheryl_node", 0), ("/timmy_node", 0)]
client.subscribe(topic)

client.loop_start()

# @app.template_filter('config_name_to_id')
# def config_name_to_id(config_name):
#     return config_name.lower().replace(" ", "-").replace("(", "9").replace(")", "0")

if __name__ == "__main__":
    # sensor_thread = Thread(target=read_serial_input)
    # sensor_thread.daemon = True
    # sensor_thread.start()
    app.run(host="0.0.0.0", port=8080, debug=True)
