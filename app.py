from flask import Flask, g, request
from flask_cors import CORS
from discord_webhook import DiscordWebhook, DiscordEmbed
import paho.mqtt.client as mqtt
from threading import Thread, Timer
from shared.services.mysql_service import MySQLService
from dotenv import load_dotenv
import os, ast, requests, datetime

from cheryl_node import bp_cheryl
from john_node import bp_john
from timmy_node import bp_timmy
from main import bp_main

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

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.secret_key =  os.getenv("APP_SECRET_KEY")

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
    print("Received message: ", msg.payload.decode())
    if msg.topic == "/john_node":
        if (json_message["sender"] == "Edge"):
            print("Received message: ", msg.payload.decode())         
    if msg.topic == "/cheryl_node":
        if (json_message["sender"] == "Edge"):
            print("Received message: ", msg.payload.decode())
    if msg.topic == "/timmy_node":
        if (json_message["sender"] == "Edge"):
            print("Received message: ", msg.payload.decode())

# @app.template_filter('config_name_to_id')
# def config_name_to_id(config_name):
#     return config_name.lower().replace(" ", "-").replace("(", "9").replace(")", "0")

def query_weather(city):
    base_url = 'http://api.weatherapi.com/v1/forecast.json'
    params = {
        'key': os.getenv("WEATHER_API_KEY"),
        'q': f"iata:{city}",
        'hour': (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H"),
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        # Extract the desired weather information from the response
        will_it_rain = data['forecast']['forecastday'][0]['hour'][0]['will_it_rain']
        return (int(will_it_rain) == 1)
    except requests.exceptions.RequestException as e:
        print('Error occurred during the API request:', e)
        return None

def every_minute_function():
    #do something every minute
    pass

def every_hour_function():
    #do something every hour (10 minutes before the next hour)
    pass

def every_minute_cron_thread():
    # Run the function every minute
    Timer(60, every_minute_cron_thread).start()
    every_minute_function()

def every_hour_cron_thread():
    # Run the function every hour
    Timer(3600, every_hour_cron_thread).start()
    every_hour_function()

if __name__ == "__main__":
    client = mqtt.Client()
    mqtt_dbconn = MySQLService(os.getenv("CLOUD_DATABASE_HOST"), os.getenv("CLOUD_DATABASE_USERNAME"), os.getenv("CLOUD_DATABASE_PASSWORD"), os.getenv("CLOUD_DATABASE_NAME"))
    client.username_pw_set(username=os.getenv("LOCAL_MQTT_USERNAME"), password=os.getenv("LOCAL_MQTT_PASSWORD")) # type: ignore
    client.on_connect = on_connect 
    client.on_publish = on_publish
    client.connect(os.getenv("CLOUD_MQTT_HOST"), int(os.getenv("CLOUD_MQTT_PORT")), 60) # type: ignore
    topic = [("/john_node", 0), ("/cheryl_node", 0), ("/timmy_node", 0)]
    client.subscribe(topic)
    client.loop_start()
    # sensor_thread = Thread(target=read_serial_input)
    # sensor_thread.daemon = True
    # sensor_thread.start()
    every_minute_cron_thread()
    every_hour_cron_thread()
    app.run(host="0.0.0.0", port=8080, debug=True)
