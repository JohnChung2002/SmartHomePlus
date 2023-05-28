from flask import Blueprint, Flask, render_template, redirect, url_for, request, g
from shared.services.auth_middleware import auth_middleware
from shared.services.validation_service import validate_iata_region
import datetime

sprinkler_bp = Blueprint('WaterSprinkler', __name__)

topic = "/cheryl_node"

# Function to send simple commands 
@sprinkler_bp.route("/action1")
@auth_middleware
def action1(): 
    g.client.publish(topic, "Sprinkler Off")
    return "Success", 200

@sprinkler_bp.route("/action2")
@auth_middleware
def action2():
    g.client.publish(topic, "Sprinkler On")
    return "Success", 200

@sprinkler_bp.route("/action3")
@auth_middleware
def action3():
    g.client.publish(topic, "Spray at Intruder")
    return "Success", 200

#  This is to change the threshold value of the brightness
@sprinkler_bp.route('/submit-form', methods=['POST'])
@auth_middleware
def submit_form():
    try:
        wetnessVal = int(request.form['wetness'])
        with g.dbconn:
            g.dbconn.update("system_data", ["status"], ["field"], [wetnessVal, "wetness_value"])
        g.client.publish(topic, f"Update Wetness Threshold,{wetnessVal}")
        return "Success", 200
    except:
        return "Invalid wetness value", 400

@sprinkler_bp.route('/config', methods=['POST'])
@auth_middleware
@validate_iata_region
def update_config():
    try:
        iata_region = request.form['iata_region']
        with g.dbconn:
            row_count = g.dbconn.update_with_feedback("config", ["value"], ["field"], [iata_region, "iata_region"])
        if row_count == 0:
            return "Not modified", 304
        else:
            return "Success", 200
    except:
        return "Invalid iata region", 400

@sprinkler_bp.route('/get-environment-data', methods=['POST'])
@auth_middleware
def get_environment_data():
    #check if there is date data, if there is, get the data from the date
    #if there is no date data, get the latest data
    date = request.form['date'] if ('date' in request.form and request.form['date']  != "") else datetime.datetime.now().strftime("%Y-%m-%d")
    if date is not None and date != "":
        with g.dbconn:
            result = g.dbconn.get_env_data(date)
    return result
