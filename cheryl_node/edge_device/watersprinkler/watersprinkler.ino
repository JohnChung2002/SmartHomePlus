#include <Servo.h>

// Pin connected to the potentiometer
const int potentiometerPin = A0;

// Pin connected to the water sensor
const int waterSensorPin = A1;

// LDR pin connected to analog pin A2
const int ldrPin = A2;    

// LED pin connected to digital pin 12 and 13
const int ledRed = 13;  
const int ledGreen = 12;  

// The number of the pushbutton pin
const int buttonPin = A3;     

// variable for reading the pushbutton status
int buttonState = 0;         

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

  // Initialize the LED pin as an output
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  
  // Set the LDR pin as an input
  pinMode(ldrPin, INPUT);
  
  // Enable the internal pull-up resistor for the LDR pin
  digitalWrite(ldrPin, LOW);
  
  // Set the button pin as an input
  pinMode(buttonPin, INPUT); 


}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    pinStatus = Serial.parseInt();

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
        digitalWrite(ledGreen, LOW);
        digitalWrite(ledRed, LOW);
        break;
      case 5:
        digitalWrite(ledGreen, HIGH);
        digitalWrite(ledRed, HIGH);
        break;
      case 6:
        digitalWrite(ledRed, LOW);
        digitalWrite(ledGreen, HIGH);
        break;
      case 7:
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
//  Serial.print(temperature);
  // Display weather indication based on temperature value
  if (temperature < 15) {
//    Serial.print("Cool weather");  // Display "Cold weather" for temperature below 0
    Serial.print(temperature);
  } else {
//    Serial.print("Hot weather");   // Display "Hot weather" for temperature above 15
    Serial.print(temperature);
  }
  
  Serial.print(",");

  // Read the analog value from the water sensor
  int wetnessValue = analogRead(waterSensorPin);
//  Serial.print(wetnessValue);
  // Display wetness indication based on wetness level
  if (wetnessValue > threshold ) {
//    Serial.print("It is currently raining!");    // Display to show if water is detected
    Serial.print(wetnessValue);
  } else {
//    Serial.print("No rain is detected");   // Display to show if no water is detected
    Serial.print(wetnessValue);
  }

  Serial.print(",");

  // Read the analog value from the LDR
  int ldrValue = analogRead(ldrPin);
//  Serial.println(ldrValue);

  // Check if the LDR value is below a certain threshold, indicating darkness
  if (ldrValue < 500) {
    // Turn on the LED
    digitalWrite(ledRed, HIGH);
    Serial.println(ldrValue);
  } else {
    // Turn off the LED
    digitalWrite(ledRed, LOW);
    Serial.println(ldrValue);
  }

//  Serial.print(",");

  // read the state of the pushbutton value:
  buttonState = digitalRead(buttonPin);


  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState == HIGH) {
    // turn LED on:
    digitalWrite(13, HIGH);
//    Serial.println(buttonState);
  } else {
    // turn LED off:
    digitalWrite(13, LOW);    
//    Serial.println(buttonState);
  }
  
  delay(10000);  // Delay for stability


}