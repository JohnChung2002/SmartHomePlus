import mysql.connector
import serial 
import time 
import os
from dotenv import load_dotenv
from flask import Blueprint, Flask, render_template, redirect, url_for, request, g

load_dotenv()
sprinkler_bp = Blueprint('WaterSprinkler', __name__)

# Dictionary of pins with name of pin and state ON/OFF 
pins = { 
    11: {'name' : 'PIN 11', 'state' : 0}  
} 
topic = "/cheryl_node"

# Main function when accessing the website 
@sprinkler_bp.route("/") 
def index():
    # Pass the template data into the template index.html and return it 
    return render_template('cheryl_index.html')

# Function to send simple commands 
@sprinkler_bp.route("/<action>") 
def action(action): 
    if action == 'action1' : 
#         ser.write(b"1")
        g.client.publish(topic, "Sprinkler Off")
        pins[11]['state'] = 0 
    if action == 'action2' : 
#         ser.write(b"2")
        g.client.publish(topic, "Sprinkler On")
        pins[11]['state'] = 1
    if action == 'action3' : 
#         ser.write(b"3")
        g.client.publish(topic, "Spray at Intruder")
        pins[11]['state'] = 2
#     if action == 'action4' : 
#         ser.write(b"4") 
#         pins[12]['state'] = 0
#     if action == 'action5' : 
#         ser.write(b"5") 
#         pins[12]['state'] = 1
        
    return redirect(url_for('cheryl_node.WaterSprinkler.index'))

#  This is to change the threshold value of the brightness
@sprinkler_bp.route('/submit-form', methods=['POST'])
def submit_form():
    wetnessVal = int(request.form['wetness'])
    with g.dbconn:
        g.dbconn.update("system_data", ["status"], ["field"], [wetnessVal, "wetness_value"])
    g.client.publish(topic, f"Update Wetness Threshold,{wetnessVal}")
#     return 'Form submitted successfully'
    return redirect(url_for('cheryl_node.WaterSprinkler.index'))

@sprinkler_bp.route('/get-environment-data')
def get_environment_data():
    with g.dbconn:
        result = g.dbconn.get_env_data()
    print(result)
    return result
