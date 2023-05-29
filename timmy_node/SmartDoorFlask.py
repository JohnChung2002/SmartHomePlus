from datetime import date
from flask import Flask, render_template, request, redirect, url_for, Response, Blueprint, g, jsonify, session
import mysql.connector
import os
from shared.services.auth_middleware import auth_middleware
from shared.services.validation_service import validate_timmy_settings, validate_timmy_profile

remote_bp = Blueprint('remote_door', __name__)

topic = "/timmy_node"

# fully opens or closes the smart pet door
@remote_bp.route("/control1")
@auth_middleware
def doorcontrol1():
    g.client.publish(topic, "doorOpen")
    return "Success", 200
    
@remote_bp.route("/control2")
@auth_middleware
def doorcontrol2():
    g.client.publish(topic, "doorClose")
    return "Success", 200

@remote_bp.route("/history")
@auth_middleware
def history():
    with g.dbconn:
        return jsonify(g.dbconn.get_all("History"))
    
@remote_bp.route("/rfid")
@auth_middleware
def rfid():
    with g.dbconn:
        return jsonify(g.dbconn.get_all("RFID"))
    
@remote_bp.route("/stranger")
@auth_middleware
def stranger():
    with g.dbconn:
        return jsonify(g.dbconn.get_stranger())
    
@remote_bp.route("/profile")
@auth_middleware
def profile():
    with g.dbconn:
        return jsonify(g.dbconn.get_all_profile())

# updates different settings
@remote_bp.route("/update_settings", methods=["POST"])
@auth_middleware
@validate_timmy_settings
def updatesettings():  
    settingsHTML = ['door-height', 'in-distance-threshold', 'out-distance-threshold', 'closing-duration', 'detection-duration', 'face-detection-duration']
    settingsDatabase = ['door_height', 'distance_in_detection', 'distance_out_detection', 'time_close', 'time_detection', 'time_face_detection']
    
    settingsValue = []
    try:
        for i in range(len(settingsHTML)):
            settingsValue.append(int(request.form.get(settingsHTML[i])))
        with g.dbconn:
            data = g.dbconn.get_last_entry("Settings", "settings_id")
            settingsID = data["settings_id"]
            print(settingsID)
            settingsValue.append(settingsID)
            row_count = g.dbconn.update_with_feedback("Settings", settingsDatabase, ["settings_id"], settingsValue)
        if row_count == 0:
            return "Not Modified", 304
        else:
            g.client.publish(topic, f"settings,{settingsValue[0]},{settingsValue[1]},{settingsValue[2]},{settingsValue[3]},{settingsValue[4]},{settingsValue[5]}")
            return "Success", 200
    except:
        return "Invalid input", 400

# updates profile information
@remote_bp.route("/update_profile", methods=["GET", "POST"])
@auth_middleware
@validate_timmy_profile
def updateprofile():
    profileHTML = ["birthday", "height", "weight"]
    profileValue = []
    try:
        for i in range(len(profileHTML)):
            profileValue.append(request.form.get(profileHTML[i]))
        profileHTML.append("bmi")
        profileValue.append(round((float(profileValue[2]) / ((float(profileValue[1])/100) ** 2)), 2))
        profileValue.append(session["user_id"])
        with g.dbconn:
            row_count = g.dbconn.update_with_feedback("Profile", profileHTML, ["profile_id"], profileValue)
        if row_count == 0:
            return "Not Modified", 304
        else:
            g.client.publish(topic, f"update_profile,{session['user_id']},{profileValue[0]},{profileValue[1]},{profileValue[2]},{profileValue[3]}")
            return "Success", 200
    except:     
        return "Invalid input", 400
