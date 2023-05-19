// libraries
#include <SPI.h>
#include <RFID.h>
#include <Servo.h>
#include <SharpIR.h>

// defining pins
#define SS_PIN 10
#define RST_PIN 9
#define buzzerPin 8
#define trigPin 7
#define echoPin 6
#define servoPin 5
#define ledred 4
#define ledyellow 3
#define ledgreen 2
#define irSensorPin2 A2
#define irSensorPin1 A1
#define potentiometer A0

// defining IR proximity sensor model
#define model1 20150
#define model2 20150

// initialization for integer obtained from serial data
unsigned int pinStatus = 0;

// initialization for servo
Servo servo;

// initialization for RFID
RFID rfid(SS_PIN, RST_PIN);
String rfidCard;

// initialization for ultrasonic sensor
long duration, usDistance;

// delay for serial data to be sent (prevent delay() from interrupting the buzzer and led delay)
long printDelay = 1000;

// stores value from potentiometer
int potentiometerValue;

// stores the calculated weight
float weight;

// initialization for the two IR proximity sensors (in and out)
SharpIR irSensorIn(irSensorPin1, model1);
SharpIR irSensorOut(irSensorPin2, model2);

// stores the distance between the subject and door
int irSensorInDistance;
int irSensorOutDistance;

// ---------------------------------------------------------------------------------------------------------------------------------------------

void setup() {
  Serial.begin(9600);

  // initializes rfid
  SPI.begin();
  rfid.init();

  // initializes buzzer
  pinMode(buzzerPin, OUTPUT);

  // initializes ultrasonic distance sensor
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // initializes servo motor
  servo.attach(servoPin);
  servo.write(180);  // closed state

  // initializes LEDs
  pinMode(ledred, OUTPUT);
  pinMode(ledyellow, OUTPUT);
  pinMode(ledgreen, OUTPUT);
  
  digitalWrite(ledred,HIGH);
  digitalWrite(ledyellow,LOW);
  digitalWrite(ledgreen,LOW);
}

// ---------------------------------------------------------------------------------------------------------------------------------------------

void loop() {
  // initialization of delay for serial data to be sent
  long timeCurrent = millis();
  static long timeDelay = 0;

  // -------------------------------------------------------------------------------------------------------------------------------------------
  
  // Checks for data in serial port
  if (Serial.available() > 0) {
      String serialInput;

      // receives serial input
      serialInput = Serial.readString();

      // runs when rfid is recognised and is bound to the person under facial recognition (turns led green, plays 'granted' sound, moves servo to open door, waits for time set to close, before led turns back to red)
      if (serialInput.startsWith("open")) {
          String timeClose;

           // extracts the time for door to close
          int serialInputIndex = serialInput.indexOf(' ');
          serialInput.remove(0, serialInputIndex + 1);
          serialInputIndex = serialInput.indexOf(' ');
          timeClose = serialInput.substring(0, serialInputIndex);

          digitalWrite(ledred,LOW);
          digitalWrite(ledyellow,LOW);
          digitalWrite(ledgreen,HIGH);
          
          digitalWrite(buzzerPin, HIGH);
          delay(100);
          digitalWrite(buzzerPin, LOW);
          delay(100);
          digitalWrite(buzzerPin, HIGH);
          delay(100);
          digitalWrite(buzzerPin, LOW);
          delay(100);
          digitalWrite(buzzerPin, HIGH);
          delay(100);
          digitalWrite(buzzerPin, LOW);
          delay(100);

          // opens door
          servo.write(0);

          // time for door to close after open
          delay(timeClose.toInt() * 1000);

          // returns back to closed state
          servo.write(180);
          
          digitalWrite(ledred,HIGH);
          digitalWrite(ledyellow,LOW);
          digitalWrite(ledgreen,LOW);
      } else {
          pinStatus = serialInput.toInt();
          
          switch (pinStatus) {
            // only lights up red LED
            case 1: 
              digitalWrite(ledred,HIGH);
              digitalWrite(ledyellow,LOW);
              digitalWrite(ledgreen,LOW); 
              break;
            // only lights up yellow LED
            case 2: 
              digitalWrite(ledred,LOW);
              digitalWrite(ledyellow,HIGH);
              digitalWrite(ledgreen,LOW); 
              break;
            // only lights up green LED
            case 3: 
              digitalWrite(ledred,LOW);
              digitalWrite(ledyellow,LOW);
              digitalWrite(ledgreen,HIGH);
              break;
            // makes a beeping sound and lights up red LED at the same time, and turns them off at the same time ('alarm' sound)
            case 4: 
              digitalWrite(buzzerPin, HIGH);
              digitalWrite(ledred,HIGH);
              delay(250);
              digitalWrite(buzzerPin, LOW);
              digitalWrite(ledred,LOW);
              break;
            // lights up the red LED and makes a long beeping sound ('denied' sound)
            case 5:
              digitalWrite(ledred,HIGH);
              digitalWrite(ledyellow,LOW);
              digitalWrite(ledgreen,LOW);
              
              digitalWrite(buzzerPin, HIGH);
              delay(1000);
              digitalWrite(buzzerPin, LOW);
              break;
            // opens door and lights up green LED   
            case 6:
              servo.write(0);  // opened state

              digitalWrite(ledred,LOW);
              digitalWrite(ledyellow,LOW);
              digitalWrite(ledgreen,HIGH); 
              break;
            // closes door and lights up red LED
            case 7:
              servo.write(180);  // closed state

              digitalWrite(ledred,HIGH);
              digitalWrite(ledyellow,LOW);
              digitalWrite(ledgreen,LOW); 
              break;  
            default: 
              break;   
          }
      }
  }

  // -------------------------------------------------------------------------------------------------------------------------------------------
  
  // Ultrasonic Sensor
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // reads and calculates the distance
  duration = pulseIn(echoPin, HIGH);
  usDistance = (duration/2) / 29.1;

  // -------------------------------------------------------------------------------------------------------------------------------------------

  // IR Proximity Sensor
  irSensorInDistance = irSensorIn.distance();
  irSensorOutDistance = irSensorOut.distance();

  // -------------------------------------------------------------------------------------------------------------------------------------------

  // RFID
  if (rfid.isCard()) {
    if (rfid.readCardSerial()) {
      rfidCard = String(rfid.serNum[0]) + " " + String(rfid.serNum[1]) + " " + String(rfid.serNum[2]) + " " + String(rfid.serNum[3]);

      // adds delay to the data sent
      if (timeCurrent - timeDelay >= printDelay) {
        timeDelay = timeCurrent;
        
        // potentiometer (simulates load cell)
        potentiometerValue = analogRead(potentiometer);

        // obtains weight minimum of 1kg and weight limit of 150kg
        weight = map(potentiometerValue, 0, 1023, 1, 150);

        // sends data to serial port
        Serial.print(irSensorInDistance);
        Serial.print(",");
        Serial.print(irSensorOutDistance);
        Serial.print(",");
        Serial.print(rfidCard);
        Serial.print(",");
        Serial.print(usDistance);
        Serial.print(",");
        Serial.println(weight);
      }
    }
    rfid.halt();
  } else {
    // adds delay to the data sent
    if (timeCurrent - timeDelay >= printDelay) {
      timeDelay = timeCurrent;

      // sends data to serial port
      Serial.print(irSensorInDistance);
      Serial.print(",");
      Serial.println(irSensorOutDistance);
    }
  }
}
