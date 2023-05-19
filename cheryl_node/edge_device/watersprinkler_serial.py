import mysql.connector
import serial
import time

device = '/dev/ttyACM0'
arduino = serial.Serial(device, 9600)

while True:
    
    mydb = mysql.connector.connect(host="localhost", user="hp", password="0123", database="waterSprinkler_db")
    print(mydb)

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


        if temperature > 15:
            status = "Hot weather"
            if brightness >= 500:
                status3 = "Daytime"
#                 arduino.write(b"6")
#                 time.sleep(1)
                if wetnessLevel < 500:
                    status2 = "No rain detected"
                    systemStat = "Sprinkler is on"
                    arduino.write(b"2")
                    arduino.write(b"6")
                    print("yes")
#                     time.sleep(1)
                    
                elif wetnessLevel >= 500:
                    status2 = "Rain is detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"1")
                    arduino.write(b"6")
#                     time.sleep(1)
                    
                    
            elif brightness < 500:
                status3 = "Nighttime"
#                 arduino.write(b"7")
                time.sleep(1)
                if wetnessLevel < 500:
                    status2 = "No rain detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"1")
                    arduino.write(b"6")
                    print("why")
#                     time.sleep(1)
                    
                elif wetnessLevel >= 500:
                    status2 = "Rain is detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"1")
#                     time.sleep(1)
                    
        elif temperature <= 15:
            status = "Cool weather"
            if brightness >= 500:
                status3 = "Daytime"
#                 arduino.write(b"6")
                time.sleep(1)
                if wetnessLevel < 500:
                    status2 = "No rain detected"
                    systemStat = "Sprinkler is on"
                    arduino.write(b"2")
#                     time.sleep(1)
                    
                elif wetnessLevel >= 500:
                    status2 = "Rain is detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"1")
#                     time.sleep(1)
                    
                    
            elif brightness < 500:
                status3 = "Nighttime"
#                 arduino.write(b"6")
                time.sleep(1)
                if wetnessLevel < 500:
                    status2 = "No rain detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"1")
#                     time.sleep(1)
                    
                elif wetnessLevel >= 500:
                    status2 = "Rain is detected"
                    systemStat = "Sprinkler is off"
                    arduino.write(b"1")
#                     time.sleep(1)
                    
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
    
    with mydb:      

        mycursor = mydb.cursor() 
        mycursor.execute("INSERT INTO systemData (temperature, tempStatus, wetness, wetStatus, brightness, timeOfDay, sprinklerStatus) VALUES (%s, '%s', %s, '%s', %s, '%s', '%s')" %(temperature, status, wetnessLevel, status2, brightness, status3, systemStat))        
    
    
#         sql = "INSERT INTO systemData (temperature, tempStatus, wetness, wetStatus, brightness, timeOfDay, sprinklerStatus) VALUES (%s, %s, %s, %s, %s, %s, %s)"
#         values = (temperature, status, wetnessLevel, status2, brightness, status3, systemStat)
# 
#         mycursor.execute(sql, values)

        mydb.commit()
        mycursor.close()
    
    
    
