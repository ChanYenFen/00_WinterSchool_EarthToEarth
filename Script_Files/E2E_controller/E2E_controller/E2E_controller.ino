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
  
  extrMotor.setMaxSpeed(3000); // to limit the value of setSpeed()   
  extrMotor.setSpeed(2800);
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
  extrMotor.runSpeed();
  currentPos = extrMotor.currentPosition();
  if (currentPos%10 == 0)
  {Serial.println(positionPr + currentPos);}

  hasExtr = true;
  hasRetr = false;
  retrCount = 0;
}

void retraction()
{
  /*
  for retraction the code below contains 4 parts:
  1. retraction happens in a while loop if the target step's not reached
  2. initialize stepper motor and power, then spin
  3. print out current position every 10 steps
  4. reset parameters for extrusion afterwards
  */
  extrMotor.setSpeed(-1000);
  digitalWrite(relay_1, HIGH);
  
  while (retrCount < retrSteps)
  {
    extrMotor.runSpeed();
    retrCount++;
    
    if (retrCount%10 == 0)
    {Serial.println(retrPr + retrCount);}
  }
  
  digitalWrite(relay_1, LOW);
  hasExtr = false;
  hasRetr = true;
}
