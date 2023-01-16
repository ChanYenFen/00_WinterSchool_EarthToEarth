#include <AccelStepper.h>
#include "config.h"

int toExtrude = -1;

String positionPr;
String retrPr;

int retrCount;
int retrSteps;

int ifRetracted = -1;

int currentPos;

bool hasExtr;
bool hasRetr;

AccelStepper extrMotor(AccelStepper::DRIVER , stepPin, dirPin); 

void setup() {
  Serial.begin(115200);
  
  extrMotor.setMaxSpeed(2000); // to limit the value of setSpeed()   
  //extrMotor.setSpeed(200);
  // Declare pins:
  pinMode(relay_1, OUTPUT);
  pinMode(urAO_0, INPUT);
  digitalRead(urAO_0);
  // ************
  
  positionPr = String("Motor is at: ");
  retrPr = String("Retraction step is: ");
  hasExtr = false;
  hasRetr = false;

  extrMotor.setMinPulseWidth(1);

  retrCount = 0;
  retrSteps =  3000;
}

void loop() 
{
  // ******Tracking UR signals******
  toExtrude = digitalRead(urAO_0);
  // *******************************

  if (toExtrude == 1 ) 
  {
    extrusion();
  }
  
  /*else if (toExtrude == 0)
  { 
    retraction();
  }*/
}

void extrusion()
{
  /*
  for extrudsion the code below contains 4 parts:
  1. initialize stepper motor and power, then spin
  2. print out current position and save the value globally  
  3. reset parameters for retraction afterwards
  */
  
  digitalWrite(relay_1, HIGH);
  extrMotor.setSpeed(100);
  extrMotor.runSpeed();
  currentPos = extrMotor.currentPosition();
  if (currentPos%10 == 0)
  {Serial.println(positionPr + currentPos);}

//  hasExtr = true;
//  hasRetr = false;
//  retrCount = 0;
}
/*
void retraction()
{
  

}*/
