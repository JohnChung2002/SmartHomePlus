from datetime import date
from flask import Flask, render_template, request, redirect, url_for, Response, Blueprint, g, jsonify
import mysql.connector
import os
from shared.services.auth_middleware import auth_middleware
from shared.services.validation_service import validate_timmy_settings

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
        return jsonify(g.dbconn.get_all("Stranger"))

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
            return "Success", 200
    except:
        return "Invalid input", 400

# profile page
@remote_bp.route("/profile")
def profile():
    # accessing database and table
    with g.dbconn:
        profile = g.dbconn.get_all("Profile")

    # updates webpage with template content
    return render_template('profile.html', profile=profile)

# updates profile information
@remote_bp.route("/update_profile", methods=["GET", "POST"])
def updateprofile():
    # accessing database and table
    mydb = mysql.connector.connect(user=os.getenv("CLOUD_DATABASE_USERNAME"), password=os.getenv("CLOUD_DATABASE_PASSWORD"), host=os.getenv("CLOUD_DATABASE_HOST"), database=os.getenv("CLOUD_DATABASE_NAME"))
    mycursor = mydb.cursor()
    mycursor.execute("SELECT name FROM Profile")
    profileName = mycursor.fetchone()
    profileHTML = ['updated-birthday', 'updated-height', 'updated-weight', 'updated-location']
    profileDatabase = ['birthday', 'height', 'weight', 'in_house']
#     profileHTML = ['updated-name', 'updated-birthday', 'updated-height', 'updated-weight', 'updated-location']
#     profileDatabase = ['name', 'birthday', 'height', 'weight', 'in_house']

    profileValueName = profileName[0]
    
    if request.method == "POST":
        for i in range(len(profileHTML)):
            profileValue = request.form.get(profileHTML[i])
            
            if profileValue == None:
                pass
            elif profileValue != '':
                mycursor = mydb.cursor()
                sql = "UPDATE Profile SET " + profileDatabase[i] + " = '" + profileValue + "' WHERE name = '" + profileValueName + "'"
                mycursor.execute(sql)
                mydb.commit()
                mycursor.close()
                
    # calculates and updates user BMI (if height, weight or both were changed) [if any]
    mycursor = mydb.cursor()
    mycursor.execute("SELECT height, weight FROM Profile")
    heightWeight = mycursor.fetchone()
    
    updatedHeight = heightWeight[0]
    updatedWeight = heightWeight[1]
    
    updatedBMI = updatedWeight / ((updatedHeight / 100) ** 2)
    updatedBMI = round(updatedBMI, 2)
    
    sql = "UPDATE Profile SET bmi = '" + str(updatedBMI) + "' WHERE name = '" + profileValueName + "'"
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    
    # redirects to the profile webpage
    return redirect(url_for('timmy_node.remote_door.profile'))
