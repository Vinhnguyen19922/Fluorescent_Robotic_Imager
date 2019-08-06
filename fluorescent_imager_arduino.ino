#include <Servo.h>

int sheetPin = 19;
int laserPin = 18;
int fanPin = 14;
int UVPin = 12;
Servo filterServo;
Servo loadServoLeft; // Attached to the leftmost servo pin set, pin10
Servo loadServoRight; // Attached to the rightmost servo pin set, pin9

boolean lights = false;

void setup() {
  
  Serial.begin(9600);
  while (!Serial) {
    ;
  }
  
  pinMode(sheetPin, OUTPUT);
  pinMode(laserPin, OUTPUT);
  pinMode(fanPin, OUTPUT);
  pinMode(UVPin, OUTPUT);
  establishContact();

}

void loop() {


  if (Serial.available()) {
    char inChar = char(Serial.read());

    //----------------------------------------------------------
    // Controls for ELS and laser
    
    if (inChar == 'a') {
      lights = true;
    }
    else if (inChar == 'b') {
      lights = false;
      digitalWrite(sheetPin, LOW);
    }
    else if (inChar == 'c') {
      digitalWrite(laserPin, HIGH);
    }
    else if (inChar == 'd') {
      digitalWrite(laserPin, LOW);
    }

    //----------------------------------------------------------------------
    // Controls for filter wheel
    
    else if (inChar == 'e') {
      filterServo.attach(15);
      filterServo.write(90);
      delay(1000);
      filterServo.detach();
    }
    else if (inChar == 'f') {
      filterServo.attach(15);
      filterServo.write(40);
      delay(1000);
      filterServo.detach();
    }
    else if (inChar == 'g') {
      filterServo.attach(15);
      filterServo.write(180);
      delay(1000);
      filterServo.detach();
    }
    //-------------------------------------------------------------
    // Controls for loading panel servos
    
    // Because servos are strange creatures,
    // the right motor of the load door has the
    // following angles:
    // CLOSED: 80 degrees
    // OPEN: 5 degrees
    
    else if (inChar == 'h') {
      loadServoLeft.attach(10);

      for(int i = 85; i >= 10; i-=3) {
        loadServoRight.write(i);
        loadServoLeft.write(170-i);
        delay(30);
      }
      loadServoRight.write(5);
      loadServoLeft.write(174);
      delay(40);
      loadServoRight.detach();
      loadServoLeft.detach();
    }
    else if (inChar == 'i') {
      loadServoRight.attach(9);
      loadServoLeft.attach(10);
      loadServoRight.write(85);
      loadServoLeft.write(89);
      delay(1000);
      //loadServoRight.detach();
      loadServoRight.write(78);
      loadServoLeft.detach();
    }

    //----------------------------------------------------------------------
    // Controls for fans

    else if (inChar =='j') {
      digitalWrite(fanPin, HIGH);
    }
    else if (inChar =='k') {
      digitalWrite(fanPin, LOW);
    }

    //----------------------------------------------------------------------
    // Controls for UV LED
    
    else if (inChar == 'm') {
      digitalWrite(UVPin, HIGH);
    }
    else if (inChar == 'n') {
      digitalWrite(UVPin, LOW);
    }
  } 

  if (lights) {
    digitalWrite(sheetPin, HIGH);
    //delay(30);
    //digitalWrite(sheetPin, LOW);
    //delay(1);
  }


}

void establishContact() {
  while (Serial.available() <= 0) {
    Serial.println("Hey!");
    delay(300);
  }
}
