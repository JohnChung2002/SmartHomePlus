import mysql.connector
import serial
import datetime
import time
import paho.mqtt.client as mqtt

device = '/dev/ttyACM0'
arduino = serial.Serial(device, 9600)

while True:
    
    mydb = mysql.connector.connect(host="localhost", user="hp", password="0123", database="waterSprinkler_db")
#     print(mydb)

    while(arduino.in_waiting == 0):
        pass

    data = arduino.readline().decode('utf-8').strip()
    print("Received data:", data) # Print received data for debugging

    # Parse sensor readings from received data
    readings = data.split(",")
    print(readings)
    
    if len(readings) == 3:
        
        temperature = int(readings[0])
        
        wetnessLevel = readings[1]
        if wetnessLevel == "":
            wetnessLevel = 0
        else:
            wetnessLevel = int(readings[1])
            
        brightness = int(readings[2])
        
        
        # Set the desired time for sprinkler activation
#         desired_hour = 17  # Update with your desired hour (24-hour format)
#         desired_minute = 0  # Update with your desired minute
        
        # Run this code for the cloud
        
#         while True:
#             
#             # Get the current time
#             current_time = datetime.now().time()
#             if current_time.hour == desired_hour and current_time.minute == desired_minute:
#                 
#                 arduino.write(b"6")                
#                 print("Sprinkler turned ON")
#                 break
#                 
#             time.sleep(2)
        

        if temperature > 15:
            status = "Hot weather"
            if brightness >= 500:
                status3 = "Daytime"
                if wetnessLevel < 500:
                    status2 = "Soil is dry"
                    systemStat = "Sprinkler is on"
                    arduino.write(b"6")
                    time.sleep(1)
                    
                elif wetnessLevel >= 500:
                    status2 = "Soil is moist"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"4")
                    time.sleep(1)  
                    
                    
            elif brightness < 500:
                status3 = "Nighttime"
                time.sleep(1)
                if wetnessLevel < 500:
                    status2 = "No rain detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"4")
                    time.sleep(1)
                    
                    
                elif wetnessLevel >= 500:
                    status2 = "Rain is detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"4")
                    time.sleep(1)
                    
        elif temperature <= 15:
            status = "Cool weather"
            if brightness >= 500:
                status3 = "Daytime"
                time.sleep(1)
                if wetnessLevel < 500:
                    status2 = "No rain detected"
                    systemStat = "Sprinkler is on"
                    arduino.write(b"6")
                    time.sleep(1)
                    
                elif wetnessLevel >= 500:
                    status2 = "Rain is detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"4")
                    time.sleep(1)
                    
                    
            elif brightness < 500:
                status3 = "Nighttime"
                if wetnessLevel < 500:
                    status2 = "No rain detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"4")
                    time.sleep(1)
                    
                elif wetnessLevel >= 500:
                    status2 = "Rain is detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"4")
                    time.sleep(1)
                    
#     elif len(readings) == 4:
#         temperature = int(readings[0])
#         wetnessLevel = readings[1]
#         if wetnessLevel == "":
#             wetnessLevel = 0
#         else:
#             wetnessLevel = int(readings[1])    
#         brightness = int(readings[2])
#         intruder = int(readings[3])
#         
#         if intruder > 500:
#             status4 = "Intruder detected"
#             arduino.write(b"3")
        
                    
        
    print(temperature, wetnessLevel, brightness)    
    print("Temperature:", status, "Wet Status:", status2, "Time of day:", status3)
    print(systemStat)
    
    
    def on_connect(client, userdata, flags, rc):
    print(f"Connected with RC: {str(rc)}")
    pass
    
    def on_publish(client, data, result):
        print("Message sent to MQTT broker")
        pass

    def on_message(client, userdata, msg):
        message_mqtt = msg.payload.decode()
        if message_mqtt == "Sprinkler Off":
            arduino.write(b"4")
        elif message_mqtt == "Sprinkler On":
            arduino.writee(b"6")           
        elif message_mqtt == "Spray at intruder":
            arduino.write(b"7")
     
    client = mqtt.Client()
    client.username_pw_set(username=os.getenv("LOCAL_MQTT_USERNAME"), password=os.getenv("LOCAL_MQTT_PASSWORD")) # type: ignore
    client.on_connect = on_connect 
    client.on_publish = on_publish
    client.on_message = on_message
    client.connect(os.getenv("LOCAL_MQTT_HOST"), int(os.getenv("LOCAL_MQTT_PORT")), 60) # type: ignore

    topic = "/cheryl_node"
    client.subscribe(topic)

    client.loop_start()
    
    
    with mydb:      

        mycursor = mydb.cursor() 
        mycursor.execute("INSERT INTO systemData (temperature, tempStatus, wetness, wetStatus, brightness, timeOfDay, sprinklerStatus) VALUES (%s, '%s', %s, '%s', %s, '%s', '%s')" %(temperature, status, wetnessLevel, status2, brightness, status3, systemStat))        
    
    

        mydb.commit()
        mycursor.close()
    
