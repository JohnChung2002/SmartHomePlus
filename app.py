from flask import Flask, g, request
from flask_cors import CORS
from discord_webhook import DiscordWebhook, DiscordEmbed
import paho.mqtt.client as mqtt
from threading import Thread, Timer
from shared.services.mysql_service import MySQLService
from dotenv import load_dotenv
import os, ast, requests, datetime, airporttime, pytz

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
    message_mqtt = msg.payload.decode()
    if (msg.topic not in ["/cheryl_node", "/john_node", "/timmy_node"]):
        print("Received unknown topic message: ", message_mqtt)
    if msg.topic == "/john_node":
        json_message = ast.literal_eval(message_mqtt)
        if (json_message["sender"] == "Edge"):
            if (json_message["title"] == "Lights"):
                with mqtt_dbconn:
                    mqtt_dbconn.update("appliance_status", ["status"], ["appliance_id"], [int(json_message["status"]), lights_dict[json_message["room"]]])
            if (json_message["title"] == "Aircon Switch"):
                with mqtt_dbconn:
                    mqtt_dbconn.update("appliance_status", ["status"], ["appliance_id"], [int(json_message["status"]), aircon_dict[json_message["room"]]])
            if (json_message["title"] == "Ventilating Fan"):
                with mqtt_dbconn:
                    mqtt_dbconn.update("appliance_status", ["status"], ["appliance_id"], [int(json_message["status"]), 6])
            if (json_message["title"] == "Update Uptime"):
                with mqtt_dbconn:
                    data = mqtt_dbconn.get_by_id("appliance_uptime", ["appliance_id"], [json_message["appliance_id"]])
                    if data is None:
                        today = datetime.date.today()
                        mqtt_dbconn.insert("appliance_uptime", ["appliance_id", "uptime", "date"], [json_message["appliance_id"], int(json_message["uptime"]), datetime.date(today.year, today.month, 1).strftime("%Y-%m-%d")])
                    else:
                        mqtt_dbconn.update("appliance_uptime", ["uptime"], ["appliance_id"], [int(json_message["uptime"]), json_message["appliance_id"]])
            print("Received John's MQTT message: ", msg.payload.decode())         
    if msg.topic == "/cheryl_node":
        if ("," in message_mqtt and "Update Wetness Threshold" not in message_mqtt):
            wetness, light_intensity, temperature = message_mqtt.split(",")
            with mqtt_dbconn:
                mqtt_dbconn.insert("environment_data", ["temperature", "wetness", "brightness"], [temperature, wetness, light_intensity])
    if msg.topic == "/timmy_node":
        timmyNodeMessage = message_mqtt.split(",")
        if timmyNodeMessage[0] == "history":
            profileID = timmyNodeMessage[1]
            currentTime = timmyNodeMessage[2]
            currentDate = timmyNodeMessage[3]
            userHeight = timmyNodeMessage[4]
            potentiometerWeight = timmyNodeMessage[5]
            bmi = timmyNodeMessage[6]
            inHouse = timmyNodeMessage[7]
            
            with mqtt_dbconn:
                mqtt_dbconn.insert("history", ["profile_id", "time", "date", "height", "weight", "bmi", "in_house"], [profileID, currentTime, currentDate, userHeight, potentiometerWeight, bmi, inHouse])
        if timmyNodeMessage[0] == "profile":
            profileID = timmyNodeMessage[1]
            userHeight = timmyNodeMessage[2]
            potentiometerWeight = timmyNodeMessage[3]
            bmi = timmyNodeMessage[4]
            inHouse = timmyNodeMessage[5]
            
            with mqtt_dbconn:
                mqtt_dbconn.update("profile", ["height"], ["profile_id"], [userHeight, profileID])
                mqtt_dbconn.update("profile", ["weight"], ["profile_id"], [potentiometerWeight, profileID])
                mqtt_dbconn.update("profile", ["bmi"], ["profile_id"], [bmi, profileID])
                mqtt_dbconn.update("profile", ["in_house"], ["profile_id"], [inHouse, profileID])
        if timmyNodeMessage[0] == "stranger":
            currentTime = timmyNodeMessage[1]
            currentDate = timmyNodeMessage[2]
            strangerMessage = timmyNodeMessage[3]
            
            with mqtt_dbconn:
                mqtt_dbconn.insert("stranger", ["time", "date", "status"], [currentTime, currentDate, strangerMessage])
        print("Received Timmy's MQTT message: ", message_mqtt)

# @app.template_filter('config_name_to_id')
# def config_name_to_id(config_name):
#     return config_name.lower().replace(" ", "-").replace("(", "9").replace(")", "0")

def query_weather(city):

    base_url = 'http://api.weatherapi.com/v1/forecast.json'
    apt = airporttime.AirportTime(iata_code=city)

    converted_datetime = apt.from_utc(datetime.datetime.utcnow())
    offset = converted_datetime.strftime("%z")
    timezone = pytz.FixedOffset(int(offset[1:3]) * 60 + int(offset[3:5]))
    given_datetime = converted_datetime.replace(tzinfo=pytz.UTC).astimezone(timezone)
    desired_time = given_datetime.strftime("%H")
    
    params = {
        'key': os.getenv("WEATHER_API_KEY"),
        'q': f"iata:{city}",
        'hour': desired_time,
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        # Extract the desired weather information from the response
        will_it_rain = int(data['forecast']['forecastday'][0]['hour'][0]['will_it_rain'])
        chance_of_rain = int(data['forecast']['forecastday'][0]['hour'][0]['chance_of_rain'])
        return [will_it_rain, chance_of_rain]
    except requests.exceptions.RequestException as e:
        print('Error occurred during the API request:', e)
        return None

def every_minute_function():
    #do something every minute
    print("every_minute_function")
    pass

def every_hour_ten_offset_function():
    #do something every hour (10 minutes before the next hour)
    will_it_rain, chance_of_rain = query_weather("KCH")
    message = f"It seems like it will be raining in the next hour. Chance of rain: {chance_of_rain}%" if will_it_rain else f"It seems like it will not be raining in the next hour. Chance of rain: {chance_of_rain}%"
    webhook = DiscordWebhook(
        url=os.getenv("SPRINKLER_DISCORD_WEBHOOK"), 
        username="Weather Notification Bot"
    )
    embed = DiscordEmbed(
        title="Weather Webhook", 
        description=message, 
        color="03b2f8",
        url = "https://dashboard.digitalserver.tech/"
    )
    webhook.add_embed(embed)
    webhook.execute()

def every_hour_function():
    #do something every hour
    print("Hourly function")
    pass

def every_minute_cron_thread():
    global minute_timer
    # Run the function every minute
    if minute_timer is not None:
        minute_timer.cancel()
    minute_timer = Timer(60, every_minute_cron_thread).start()
    every_minute_function()

def every_hour_ten_offset_cron_thread():
    global hour_ten_offset_timer
    # Run the function every hour
    current_time = datetime.datetime.now()
    # Calculate the time until the next hour
    time_until_next_hour = (((60 - current_time.minute) * 60) - current_time.second) - 600  # 10 minutes before the next hour
    if (time_until_next_hour <= 0):
        time_until_next_hour = 3600
    print(time_until_next_hour)
    if hour_ten_offset_timer is not None:
        hour_ten_offset_timer.cancel()
    hour_ten_offset_timer = Timer(time_until_next_hour, every_hour_ten_offset_cron_thread).start()
    every_hour_ten_offset_function()

def every_hour_cron_thread():
    global hour_timer
    # Run the function every hour
    current_time = datetime.datetime.now()
    # Calculate the time until the next hour
    time_until_next_hour = ((60 - current_time.minute) * 60) - current_time.second
    if hour_timer is not None:
        hour_timer.cancel()
    hour_timer = Timer(time_until_next_hour, every_hour_cron_thread).start()
    every_hour_function()

minute_timer = None
hour_ten_offset_timer = None
hour_timer = None

if __name__ == "__main__":
    client = mqtt.Client()
    mqtt_dbconn = MySQLService(os.getenv("CLOUD_DATABASE_HOST"), os.getenv("CLOUD_DATABASE_USERNAME"), os.getenv("CLOUD_DATABASE_PASSWORD"), os.getenv("CLOUD_DATABASE_NAME"))
    client.username_pw_set(username=os.getenv("CLOUD_MQTT_USERNAME"), password=os.getenv("CLOUD_MQTT_PASSWORD")) # type: ignore
    client.on_connect = on_connect 
    client.on_publish = on_publish
    client.on_message = on_message
    client.connect(os.getenv("CLOUD_MQTT_HOST"), int(os.getenv("CLOUD_MQTT_PORT")), 60) # type: ignore
    topic = [("/john_node", 0), ("/cheryl_node", 0), ("/timmy_node", 0)]
    client.subscribe(topic)
    client.loop_start()
    # sensor_thread = Thread(target=read_serial_input)
    # sensor_thread.daemon = True
    # sensor_thread.start()
    every_minute_cron_thread()
    every_hour_cron_thread()
    every_hour_ten_offset_cron_thread()
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)
