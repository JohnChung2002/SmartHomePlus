from datetime import date
from flask import Flask, render_template, request, redirect, url_for, Response, Blueprint, g, jsonify
import mysql.connector
import os
from dotenv import load_dotenv
from shared.services.auth_middleware import auth_middleware

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
@remote_bp.route("/update_settings", methods=["GET", "POST"])
def updatesettings():
    # accessing database and table
#     with g.dbconn:
#         data = g.dbconn.get_last_entry("Settings", "settings_id")
#         settingsID = data["settings_id"]
    
    settingsHTML = ['door-height', 'in-distance-threshold', 'out-distance-threshold', 'closing-duration', 'detection-duration', 'face-detection-duration']
    settingsDatabase = ['door_height', 'distance_in_detection', 'distance_out_detection', 'time_close', 'time_detection', 'time_face_detection']
    
    if request.method == "POST":
        for i in range(len(settingsHTML)):
            settingsValue = request.form.get(settingsHTML[i])
            
            if settingsValue != None:
                with g.dbconn:
                    data = g.dbconn.get_last_entry("Settings", "settings_id")
                    settingsID = data["settings_id"]
                    print(settingsID)
                    mqtt_dbconn.update("Settings", [settingsDatabase[i]], ["settings_id"], [settingsValue, settingsID])
#                 mydb = mysql.connector.connect(user=os.getenv("CLOUD_DATABASE_USERNAME"), password=os.getenv("CLOUD_DATABASE_PASSWORD"), host=os.getenv("CLOUD_DATABASE_HOST"), database=os.getenv("CLOUD_DATABASE_NAME"))
#                 mycursor = mydb.cursor()
#                 sql = "UPDATE Settings SET " + settingsDatabase[i] + " = '" + settingsValue + "' WHERE settings_id = '" + str(settingsID) + "'"
#                 mycursor.execute(sql)
#                 mydb.commit()
#                 mycursor.close()

    # redirects to the homepage
    return redirect(url_for('timmy_node.remote_door.smartdoor'))

# profile page
@remote_bp.route("/profile")
def profile():
    # accessing database and table
    mydb = mysql.connector.connect(user=os.getenv("CLOUD_DATABASE_USERNAME"), password=os.getenv("CLOUD_DATABASE_PASSWORD"), host=os.getenv("CLOUD_DATABASE_HOST"), database=os.getenv("CLOUD_DATABASE_NAME"))
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Profile")
    profile = mycursor.fetchall()
    mycursor.close()
    
    templateData = {
                    'profile' : profile
                    }

    # updates webpage with template content
    return render_template('profile.html', **templateData)

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
