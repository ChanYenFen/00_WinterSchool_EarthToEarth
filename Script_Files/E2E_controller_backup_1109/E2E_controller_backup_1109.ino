#include "config.h"

int toExtrude = -1;

void setup() {
  Serial.begin(115200);

  // Dclare pins as output:
  pinMode(dirPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
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
    digitalWrite(dirPin, LOW);
    
    for (int i=0; i < 200; i++)
    {
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(500);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(500);
    }
   }
  else if (toExtrude ==0)
  {
//    // implement retraction here for the moment
//    digitalWrite(relay_1, HIGH);
//    digitalWrite(dirPin,HIGH);
//    for (int i=0; i < 2; i++)
//    {
//      digitalWrite(stepPin, HIGH);
//      delayMicroseconds(500);
//      digitalWrite(stepPin, LOW);
//      delayMicroseconds(500);
//    }
//    
    // motor STOP spining
    digitalWrite(relay_1, LOW);
    Serial.println("Motor is off");
  }


}
