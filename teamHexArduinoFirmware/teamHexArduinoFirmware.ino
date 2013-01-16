/*
MASLAB Team Hex Arduino 2560 Firmware
Daniel J. Gonzalez
dgonz@mit.edu
January 2013

---Wire connections---
-Motor Controller:
5V to 5V
GND to GND
PWM1 to 8
DIR1 to 22
PWM2 to 9
DIR2 to 23
-Left Motor:
Connector to Motor controller plug 1
Encoder black to 5V
Encoder lime to GND
Encoder red to 2
Encoder white to 3
-Right Motor:
Connector to Motor controller plug 1
Encoder black to 5V
Encoder lime to GND
Encoder red to 21
Encoder white to 20


--Done: 
-Serial Communication with master. Baudrate: 1000000 (One Million)
-interrupt-driven quadrature decoding for two drive motors.
-Drive motors with PWM out

--ToDo: 
-Drive Servos with PWM out.
-Read Analog and Digital sensor feedback and send to master
*/

#include "Arduino.h"
#include <digitalWriteFast.h>  // library for high performance reads and writes by jrraines
                               // see http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1267553811/0
                               // and http://code.google.com/p/digitalwritefast/
 
// It turns out that the regular digitalRead() calls are too slow and bring the arduino down when
// I use them in the interrupt routines while the motor runs at full speed.

// Serial
#define TIMEOUT 1000
int inBytes = 0;
char buf[256];

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

volatile long leftEncoderTicks = 0;
volatile long rightEncoderTicks = 0;

unsigned char inByte = '0';

static int dir(int val) {
  if (val< 0) return 0;
  if (val>=0) return 1;
}

void setup(){
  Serial.begin(1000000);
  
  // Motors
  pinMode(LMotorDirPin,OUTPUT);
  pinMode(RMotorDirPin,OUTPUT);
  digitalWrite(LMotorDirPin,HIGH);
  digitalWrite(RMotorDirPin,LOW);
  commandL = 0;
  commandR = 0;
  
  
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
  writeEncoderVals();
  //getMotorCommands();
  //serReceive();
  //serSend(buf, inBytes);
  //commandL = lIn;
  //commandR = rIn;
  //commandMotors(commandL, commandR);
} 

void serReceive() {
  int cTime;
  
  Serial.write('R');
  while((inByte = Serial.read()) != 'S');
  cTime = micros();
  while(!Serial.available() && (micros()-cTime) < TIMEOUT);
  if(!Serial.available()) {
    inBytes = 0;
  }
  else {
    inBytes = (int) Serial.read();
  }
  Serial.setTimeout((TIMEOUT*inBytes)/1000);
  Serial.readBytes(buf, inBytes);
}

// Tries to send until it gets a reply confirming it sent the message.
void serSend(char *msg, char length) {
  //int cTime;
  //bool replied = false;
  //while(!replied) {
  while(Serial.read() != 'R');
  Serial.write('S');
  Serial.write(length);
  for(char *i = msg; (i-msg) < length; ++i) {
    Serial.write(*i);
  }
  while(Serial.read() != 'E');
    //cTime = micros();
    //while(!Serial.available() && (micros()-cTime) < TIMEOUT);
    //if(Serial.available() && Serial.read() == 'E') {
      //replied = true;
    //}
  //}
}

// Tries to read a message. Blocks until it gets an S.
void serRead(){
  while((inByte = Serial.read()) != 'S');
  while(!Serial.available());
  int lIn1 = -1*(int)Serial.read();
  while(!Serial.available());
  int lIn2 = (int)Serial.read();
  lIn = lIn1+lIn2;
  while(!Serial.available());
  int rIn1 = -1*(int)Serial.read();
  while(!Serial.available());
  int rIn2 = (int)Serial.read();
  rIn = rIn1+rIn2;
  //while(!Serial.available());
}

void getMotorCommands(){
  serReceive();
}

void writeEncoderVals(){
  char eV[8];
  char le1,le2,le3,le4,re1,re2,re3,re4;
  eV[0] = leftEncoderTicks>>24;
  eV[1] = (leftEncoderTicks>>16)&0xFF;
  eV[2] = (leftEncoderTicks>>8)&0xFF;
  eV[3] = leftEncoderTicks&0xFF;
  
  eV[4] = rightEncoderTicks>>24;
  eV[5] = (rightEncoderTicks>>16)&0xFF;
  eV[6] = (rightEncoderTicks>>8)&0xFF;
  eV[7] = rightEncoderTicks&0xFF;

  serSend(eV, 8);
}

void commandMotors(int lCommand,int rCommand){
  digitalWrite(LMotorDirPin,dir(lCommand));
  digitalWrite(RMotorDirPin,dir(rCommand));
  analogWrite(LMotorPWMPin,abs(lCommand));
  analogWrite(RMotorPWMPin,abs(rCommand));
}

// Interrupt service routines for the left motor's quadrature encoder
void HandleLeftMotorInterruptA(){
  // XOR ^: 0 if the same, 1 otherwise. Assuming they only take values in {0,1} (true for digitalReadFast)
  leftEncoderTicks -= 1 - 2*(digitalReadFast(LeftEncoderPinB)^digitalReadFast(LeftEncoderPinA));
}
 
void HandleLeftMotorInterruptB(){
  // XOR ^: 0 if the same, 1 otherwise. Assuming they only take values in {0,1} (true for digitalReadFast)
  leftEncoderTicks += 1 - 2*(digitalReadFast(LeftEncoderPinB)^digitalReadFast(LeftEncoderPinA));
}

void HandleRightMotorInterruptA(){
  // XOR ^: 0 if the same, 1 otherwise. Assuming they only take values in {0,1} (true for digitalReadFast)
  rightEncoderTicks += 1 - 2*(digitalReadFast(RightEncoderPinB)^digitalReadFast(RightEncoderPinA));
}
 
void HandleRightMotorInterruptB(){
  // XOR ^: 0 if the same, 1 otherwise. Assuming they only take values in {0,1} (true for digitalReadFast)
  rightEncoderTicks -= 1 - 2*(digitalReadFast(RightEncoderPinB)^digitalReadFast(RightEncoderPinA));
}
