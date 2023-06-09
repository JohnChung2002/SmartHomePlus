# imports libraries
import time
from datetime import date, datetime
import serial
import mysql.connector
from SmartDoorDetection import detection
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

# initialization of variables
directionIn = False
directionOut = False
inHouse = "2"
personDetected = False
strangerWrite = True
showRed = True
faceDetected = False

# loads environment variables
load_dotenv()

# microcontroller (Arduino Uno)
device = '/dev/ttyUSB0'
arduino = serial.Serial(device, 9600)

# acts as a timer to keep track of how long someone has been by the door
def Countdown():
    timeElapsed = datetime.now() - timeDetectionStart
    timeElapsedMs = (timeElapsed.days * 24 * 60 * 60 + timeElapsed.seconds) * 1000 + timeElapsed.microseconds / 1000.0
    
    return int(timeElapsedMs)

# connects to MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected with RC: {str(rc)}")
    
    pass

# sends messages through MQTT
def on_publish(client, data, result):
    print("Message sent to MQTT broker")
    
    pass

# receives messages through MQTT
def on_message(client, userdata, msg):
    messageReceived = msg.payload.decode()
    
    if messageReceived == "doorOpen":
        arduino.write(b"6")
        time.sleep(1)
    elif messageReceived == "doorClose":
        arduino.write(b"7")
        time.sleep(1)
    else:
        mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Door")
        mycursor = mydb.cursor()
    
        tableValues = messageReceived.split(",")
        
        if tableValues[0] == "update_profile":
            updateUser = tableValues[1]
            updatedBirthday = tableValues[2]
            updatedHeight = tableValues[3]
            updatedWeight = tableValues[4]
            updatedBMI = tableValues[5]
            
            sql = "UPDATE Profile SET birthday = '" + updatedBirthday + "' WHERE profile_id = '" + updateUser + "'"
            mycursor.execute(sql)
            mydb.commit()
            
            sql = "UPDATE Profile SET height = '" + updatedHeight + "' WHERE profile_id = '" + updateUser + "'"
            mycursor.execute(sql)
            mydb.commit()
            
            sql = "UPDATE Profile SET weight = '" + updatedWeight + "' WHERE profile_id = '" + updateUser + "'"
            mycursor.execute(sql)
            mydb.commit()
            
            sql = "UPDATE Profile SET bmi = '" + updatedBMI + "' WHERE profile_id = '" + updateUser + "'"
            mycursor.execute(sql)
            mydb.commit()
        elif tableValues[0] == "settings":
            mycursor.execute("SELECT settings_id FROM Settings")
            settings = mycursor.fetchone()
            settingsID = settings[0]
            settingsID = str(settingsID)
            
            updatedDoorHeight = tableValues[1]
            updatedDistanceInDetection = tableValues[2]
            updatedDistanceOutDetection = tableValues[3]
            updatedTimeClose = tableValues[4]
            updatedTimeDetection = tableValues[5]
            updatedTimeFaceDetection = tableValues[6]
            
            sql = "UPDATE Settings SET door_height = '" + updatedDoorHeight + "' WHERE settings_id = '" + settingsID + "'"
            mycursor.execute(sql)
            mydb.commit()
            
            sql = "UPDATE Settings SET distance_in_detection = '" + updatedDistanceInDetection + "' WHERE settings_id = '" + settingsID + "'"
            mycursor.execute(sql)
            mydb.commit()
            
            sql = "UPDATE Settings SET distance_out_detection = '" + updatedDistanceOutDetection + "' WHERE settings_id = '" + settingsID + "'"
            mycursor.execute(sql)
            mydb.commit()
            
            sql = "UPDATE Settings SET time_close = '" + updatedTimeClose + "' WHERE settings_id = '" + settingsID + "'"
            mycursor.execute(sql)
            mydb.commit()
            
            sql = "UPDATE Settings SET time_detection = '" + updatedTimeDetection + "' WHERE settings_id = '" + settingsID + "'"
            mycursor.execute(sql)
            mydb.commit()
            
            sql = "UPDATE Settings SET time_face_detection = '" + updatedTimeFaceDetection + "' WHERE settings_id = '" + settingsID + "'"
            mycursor.execute(sql)
            mydb.commit()

    pass

# initializes MQTT client
client = mqtt.Client()
client.username_pw_set(username=os.getenv("LOCAL_MQTT_USERNAME"), password=os.getenv("LOCAL_MQTT_PASSWORD"))
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message
client.connect(os.getenv("LOCAL_MQTT_HOST"), int(os.getenv("LOCAL_MQTT_PORT")), 60)

# subscribes to MQTT topic
topic = "/timmy_node"
client.subscribe(topic)

# starts MQTT loop
client.loop_start()

# infinite loop
while True:
    # obtains the current date and time
    timeNow = datetime.now()
    currentTime = timeNow.strftime("%H:%M:%S")
    dateNow = date.today()
    currentDate = dateNow.strftime("%Y-%m-%d")
    
    # connection to the database and extraction of values from settings table
    mydb = mysql.connector.connect(host="localhost", user="pi", password="pi_101222782", database="Smart Door")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Settings")
    settings = mycursor.fetchall()
    
    # obtains all settings values
    doorHeight = settings[0][1]
    irSensorInThreshold = settings[0][2]
    irSensorOutThreshold = settings[0][3]
    timeClose = settings[0][4]
    timeDetection = settings[0][5]
    timeFaceDetection = settings[0][6]
    
    # obtains, reads and extracts the different data from Arduino
    line = arduino.readline().decode().strip()
    sensorValue = line.split(",")
    
    # obtains the IR proximity sensors distances (in and out)
    subjectDistanceIn = int(sensorValue[0])
    subjectDistanceOut = int(sensorValue[1])
    
    print("DistanceIn: ", subjectDistanceIn)
    print("DistanceOut: ", subjectDistanceOut)
    
    # if subject is within range outside the house (going in)
    if subjectDistanceIn <= irSensorInThreshold:
        directionIn = True
        inHouse = "1"
    
    # if subject is within range inside the house (going out)
    if subjectDistanceOut <= irSensorOutThreshold:
        directionOut = True
        inHouse = "0"
    
    # runs when only the IR proximity sensors distances are received (when no rfid is scanned)
    if len(sensorValue) == 2:
        # runs when someone is detected to be outside the smart door
        if directionIn == True:
            if personDetected == False:
                timeDetectionStart = datetime.now()
                timeDetected = Countdown()
                personDetected = True
                strangerWrite = True
                
                # Lights up yellow LED
                arduino.write(b"2")
                time.sleep(1)
                
            if personDetected == True:
                # runs when a stranger has been outside the smart door for more than the set time
                if Countdown() - timeDetected > timeDetection * 1000:
                    if strangerWrite == True:
                        sql = "INSERT INTO Stranger (time, date, status) VALUES ('" + currentTime + "', '" + currentDate + "', 'No RFID')"
                        mycursor.execute(sql)
                        mydb.commit()
                        
                        # publishes MQTT message
                        noRFIDMessage = "stranger," + currentTime + "," + currentDate + ",No RFID"
                        client.publish(topic, noRFIDMessage)
                        
                    strangerWrite = False
                    
                    # continuously beeps the buzzer and blinks the red LED until the stranger leaves
                    arduino.write(b"4")
                    time.sleep(1)
                    
                showRed = True
        # runs when the stranger has left or when there are no strangers   
        else:
            personDetected = False
            
            if showRed == True:
                # Lights up red LED
                arduino.write(b"1")
                time.sleep(1)
                            
                showRed = False
                    
        # runs when someone is detected to be inside the smart door
        if directionOut == True:
            pass
        else:
            pass
        
        # resets the presence of someone at the door
        directionIn = False
        directionOut = False
    # runs when the IR proximity sensors distances, RFID value, ultrasonic sensor distance and weight are received (when rfid is scanned)
    elif len(sensorValue) == 5:
        # checks if someone is at the door when the rfid is scanned
        if inHouse != "2":
            personDetected = False
            
            # obtains the RFID value, ultrasonic sensor distance and weight
            rfidValue = sensorValue[2]
            ultrasonicSensorDistance = float(sensorValue[3])
            potentiometerWeight = float(sensorValue[4])
            
            # calculates the height and bmi of the user
            userHeight = doorHeight - ultrasonicSensorDistance
            bmi = potentiometerWeight / ((userHeight / 100) ** 2)
            bmi = round(bmi, 2)
            
            print("Location: ", inHouse)
            print("RFID Value: ", rfidValue)
            print("Height: ", userHeight)
            print("Weight: ", potentiometerWeight)
            print("BMI: ", bmi)
            
            mycursor.execute("SELECT Profile.profile_id, Profile.name, RFID.number FROM Profile LEFT JOIN RFID ON Profile.rfid_id=RFID.rfid_id")
            rfidProfile = mycursor.fetchall()
            
            # checks whether the RFID value is one of the existing RFID values
            existingRFID = []
                        
            for i in rfidProfile:
                existingRFID.append(i[2])
                
            if rfidValue not in existingRFID:
                sql = "INSERT INTO Stranger (time, date, status) VALUES ('" + currentTime + "', '" + currentDate + "', 'Wrong RFID')"
                mycursor.execute(sql)
                mydb.commit()
                
                # publishes MQTT message
                wrongRFIDMessage = "stranger," + currentTime + "," + currentDate + ",Wrong RFID"
                client.publish(topic, wrongRFIDMessage)
                
                # lights up red LED and makes a long beeping sound
                arduino.write(b"5")
                time.sleep(1)
            else:
                # goes through the different user profiles
                for i in rfidProfile:
                    # checks whether the RFID value exists
                    if rfidValue == i[2]:
                        # counts down the duration set to detect face
                        timeDetectionStart = datetime.now()
                        timeDetected = Countdown()
                        
                        # calls the detection function in SmartDoorDetection.py
                        faceDetected = detection(i[1], timeDetected, timeDetectionStart, timeFaceDetection)
                        
                        # checks whether the user bound to the RFID value matches the face of the user
                        if faceDetected == True:
                            faceDetected = False
                            
                            # adds and updates the values in the tables
                            sql = "INSERT INTO History (profile_id, time, date, height, weight, bmi, in_house) VALUES ('" + str(i[0]) + "', '" + currentTime + "', '" + currentDate + "', '" + str(userHeight) + "', '" + str(potentiometerWeight) + "', '" + str(bmi) + "', '" + inHouse + "')"
                            mycursor.execute(sql)
                            mydb.commit()
                            
                            sql = "UPDATE Profile SET height = '" + str(userHeight) + "' WHERE profile_id = '" + str(i[0]) + "'"
                            mycursor.execute(sql)
                            mydb.commit()
                            
                            sql = "UPDATE Profile SET weight = '" + str(potentiometerWeight) + "' WHERE profile_id = '" + str(i[0]) + "'"
                            mycursor.execute(sql)
                            mydb.commit()
                            
                            sql = "UPDATE Profile SET bmi = '" + str(bmi) + "' WHERE profile_id = '" + str(i[0]) + "'"
                            mycursor.execute(sql)
                            mydb.commit()
                            
                            sql = "UPDATE Profile SET in_house = '" + inHouse + "' WHERE profile_id = '" + str(i[0]) + "'"
                            mycursor.execute(sql)
                            mydb.commit()
                            
                            # publishes MQTT message
                            addHistoryMessage = "history," + str(i[0]) + "," + currentTime + "," + currentDate + "," + str(userHeight) + "," + str(potentiometerWeight) + "," + str(bmi) + "," + inHouse
                            client.publish(topic, addHistoryMessage)
                            updateProfileMessage = "profile," + str(i[0]) + "," + str(userHeight) + "," + str(potentiometerWeight) + "," + str(bmi) + "," + inHouse
                            client.publish(topic, updateProfileMessage)
                            
                            # lights up green LED, makes 'granted' sound and opens door for set time before closing
                            doorOpen = "open " + str(timeClose)
                            arduino.write(doorOpen.encode('utf-8'))
                            time.sleep(1)
                        else:
                            sql = "INSERT INTO Stranger (time, date, status) VALUES ('" + currentTime + "', '" + currentDate + "', 'Wrong User')"
                            mycursor.execute(sql)
                            mydb.commit()
                            
                            # publishes MQTT message
                            wrongUserMessage = "stranger," + currentTime + "," + currentDate + ",Wrong User"
                            client.publish(topic, wrongUserMessage)
                        
                            # lights up red LED and makes a long beeping sound
                            arduino.write(b"5")
                            time.sleep(1)
        else:
            sql = "INSERT INTO Stranger (time, date, status) VALUES ('" + currentTime + "', '" + currentDate + "', 'No User')"
            mycursor.execute(sql)
            mydb.commit()
            
            # publishes MQTT message
            noUserMessage = "stranger," + currentTime + "," + currentDate + ",No User"
            client.publish(topic, noUserMessage)
                        
            # lights up red LED and makes a long beeping sound
            arduino.write(b"5")
            time.sleep(1)
        
    # resets user location
    inHouse = "2"
        
    mycursor.close()
    print("-------------------------------")