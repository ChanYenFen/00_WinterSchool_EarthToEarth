#include "config.h"
#include <Stepper.h>

int toExtrude = -1;

Stepper myStepper(stepPerRevolution,dirPin, stepPin);

void setup() {
  Serial.begin(9600);
  // Declare pins:
  pinMode(relay_1, OUTPUT);
  pinMode(urAO_0, INPUT);
  digitalRead(urAO_0);
  // ************
  
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);

  //60rpm = 1rps
  myStepper.setSpeed(100*4);
  

}

void loop() 
{
  // ******Tracking UR signals******
  toExtrude = digitalRead(urAO_0);
  // *******************************

  if (toExtrude == HIGH ) 
  {
    digitalWrite(relay_1, HIGH);
    extrusionL();
  }
  
  /*else if (toExtrude == 0)
  { 
    retraction();
  }*/
}

void extrusion()
{
  digitalWrite(dirPin, HIGH);

  digitalWrite(stepPin, HIGH);
  delayMicroseconds(400);
  digitalWrite(stepPin, LOW);
  delayMicroseconds(400);
}

void extrusionL()
{
  myStepper.step(1);
//  delay(500);
}

void testRevolution()
{
  myStepper.step(stepPerRevolution);
  delay(300);

}
