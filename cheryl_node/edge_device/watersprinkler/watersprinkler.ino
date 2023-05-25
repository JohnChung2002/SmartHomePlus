#include <Servo.h>

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

Servo myServo; // Create a Servo object

int threshold = 500; // Set the threshold value of the water sensor

unsigned int pinStatus = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);  // Initialize serial communication for debugging
  myServo.attach(11); // Attach the servo to pin 3
  myServo.write(180); // Starts from this position

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
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    pinStatus = Serial.parseInt();
    Serial.println(pinStatus);

    switch (pinStatus){
      case 1:
        myServo.write(180);
        break;
      case 2:
        myServo.write(90);
        break;
      case 3:
        myServo.write(0);
        break;
      case 4:
        myServo.write(180);
        digitalWrite(ledGreen, LOW);
        digitalWrite(ledRed, LOW);
        break;
      case 5:
        myServo.write(90);
        digitalWrite(ledGreen, HIGH);
        digitalWrite(ledRed, HIGH);
        break;
      case 6:
        myServo.write(90);
        digitalWrite(ledRed, LOW);
        digitalWrite(ledGreen, HIGH);
        break;
      case 7:
        myServo.write(90);
        digitalWrite(ledRed, HIGH);
        digitalWrite(ledGreen, LOW);
        break;
      default:
        break;                            
    }
  }

  // Read the analog value from the potentiometer
  int potValue = analogRead(potentiometerPin);

  // Map the analog value to the temperature range
  int temperature = map(potValue, minTemp, maxTemp, -20, 50);
  Serial.print(temperature);

  Serial.print(",");


  // Read the analog value from the water sensor
  int wetnessValue = analogRead(waterSensorPin);
  Serial.print(wetnessValue);


  Serial.print(",");

  // Read the analog value from the LDR
  int ldrValue = analogRead(ldrPin);
  Serial.println(ldrValue);
//  Serial.print(",");


  // read the state of the pushbutton value:
//  buttonPress();
//  Serial.print("Button State: ");
//  Serial.println(buttonState);


  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
//  if (buttonState == LOW) {
//    // turn LED on:
//    digitalWrite(10, HIGH);
//    Serial.println(buttonState);
//  } else {
//    // turn LED off:
//    digitalWrite(10, LOW);    
//    Serial.println(buttonState);
//  }
  
  delay(1000);  // Delay for stability


}

void buttonPress() {
  int reading = digitalRead(buttonPin);
  if (reading == 0 && buttonStatus == 0) {
    buttonState = !buttonState;
    //Status Changed
    buttonStatus = 1;
  }
  if (reading == 1 && buttonStatus == 1) {
    buttonStatus = 0;
  }
}


void stableDelay(int interval) {
  long startDelayTime = millis();
  while (true) {
    if (millis() - startDelayTime >= interval) {
      return;
    }
  }
}
