#include <Servo.h>
#include <TimeOut.h>

// Pin connected to the potentiometer
const int potentiometerPin = A0;

// Pin connected to the water sensor
const int waterSensorPin = A1;

// LDR pin connected to analog pin A2
const int ldrPin = A2;    

// LED pin connected to digital pin 12 and 13
const int ledRed = 10;  
const int ledGreen = 12;  

// The number of the pushbutton pin
const int buttonPin = 2;     

// variable for reading the pushbutton status
int buttonState = 0;    
int buttonStatus = 0;     

// Temperature range
const int minTemp = 0;     // Minimum temperature value from the potentiometer
const int maxTemp = 1023;  // Maximum temperature value from the potentiometer

// Create a Servo object
Servo sprinklerServo;
TimeOut timeout0;

// The pin connected to the servo
const int servoPin = 11;

int wetthreshold = 500; // Set the threshold value of the water sensor
int lightthreshold = 400; // Set the threshold value of the light sensor

String commandInput;

const int desiredMoisture = 30;  // Desired moisture level in percentage

int currentMoisture = 0;
int currentLightLevel = 0;
int sprinklerPosition = 0;
bool isSprinklerOn = false;
bool previousSprinklerStatus = false;
bool override = false;
bool intruder = false;

void setSprinklerStatus(int position) {
  sprinklerServo.write(position);
  sprinklerPosition = position;
  isSprinklerOn = (position > 0 && position <= 90);
} 

void endIntruderOverride() {
  override = false;
}

void setup() {
  //Initialize serial communication for debugging
  
  Serial.begin(9600); 
  //Attach the servo pin
  sprinklerServo.attach(servoPin); 

  // Initialize the servo position
  setSprinklerStatus(180);

  // Initialize the LED pin as an output
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);

  // Initialize the LED pin as turned off
  digitalWrite(ledRed, LOW);
  digitalWrite(ledGreen, LOW);
  
  // Set the LDR pin as an input
  pinMode(ldrPin, INPUT);
  
  // Enable the internal pull-up resistor for the LDR pin
  digitalWrite(ldrPin, LOW);
  
  // Set the button pin as an input
  pinMode(buttonPin, INPUT_PULLUP); 

  
}

void loop() {
  TimeOut::handler();
  if (Serial.available() > 0) {
    commandInput = Serial.readString();

    if (commandInput == "On") {
      override = true;
      sprinklerServo.write(90);
      digitalWrite(ledGreen, HIGH);
      digitalWrite(ledRed, LOW);
    } else if (commandInput == "Off") {
      override = false;
      sprinklerServo.write(180);
      digitalWrite(ledGreen, LOW);
      digitalWrite(ledRed, LOW);
    } else if (commandInput == "Spray") {
      override = true;
      intruder = true;
      timeout0.cancel();
      sprinklerServo.write(0);
      digitalWrite(ledGreen, LOW);
      digitalWrite(ledRed, HIGH);
    } else if (commandInput.indexOf("Update|") != -1) {
      wetthreshold = commandInput.substring(7).toInt();
    }
  }

  // Read the analog value from the potentiometer
  int potValue = analogRead(potentiometerPin);
  // Map the analog value to the temperature range
  int temperature = map(potValue, minTemp, maxTemp, -20, 50);
  // Read the moisture level from the water sensor
  int wetnessValue = analogRead(waterSensorPin);
  // Read the light level from the LDR
  int ldrValue = analogRead(ldrPin);

  // Check if it is daytime and the moisture level is low
  if (!override) {
    if (ldrValue > lightthreshold && wetnessValue < wetthreshold) {
      if (!isSprinklerOn) {
        // Turn on the sprinkler
        setSprinklerStatus(90);
        Serial.println("Sprinkler turned ON");
        digitalWrite(ledGreen, HIGH);
        digitalWrite(ledRed, LOW);
      }
    } else {
      if (isSprinklerOn) {
        // Turn off the sprinkler
        setSprinklerStatus(180);
        Serial.println("Sprinkler turned OFF");
        digitalWrite(ledRed, LOW);
        digitalWrite(ledGreen, LOW);
      }
    }
  } else {
    if (intruder) {
      timeout0.timeOut(10000, endIntruderOverride);
      intruder = false;
    }
  }
  

  delay(100);
  
  Serial.print(wetnessValue);
  Serial.print(",");
  Serial.print(ldrValue);
  Serial.print(",");
  Serial.println(temperature);

  // Check if the sprinkler status has changed
  if (previousSprinklerStatus != isSprinklerOn) {
    // Update the previous sprinkler status
    previousSprinklerStatus = isSprinklerOn;
  }

  // Wait for a short interval before checking again
  delay(1000);
}
