#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <TimeOut.h>
#include <ArduinoJson.h>

#define ROOM_1_LED 22
#define CORRIDOR_LED 23
#define ROOM_2_LED 24

#define ROOM_1_LIS A0
#define CORRIDOR_LIS A1
#define ROOM_2_LIS A2

#define MOTION_SENSOR 28
#define FAN 29

#define ROOM_1_THRESHOLD 10
#define CORRIDOR_THRESHOLD 40
#define ROOM_2_THRESHOLD 10

String serialInput, serialOutput;
StaticJsonDocument<500> jsonDoc;
int room1person = 0;
int room2person = 0;
int manualOverride[3] = {0, 0, 0};
int button_pins[7] = {2, 3, 4, 5, 6, 7, 8};
int button_status[14] = {0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1};
int motion_sensor_status = 0;
int airConStatus[2] = {0, 0};
int airConTemp[2] = {0, 0};
int ventilatingFanStatus = 0;

unsigned long lastMillis = 0;
unsigned long currentMillis = 0;
const unsigned long interval = 30000;
unsigned long motionLastMillis = 0;
unsigned long motionCurrentMillis = 0;
const unsigned long motionInterval = 30000;

void noStopDelay(int interval) {
  long startDelayTime = millis();
  while (true) {
    if (millis() - startDelayTime >= interval) {
      return;
    }
  }
}

void endOfMotion() {
  if (manualOverride[1] == 0) {
    button_status[6] = 0;
    serialOutput = "{'title': 'Lights', 'room': 'Corridor', 'status': '" + String(button_status[6]) + "'}";
    Serial.println(serialOutput);
  }
}

TimeOut timeout0;
LiquidCrystal_I2C lcd(0x27, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);

void setup()
{
  Serial.begin(9600);
  for (int i = 0; i < (sizeof(button_pins) / sizeof(button_pins[0])); i++) {
    pinMode(button_pins[i], INPUT_PULLUP);
  }
  pinMode(ROOM_1_LED, INPUT);
  pinMode(CORRIDOR_LED, INPUT);
  pinMode(ROOM_2_LED, INPUT);
  pinMode(MOTION_SENSOR, INPUT);
  pinMode(FAN, OUTPUT);
  lcd.begin(16, 2);
  lcd.clear();
  serialOutput = "{'title': 'Arduino Ready'}";
  Serial.println(serialOutput);
}

void loadInformation() {
  
}

void checkButtonClick() {
  for (int i = 0; i < (sizeof(button_status) / sizeof(button_status[0])); i+=2) {
    int reading = digitalRead(button_pins[(i/2)]);
    if (reading == 0 && button_status[i+1] == 1) {
      button_status[i+1] = 0;
      String output = "Pin " + String(button_pins[(i/2)]) + " Pressed once!";
      switch (button_pins[(i/2)]) {
        case 2:
          room1person++;
          serialOutput = "{'title': 'Room Count', 'room': '1', 'action': 'Inc'}";
          Serial.println(serialOutput);
          break;
        case 4:
          if (room1person != 0) {
            room1person--;
            serialOutput = "{'title': 'Room Count', 'room': '1', 'action': 'Dec'}";
            Serial.println(serialOutput);
          } else {
            room1person;
          }
          break;
        case 6:
          room2person++;
          serialOutput = "{'title': 'Room Count', 'room': '2', 'action': 'Inc'}";
          Serial.println(serialOutput);
          break;
        case 8:
          if (room2person != 0) {
            room2person--;
            serialOutput = "{'title': 'Room Count', 'room': '2', 'action': 'Dec'}";
            Serial.println(serialOutput);
          } else {
            room2person;
          }
        default:
          button_status[i] = !button_status[i];
          manualOverride[(button_pins[(i/2)]-3)/2] = !manualOverride[(button_pins[(i/2)]-3)/2];
          switch (button_pins[(i/2)]) {
            case 3:
              serialOutput = "{'title': 'Lights', 'room': '1', 'status': '" + String(button_status[i]) + "'}";
              break;
            case 5:
              serialOutput = "{'title': 'Lights', 'room': 'Corridor', 'status': '" + String(button_status[i]) + "'}";
              break;
            case 7:
              serialOutput = "{'title': 'Lights', 'room': '2', 'status': '" + String(button_status[i]) + "'}";
              break;
          }
          Serial.println(serialOutput);
          break;
      }
    }
    if (reading == 1 && button_status[i+1] == 0) {
      button_status[i+1] = 1;
    }
  }
}

void detectMotion() {
  int reading = digitalRead(MOTION_SENSOR);
  int corridor = analogRead(CORRIDOR_LIS);
  if (reading == 1 && motion_sensor_status == 1) {
    motion_sensor_status = 0;
    if (manualOverride[1] == 0) {
      button_status[6] = (corridor <= CORRIDOR_THRESHOLD);
      serialOutput = "{'title': 'Lights', 'room': 'Corridor', 'status': '" + String(button_status[6]) + "'}";
      Serial.println(serialOutput);
    }
    serialOutput = "{'title': 'Motion', 'action': 'Detected'}";
    Serial.println(serialOutput);
    timeout0.cancel();
  }
  if (reading == 0 && motion_sensor_status == 0) {
    motion_sensor_status = 1;
    serialOutput = "{'title': 'Motion', 'action': 'Ended'}";
    Serial.println(serialOutput);
    timeout0.timeOut(5000, endOfMotion);
  }
}

void checkBrightness() {
  int room_1 = analogRead(ROOM_1_LIS);
  int room_2 = analogRead(ROOM_2_LIS);
  if (manualOverride[0] == 0) {
    button_status[2] =  (room1person > 0) && (room_1 <= ROOM_1_THRESHOLD);
    if (button_status[2] == 1) {
      serialOutput = "{'title': 'Lights', 'room': '1', 'status': '" + String(button_status[2]) + "'}";
      Serial.println(serialOutput);
    }
  }
  if (manualOverride[2] == 0) {
    button_status[10] = (room2person > 0) && (room_2 <= ROOM_2_THRESHOLD);
    if (button_status[10] == 1) {
      serialOutput = "{'title': 'Lights', 'room': '2', 'status': '" + String(button_status[10]) + "'}";
      Serial.println(serialOutput);
    }
  }
}

void loop() {
  TimeOut::handler();
  if (Serial.available() != 0) {
    deserializeJson(jsonDoc, Serial.readString());
    if (jsonDoc["title"] == "Load Configurations") {
      button_status[2] = int(jsonDoc["room1Status"]);
      button_status[6] = int(jsonDoc["corridorStatus"]);
      button_status[10] = int(jsonDoc["room2Status"]);
      for (int i = 0; i < (sizeof(airConStatus) / sizeof(airConStatus[0])); i++) {
        airConStatus[i] = int(jsonDoc["aircon"][i]["status"]);
        airConTemp[i] = int(jsonDoc["aircon"][i]["temp"]);
      }
      lcd.clear();
      for (int i = 0; i < (sizeof(airConStatus) / sizeof(airConStatus[0])); i++) {
        lcd.setCursor(0, i);
        lcd.print("AC" + String(i+1) + ":" + String(airConStatus[i] ? "On |" : "Off|") + String(airConTemp[i]) + (char)223 +"C");
      }
      ventilatingFanStatus = int(jsonDoc["ventilatingFanStatus"]);
      serialOutput = "{'title': 'Load Configurations Response', 'status': 'Success'}";
      Serial.println(serialOutput);
    } else if (jsonDoc["title"] == "Aircon Switch") {
      if (jsonDoc["room"] == "1") {
        airConStatus[0] = int(jsonDoc["status"]);
      } else if (jsonDoc["room"] == "2") {
        airConStatus[1] = int(jsonDoc["status"]);
      }
      lcd.clear();
      for (int i = 0; i < (sizeof(airConStatus) / sizeof(airConStatus[0])); i++) {
        lcd.setCursor(0, i);
        lcd.print("AC" + String(i+1) + ":" + String(airConStatus[i] ? "On |" : "Off|") + String(airConTemp[i]) + (char)223 +"C");
      }
      serialOutput = "{'title': 'Aircon Switch Response', 'status': 'Success'}";
      Serial.println(serialOutput);
    } else if (jsonDoc["title"] == "Aircon Temp") {
      if (airConStatus[int(jsonDoc["room"])-1] == 1) {
        if (jsonDoc["room"] == "1" && airConStatus[int(jsonDoc["room"])-1] == 1) {
          airConTemp[0] = int(jsonDoc["temp"]);
        } else if (jsonDoc["room"] == "2" && airConStatus[int(jsonDoc["room"])-1] == 1) {
          airConTemp[1] = int(jsonDoc["temp"]);
        }
        lcd.clear();
        for (int i = 0; i < (sizeof(airConStatus) / sizeof(airConStatus[0])); i++) {
          lcd.setCursor(0, i);
          lcd.print("AC" + String(i+1) + ":" + String(airConStatus[i] ? "On |" : "Off|") + String(airConTemp[i]) + (char)223 +"C");
        }
        serialOutput = "{'title': 'Aircon Temp Response', 'status': 'Success'}";
        Serial.println(serialOutput);
      }
    } else if (jsonDoc["title"] == "Ventilating Fan") {
      ventilatingFanStatus = jsonDoc["status"];
      serialOutput = "{'title': 'Fan Response', 'status': '" + String(ventilatingFanStatus ? "On" : "Off") + "'}";
      Serial.println(serialOutput);
    } else if (jsonDoc["title"] == "Lights") {
      if (jsonDoc["room"] == "1") {
        button_status[2] = int(jsonDoc["status"]);
      } else if (jsonDoc["room"] == "2") {
        button_status[10] = int(jsonDoc["status"]);
      } else if (jsonDoc["room"] == "Corridor") {
        button_status[6] = int(jsonDoc["status"]);
      }
      serialOutput = "{'title': 'Lights Response', 'status': 'Success'}";
      Serial.println(serialOutput);
    } else if (jsonDoc["title"] == "Disengage Override") {
      for (int i = 0; i < (sizeof(manualOverride) / sizeof(manualOverride[0])); i++) {
        manualOverride[i] = 0;
      }
      serialOutput = "{'title': 'Disengage Override Response', 'status': 'Success'}";
      Serial.println(serialOutput);
    } else if (jsonDoc["title"] == "Intruder") {
      for (int i = 0; i < (sizeof(manualOverride) / sizeof(manualOverride[0])); i++) {
        manualOverride[i] = int(jsonDoc["status"]);
      }
      if (jsonDoc["status"] == "1") {
        button_status[2] = 1;
        button_status[6] = 1;
        button_status[10] = 1;
      }
      serialOutput = "{'title': 'Intruder Response', 'status': 'Success'}";
      Serial.println(serialOutput);
    }
  }
  checkButtonClick();
  detectMotion();
  currentMillis = millis();
  if (currentMillis - lastMillis >= interval) {
    checkBrightness();
    lastMillis = currentMillis;
  }
  digitalWrite(ROOM_1_LED, button_status[2]);
  digitalWrite(CORRIDOR_LED, button_status[6]);
  digitalWrite(ROOM_2_LED, button_status[10]);
  digitalWrite(FAN, ventilatingFanStatus);
  noStopDelay(100);
}
