/*
MASLAB Team Hex Arduino 2560 Firmware
Daniel J. Gonzalez
dgonz@mit.edu
January 2013

Done: 
-Serial Communication with master. Baudrate: 1000000 (One Million)
-interrupt-driven quadrature decoding for two drive motors.
-Drive motors with PWM out

ToDo: 
-Drive Servos with PWM out.
-Read Analog and Digital sensor feedback and send to master
*/

#include "Arduino.h"
#include <digitalWriteFast.h>  // library for high performance reads and writes by jrraines
                               // see http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1267553811/0
                               // and http://code.google.com/p/digitalwritefast/
 
// It turns out that the regular digitalRead() calls are too slow and bring the arduino down when
// I use them in the interrupt routines while the motor runs at full speed.

// Quadrature encoders
// Left encoder
#define LeftEncoderIntA 0
#define LeftEncoderIntB 1
#define LeftEncoderPinA 2
#define LeftEncoderPinB 3
#define LeftEncoderIsReversed

// Right encoder
#define RightEncoderIntA 2
#define RightEncoderIntB 3
#define RightEncoderPinA 21
#define RightEncoderPinB 20
#define RightEncoderIsReversed

//Motor Outputs
#define LMotorPWMPin 8
#define RMotorPWMPin 9
#define LMotorDirPin 22
#define RMotorDirPin 23

int rIn = 0;
int lIn = 0;
int commandL;
int commandR;

volatile bool leftEncoderASet;
volatile bool leftEncoderBSet;
volatile bool leftEncoderAPrev;
volatile bool leftEncoderBPrev;
volatile long leftEncoderTicks = 0;

volatile bool rightEncoderASet;
volatile bool rightEncoderBSet;
volatile bool rightEncoderAPrev;
volatile bool rightEncoderBPrev;
volatile long rightEncoderTicks = 0;

unsigned char inByte = '0';

static int dir(int val) {
  if (val< 0) return 0;
  if (val>=0) return 1;
}

void setup(){
  Serial.begin(1000000);
  //establishContact();
  pinMode(LMotorDirPin,OUTPUT);
  pinMode(RMotorDirPin,OUTPUT);
  digitalWrite(LMotorDirPin,HIGH);
  digitalWrite(RMotorDirPin,LOW);
  int commandL = 0;
  int commandR = 0;
   
  // Quadrature encoders
  // Left encoder
  pinMode(LeftEncoderPinA, INPUT);      // sets pin A as input
  digitalWrite(LeftEncoderPinA, LOW);  // turn on pullup resistors
  pinMode(LeftEncoderPinB, INPUT);      // sets pin B as input
  digitalWrite(LeftEncoderPinB, LOW);  // turn on pullup resistors
  attachInterrupt(LeftEncoderIntA, HandleLeftMotorInterruptA, CHANGE);
  attachInterrupt(LeftEncoderIntB, HandleLeftMotorInterruptB, CHANGE);
  
  // Right encoder
  pinMode(RightEncoderPinA, INPUT);      // sets pin A as input
  digitalWrite(RightEncoderPinA, LOW);  // turn on pullup resistors
  pinMode(RightEncoderPinB, INPUT);      // sets pin B as input
  digitalWrite(RightEncoderPinB, LOW);  // turn on pullup resistors
  attachInterrupt(RightEncoderIntA, HandleRightMotorInterruptA, CHANGE);
  attachInterrupt(RightEncoderIntB, HandleRightMotorInterruptB, CHANGE);
}

void loop(){
  serRead();
  commandL = map(lIn,0,255,-255,255);
  commandR = map(rIn,0,255,-255,255);
  commandMotors(commandL, commandR);
}

void establishContact() {
  while (Serial.available() <= 0) {
    Serial.print('A');   // send a capital A
    delay(300);
  }
}

void serRead(){
  while((inByte = Serial.read()) != 'S');
  while(!Serial.available());
  lIn = (int)Serial.read();
  while(!Serial.available());
  rIn = (int)Serial.read();
  while(!Serial.available());
  if((inByte = Serial.read()) == 'E') {
    return;
  }
}

void writeEncoderVals(){
  Serial.print("S");//Start byte. Line dropped if not present
  Serial.print(rightEncoderTicks);
  Serial.print(",");//All data separated by commas
  Serial.print(leftEncoderTicks);
  Serial.println("E");
}

void commandMotors(int lCommand,int rCommand){
  digitalWrite(LMotorDirPin,dir(lCommand));
  digitalWrite(RMotorDirPin,dir(rCommand));
  analogWrite(LMotorPWMPin,abs(lCommand));
  analogWrite(RMotorPWMPin,abs(rCommand));
}

// Interrupt service routines for the left motor's quadrature encoder
void HandleLeftMotorInterruptA(){
  leftEncoderBSet = digitalReadFast(LeftEncoderPinB);
  leftEncoderASet = digitalReadFast(LeftEncoderPinA);
  
  leftEncoderTicks+=ParseEncoderLeft();
  
  leftEncoderAPrev = leftEncoderASet;
  leftEncoderBPrev = leftEncoderBSet;
}
 
// Interrupt service routines for the right motor's quadrature encoder
void HandleLeftMotorInterruptB(){
  // Test transition;
  leftEncoderBSet = digitalReadFast(LeftEncoderPinB);
  leftEncoderASet = digitalReadFast(LeftEncoderPinA);
  
  leftEncoderTicks+=ParseEncoderLeft();
  
  leftEncoderAPrev = leftEncoderASet;
  leftEncoderBPrev = leftEncoderBSet;
}

int ParseEncoderLeft(){
  if(leftEncoderAPrev && leftEncoderBPrev){
    if(!leftEncoderASet && leftEncoderBSet) return 1;
    if(leftEncoderASet && !leftEncoderBSet) return -1;
  }else if(!leftEncoderAPrev && leftEncoderBPrev){
    if(!leftEncoderASet && !leftEncoderBSet) return 1;
    if(leftEncoderASet && leftEncoderBSet) return -1;
  }else if(!leftEncoderAPrev && !leftEncoderBPrev){
    if(leftEncoderASet && !leftEncoderBSet) return 1;
    if(!leftEncoderASet && leftEncoderBSet) return -1;
  }else if(leftEncoderAPrev && !leftEncoderBPrev){
    if(leftEncoderASet && leftEncoderBSet) return 1;
    if(!leftEncoderASet && !leftEncoderBSet) return -1;
  }
}

// Interrupt service routines for the right motor's quadrature encoder
void HandleRightMotorInterruptA(){
  rightEncoderBSet = digitalReadFast(RightEncoderPinB);
  rightEncoderASet = digitalReadFast(RightEncoderPinA);
  
  rightEncoderTicks+=ParseEncoderright();
  
  rightEncoderAPrev = rightEncoderASet;
  rightEncoderBPrev = rightEncoderBSet;
}
 
// Interrupt service routines for the right motor's quadrature encoder
void HandleRightMotorInterruptB(){
  // Test transition;
  rightEncoderBSet = digitalReadFast(RightEncoderPinB);
  rightEncoderASet = digitalReadFast(RightEncoderPinA);
  
  rightEncoderTicks+=ParseEncoderright();
  
  rightEncoderAPrev = rightEncoderASet;
  rightEncoderBPrev = rightEncoderBSet;
}

int ParseEncoderright(){
  if(rightEncoderAPrev && rightEncoderBPrev){
    if(!rightEncoderASet && rightEncoderBSet) return 1;
    if(rightEncoderASet && !rightEncoderBSet) return -1;
  }else if(!rightEncoderAPrev && rightEncoderBPrev){
    if(!rightEncoderASet && !rightEncoderBSet) return 1;
    if(rightEncoderASet && rightEncoderBSet) return -1;
  }else if(!rightEncoderAPrev && !rightEncoderBPrev){
    if(rightEncoderASet && !rightEncoderBSet) return 1;
    if(!rightEncoderASet && rightEncoderBSet) return -1;
  }else if(rightEncoderAPrev && !rightEncoderBPrev){
    if(rightEncoderASet && rightEncoderBSet) return 1;
    if(!rightEncoderASet && !rightEncoderBSet) return -1;
  }
}
