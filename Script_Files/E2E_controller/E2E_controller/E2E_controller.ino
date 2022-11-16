#include <AccelStepper.h>
#include "config.h"

int toExtrude = -1;

AccelStepper extrMotor(AccelStepper::DRIVER, 3,2); //pin 2 = dir, pin 3 = step

void setup() {
  Serial.begin(115200);
  
  extrMotor.setMaxSpeed(1000);


  // Dclare pins as output:
  //pinMode(dirPin, OUTPUT);
  //pinMode(stepPin, OUTPUT);
  pinMode(relay_1, OUTPUT);
  pinMode(urAO_0, INPUT);
  digitalRead(urAO_0);
}

void loop() {
  
  // ******Tracking UR signals******
  toExtrude = digitalRead(urAO_0);

  if (toExtrude) 
  {
    // motor spining
    digitalWrite(relay_1, HIGH);
    Serial.println("Motor is running");
    extrMotor.setSpeed(1000);
    extrMotor.runSpeed();

    

   }
  else if (toExtrude ==0)
  {
    // motor STOP spining
    extrMotor.moveTo(-500);
    while (extrMotor.currentPosition() !=0)
      extrMotor.run();
    extrMotor.stop();
    extrMotor.runToPosition();  
//    extrMotor.setSpeed(0);

    digitalWrite(relay_1, LOW);
    Serial.println("Motor is off");
  }


}
