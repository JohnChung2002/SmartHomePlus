import serial
from datetime import date
import time
from flask import Flask, render_template, request, redirect, url_for, Response
import mysql.connector
from SmartDoorML import frames, picturecounter

app = Flask(__name__)

# pin dictionary
pins = {
        5: {'name' : 'PIN5', 'state' : 0}
        }

counter = 0
captureNow = False

# homepage (dashboard)
@app.route("/")
def index():
    # accessing database and table
    mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Door")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Profile")
    profile = mycursor.fetchall()
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
                    'profile' : profile,
                    'history' : history,
                    'rfid' : rfid,
                    'settings' : settings,
                    'stranger' : stranger,
                    'counter': counter
                    }

    # updates homepage with template content
    return render_template('index.html', **templateData)

@app.route("/feed")
def feed():
    global captureNow
    latestFrames = frames(captureNow)
    
    if captureNow == True:
        captureNow = False
        
    return Response(latestFrames, mimetype='multipart/x-mixed-replace; boundary=frame')
        
@app.route("/capture")
def capture():
    global counter
    counter = picturecounter()
    
    global captureNow
    captureNow = True
    
    # redirects to the homepage
    return redirect(url_for('index'))
        
# creates a new profile
@app.route("/create_profile", methods=["GET", "POST"])
def createprofile():
    # accessing database and table
    mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Door")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Profile")
    profile = mycursor.fetchall()
    mycursor.execute("SELECT * FROM RFID")
    rfid = mycursor.fetchall()
    mycursor.close()
    
    # obtains available rfid
    availableRFID = []
    numberRFID = len(rfid)
    
    if numberRFID > 0:
        for i in rfid:
            availableRFID.append(i[0])
    
    profileHTML = ['name', 'birthday', 'height', 'weight', 'location']
    profileDatabase = ['name', 'birthday', 'height', 'weight', 'in_house']
    profileCreate = []
    profileCreateValue = []
    
    if request.method == "POST":
        for i in range(len(profileHTML)):
            profileValue = request.form.get(profileHTML[i])
            
            if profileValue == None:
                pass
            elif profileValue != '':
                profileCreate.append(profileDatabase[i])
                profileCreateValue.append(profileValue)
        
        if ("height" in profileCreate) and ("weight" in profileCreate):
            profileCreate.append('bmi')
            
            for i in range(len(profileCreate)):
                if i == "height":
                    profileHeight = profileCreateValue[i]
            
            for i in range(len(profileCreate)):
                if i == "weight":
                    profileWeight = profileCreateValue[i]
                    
            profileBMI = profileWeight / ((profileHeight / 100) ** 2)
            
            profileCreateValue.append(profileBMI)
                
        profileCreate.append('rfid_number')
               
        if len(profile) == 0:
            profileCreateValue.append(availableRFID[0])
        else:
            for i in profile:
                for j in availableRFID:
                    if i[1] != j:
                        profileCreateValue.append(j)
                
        mycursor = mydb.cursor()
        
        sql = "INSERT INTO Profile ("
        for i in range(len(profileCreate) - 1):
            sql += (profileCreate[i] + ", ")
        sql += (profileCreate[-1] + ") VALUES (")
        for i in range(len(profileCreateValue) - 1):
            sql += ("'" + profileCreateValue[i] + "', ")
        sql += ("'" + str(profileCreateValue[-1]) + "')")
        
        mycursor.execute(sql)
        mydb.commit()
        mycursor.close()

    # redirects to the homepage
    return redirect(url_for('index'))

# # grants or denies the permission for each pet to use the smart pet door
# @app.route("/setpermission/<namepermission>/<permission>")
# def setpermission(namepermission, permission):
#     # accessing database and table
#     mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Pet Door")
#     mycursor = mydb.cursor()
#     
#     # grants or denies a specific pet's permission
#     if permission == "grant":
#         sql = "UPDATE Profile SET permission = '1' WHERE name = '" + namepermission + "'"
#     else:
#         sql = "UPDATE Profile SET permission = '0' WHERE name = '" + namepermission + "'"
#             
#     mycursor.execute(sql)
#     mydb.commit()
#     mycursor.close()
#     
#     # redirects to the homepage
#     return redirect(url_for('index'))
# 
# # fully opens or closes the smart pet door
# @app.route("/<control>")
# def doorcontrol(control):
#     if control == 'control1' :
#         ser.write(b"6")
#         pins[5]['state'] = 1
#     if control == 'control2' :
#         ser.write(b"7")
#         pins[5]['state'] = 0
#         
#     # redirects to the homepage
#     return redirect(url_for('index'))
# 
# # profile page
# @app.route("/profile")
# def profile():
#     # accessing database and table
#     mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Pet Door")
#     mycursor = mydb.cursor()
#     mycursor.execute("SELECT * FROM Profile")
#     profile = mycursor.fetchall()
#     mycursor.execute("SELECT profile_id, weight FROM History")
#     historyweight = mycursor.fetchall()
#     mycursor.execute("SELECT * FROM RFID")
#     rfid = mycursor.fetchall()
#     mycursor.close()
#     
#     # displays parts of the page if true
#     displayCreateProfile = False
#     displayUpdateProfile = False
#     displayDeleteProfile = False
#         
#     numberProfile = len(profile)
#     
#     # displays when it has not reached maximum number of RFIDs used
#     if (numberProfile < len(rfid)):
#         displayCreateProfile = True
#         
#     # displays when there is at least one profile
#     if (numberProfile > 0):
#         displayUpdateProfile = True
#         displayDeleteProfile = True
#     
#     averageweight = []
#     highweight = []
#     lowweight = []
#     
#     # average weight calculation
#     for i in profile:
#         averageloopprofile = []
#         loopnumber = 0
#         averagestart = 0
#         
#         for j in historyweight:
#             if i[0] == j[0]:
#                 loopnumber += 1
#                 averagestart += j[1]
#         
#         averageloopprofile.append(i[0])
#         
#         if loopnumber == 0:
#             averageloopprofile.append("-")
#         else:  
#             averageend = averagestart / loopnumber
#             averageloopprofile.append("{:.2f}".format(averageend))  # two decimal places
#         
#         averageweight.append(averageloopprofile)
#     
#     # highest weight calculation
#     for i in profile:
#         highloopprofile = []
#         highprofile = []
#         highstart = 0
#         
#         for j in historyweight:
#             if i[0] == j[0]:
#                 highprofile.append(j[1])
#                 
#         highloopprofile.append(i[0])
#         
#         if len(highprofile) == 0:
#             highloopprofile.append("-")
#         else:  
#             highstart = max(highprofile)
#             highloopprofile.append(highstart)
#         
#         highweight.append(highloopprofile)
#     
#     # lowest weight calculation
#     for i in profile:
#         lowloopprofile = []
#         lowprofile = []
#         lowstart = 0
#         
#         for j in historyweight:
#             if i[0] == j[0]:
#                 lowprofile.append(j[1])
#                 
#         lowloopprofile.append(i[0])
#         
#         if len(lowprofile) == 0:
#             lowloopprofile.append("-")
#         else: 
#             lowstart = min(lowprofile)
#             lowloopprofile.append(lowstart)
#         
#         lowweight.append(lowloopprofile)
#     
#     # obtains rfid numbers
#     rfidlist = []
#     
#     for i in rfid:
#         rfidnumber = []
#         
#         rfidnumber.append(i[0])
#         rfidnumber.append(i[1])
#         rfidlist.append(rfidnumber)
#     
#     templateData = {
#                     'profile' : profile,
#                     'displayCreateProfile' : displayCreateProfile,
#                     'displayUpdateProfile' : displayUpdateProfile,
#                     'displayDeleteProfile' : displayDeleteProfile,
#                     'averageweight' : averageweight,
#                     'highweight' : highweight,
#                     'lowweight' : lowweight,
#                     'rfidlist' : rfidlist
#                     }
# 
#     # updates webpage with template content
#     return render_template('profile.html', **templateData)
# 
# # creates a new profile
# @app.route("/create_profile", methods=["GET", "POST"])
# def createprofile():
#     # accessing database and table
#     mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Pet Door")
#     mycursor = mydb.cursor()
#     mycursor.execute("SELECT * FROM Profile")
#     profile = mycursor.fetchall()
#     mycursor.execute("SELECT * FROM RFID")
#     rfid = mycursor.fetchall()
#     mycursor.close()
#     
#     # obtains available rfid
#     availableRFID = []
#     numberRFID = len(rfid)
#     
#     if numberRFID > 0:
#         for i in rfid:
#             availableRFID.append(i[0])
#     
#     profileHTML = ['name', 'type', 'birthday', 'height', 'maximum-weight', 'minimum-weight', 'weight', 'location', 'permission']
#     profileDatabase = ['name', 'type', 'birthday', 'height', 'maximum_weight', 'minimum_weight', 'weight', 'in_house', 'permission']
#     profileCreate = []
#     profileCreateValue = []
#     
#     if request.method == "POST":
#         for i in range(len(profileHTML)):
#             profileValue = request.form.get(profileHTML[i])
#             
#             if profileValue == None:
#                 pass
#             elif profileValue != '':
#                 profileCreate.append(profileDatabase[i])
#                 profileCreateValue.append(profileValue)
#                 
#         profileCreate.append('rfid_number')
#                
#         if len(profile) == 0:
#             profileCreateValue.append(availableRFID[0])
#         else:
#             for i in profile:
#                 for j in availableRFID:
#                     if i[10] != j:
#                         profileCreateValue.append(j)
#                 
#         mycursor = mydb.cursor()
#         
#         sql = "INSERT INTO Profile ("
#         for i in range(len(profileCreate) - 1):
#             sql += (profileCreate[i] + ", ")
#         sql += (profileCreate[-1] + ") VALUES (")
#         for i in range(len(profileCreateValue) - 1):
#             sql += ("'" + profileCreateValue[i] + "', ")
#         sql += ("'" + str(profileCreateValue[-1]) + "')")
#         
#         mycursor.execute(sql)
#         mydb.commit()
#         mycursor.close()
# 
#     # redirects to the profile webpage
#     return redirect(url_for('profile'))
# 
# # updates profile information
# @app.route("/update_profile", methods=["GET", "POST"])
# def updateprofile():
#     # accessing database and table
#     mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Pet Door")
#     profileHTML = ['updated-name', 'updated-type', 'updated-birthday', 'updated-height', 'updated-maximum-weight', 'updated-minimum-weight', 'updated-weight', 'updated-location']
#     profileDatabase = ['name', 'type', 'birthday', 'height', 'maximum_weight', 'minimum_weight', 'weight', 'in_house']
#     
#     if request.method == "POST":
#         profileValueName = request.form.get('update-name')
#         
#         for i in range(len(profileHTML)):
#             profileValue = request.form.get(profileHTML[i])
#             
#             if profileValue == None:
#                 pass
#             elif profileValue != '':
#                 mycursor = mydb.cursor()
#                 sql = "UPDATE Profile SET " + profileDatabase[i] + " = '" + profileValue + "' WHERE name = '" + profileValueName + "'"
#                 mycursor.execute(sql)
#                 mydb.commit()
#                 mycursor.close()
#     
#     # redirects to the profile webpage
#     return redirect(url_for('profile'))
# 
# # deletes profile
# @app.route("/delete_profile", methods=["GET", "POST"])
# def deleteprofile():
#     if request.method == "POST":
#         profileValueName = request.form.get('delete-profile')
#         
#         # accessing database and table
#         mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Pet Door")
#         mycursor = mydb.cursor()
#         sql = "DELETE FROM Profile WHERE name = '" + profileValueName + "'"
#         mycursor.execute(sql)
#         mydb.commit()
#         mycursor.close()
#     
#     # redirects to the profile webpage
#     return redirect(url_for('profile'))
# 
# # history page
# @app.route("/history")
# def history():
#     # accessing database and table
#     mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Pet Door")
#     mycursor = mydb.cursor()
#     mycursor.execute("SELECT * FROM History ORDER BY history_id DESC LIMIT 10")
#     history = mycursor.fetchall()
#     mycursor.execute("SELECT profile_id, name FROM Profile")
#     profile = mycursor.fetchall()
#     mycursor.execute("SELECT * FROM Stray ORDER BY stray_id DESC LIMIT 10")
#     stray = mycursor.fetchall()
#     mycursor.close()
#     
#     templateData = {
#                     'history' : history,
#                     'profile' : profile,
#                     'stray' : stray
#                     }
# 
#     # updates webpage with template content
#     return render_template('history.html', **templateData)
# 
# # settings page
# @app.route("/settings")
# def settings():
#     # accessing database and table
#     mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Pet Door")
#     mycursor = mydb.cursor()
#     mycursor.execute("SELECT * FROM Settings")
#     settings = mycursor.fetchall()
#     mycursor.close()
#     
#     templateData = {
#                     'settings' : settings
#                     }
# 
#     # updates webpage with template content
#     return render_template('settings.html', **templateData)
# 
# # updates different settings
# @app.route("/update_settings", methods=["GET", "POST"])
# def updatesettings():
#     # accessing database and table
#     mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Pet Door")
#     settingsHTML = ['height-space', 'distance-detection', 'time-close', 'time-detection']
#     settingsDatabase = ['height_space', 'distance_detection', 'time_close', 'time_detection']
#     
#     if request.method == "POST":
#         for i in range(len(settingsHTML)):
#             settingsValue = request.form.get(settingsHTML[i])
#             
#             if settingsValue != None:
#                 mycursor = mydb.cursor()
#                 sql = "UPDATE Settings SET " + settingsDatabase[i] + " = '" + settingsValue + "' WHERE settings_id = '1'"
#                 mycursor.execute(sql)
#                 mydb.commit()
#                 mycursor.close()
# 
#     # redirects to the settings webpage
#     return redirect(url_for('settings'))

# starts the Flask micro-web-framework server and establishes the Serial Messaging connection to Arduino (microcontroller)
if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser.flush()
    app.run(host='0.0.0.0',port=8080,debug=False)