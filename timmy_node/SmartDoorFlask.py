import serial
from datetime import date
import time
from flask import Flask, render_template, request, redirect, url_for, Response, Blueprint
import mysql.connector

remote_bp = Blueprint('remote_door', __name__)

# pin dictionary
pins = {
        5: {'name' : 'PIN5', 'state' : 0}
        }

# homepage (dashboard)
@remote_bp.route("/")
def index():
    # accessing database and table
    mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Door")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM History")
    history = mycursor.fetchall()
    mycursor.execute("SELECT * FROM RFID")
    rfid = mycursor.fetchall()
    mycursor.execute("SELECT * FROM Settings")
    settings = mycursor.fetchall()
    mycursor.execute("SELECT * FROM Stranger")
    stranger = mycursor.fetchall()
    mycursor.close()
        
    templateData = {
                    'history' : history,
                    'rfid' : rfid,
                    'settings' : settings,
                    'stranger' : stranger
                    }

    # updates homepage with template content
    return render_template('index.html', **templateData)

# fully opens or closes the smart pet door
@remote_bp.route("/<control>")
def doorcontrol(control):
    if control == 'control1' :
        client.publish(topic, "doorOpen")
        pins[5]['state'] = 1
    if control == 'control2' :
        client.publish(topic, "doorClose")
        pins[5]['state'] = 0
        
    # redirects to the homepage
    return redirect(url_for('index'))

# updates different settings
@remote_bp.route("/update_settings", methods=["GET", "POST"])
def updatesettings():
    # accessing database and table
    mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Door")
    settingsHTML = ['door-height', 'in-distance-threshold', 'out-distance-threshold', 'closing-duration', 'detection-duration', 'face-detection-duration']
    settingsDatabase = ['door_height', 'distance_in_detection', 'distance_out_detection', 'time_close', 'time_detection', 'time_face_detection']
    
    if request.method == "POST":
        for i in range(len(settingsHTML)):
            settingsValue = request.form.get(settingsHTML[i])
            
            if settingsValue != None:
                mycursor = mydb.cursor()
                sql = "UPDATE Settings SET " + settingsDatabase[i] + " = '" + settingsValue + "' WHERE settings_id = '1'"
                mycursor.execute(sql)
                mydb.commit()
                mycursor.close()

    # redirects to the homepage
    return redirect(url_for('index'))

# profile page
@remote_bp.route("/profile")
def profile():
    # accessing database and table
    mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Door")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Profile")
    profile = mycursor.fetchall()
    
    templateData = {
                    'profile' : profile
                    }

    # updates webpage with template content
    return render_template('profile.html', **templateData)

# updates profile information
@remote_bp.route("/update_profile", methods=["GET", "POST"])
def updateprofile():
    # accessing database and table
    mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Door")
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
    return redirect(url_for('profile'))