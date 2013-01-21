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
-Read Analog and Digital sensor feedback and send to master

--ToDo: 
-Drive Servos with PWM out.
*/

#include "Arduino.h"
#include <digitalWriteFast.h>  // library for high performance reads and writes by jrraines
                               // see http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1267553811/0
                               // and http://code.google.com/p/digitalwritefast/
 
// It turns out that the regular digitalRead() calls are too slow and bring the arduino down when
// I use them in the interrupt routines while the motor runs at full speed.

// Serial
#define TIMEOUT 1000l
int inBytes = 0;
char buf[256];

// Quadrature encoders
// Left encoder
#define LeftEncoderIntA 0
#define LeftEncoderPinA 2
#define LeftEncoderPinB 4
#define LeftEncoderIsReversed

// Right encoder
#define RightEncoderIntA 1
#define RightEncoderPinA 3
#define RightEncoderPinB 5
#define RightEncoderIsReversed

//Motor Outputs
#define LMotorPWMPin 8
#define RMotorPWMPin 9
#define LMotorDirPin 22
#define RMotorDirPin 23

// Distance sensors
#define NSENSORS 5
#define SENSOR_0 0
#define SENSOR_1 1
#define SENSOR_2 2
#define SENSOR_3 3
#define SENSOR_4 4

int sensors[NSENSORS];
char sensorsToSend[NSENSORS*2];

int rIn = 0;
int lIn = 0;
int commandL;
int commandR;

volatile long leftEncoderTicks = 0;
volatile long rightEncoderTicks = 0;

char eV[8];

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
  attachInterrupt(LeftEncoderIntA, HandleLeftMotorInterrupt, CHANGE);
  // Right encoder
  pinMode(RightEncoderPinA, INPUT);      // sets pin A as input
  digitalWrite(RightEncoderPinA, LOW);  // turn on pullup resistors
  pinMode(RightEncoderPinB, INPUT);      // sets pin B as input
  digitalWrite(RightEncoderPinB, LOW);  // turn on pullup resistors
  attachInterrupt(RightEncoderIntA, HandleRightMotorInterrupt, CHANGE);  
}

void loop(){
  // Get information from sensors
  for(int i = 0; i < NSENSORS; ++i) {
    sensors[i] = analogRead(i);
    sensorsToSend[i*2] = (char)(sensors[i]>>8);
    sensorsToSend[i*2+1] = (char)(sensors[i]&0xFF);
  }
  // Get information from encoders
  writeEncoderVals();
  // Compile everything into one buffer
  for(int i = 0; i < 8; ++i) {
    buf[i] = eV[i];
  }
  for(int i = 0; i < NSENSORS*2; ++i) {
    buf[i+8] = sensorsToSend[i];
  }
  // Send information
  serSend(buf, NSENSORS*2+8);
  // Get and execute motor commands
  getMotorCommands();
  commandMotors(lIn, rIn);
}

// Serial library

// Waits for an 'S' byte (start byte), and then sends a confirmation it got the message.
void serReceive() {
  int cTime;
  while(Serial.read() != 'S');
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
  Serial.write('E');
}

// Tries to send until it gets a reply confirming it sent the message.
void serSend(char *msg, char length) {
  long cTime;
  Serial.write('S');
  Serial.write(length);
  for(char *i = msg; (i-msg) < length; ++i) {
    Serial.write(*i);
  }
  while(Serial.read() != 'E');
}

void getMotorCommands(){
  serReceive();
  if(inBytes == 4) {
    lIn = -1*(int)buf[0] + (int)buf[1];
    rIn = -1*(int)buf[2] + (int)buf[3];
  }
}

void commandMotors(int lCommand,int rCommand){
  digitalWrite(LMotorDirPin,dir(lCommand));
  digitalWrite(RMotorDirPin,dir(rCommand));
  analogWrite(LMotorPWMPin,abs(lCommand));
  analogWrite(RMotorPWMPin,abs(rCommand));
  //analogWrite(VacuumPWMPin,20);
}

void writeEncoderVals(){
  eV[0] = leftEncoderTicks>>24;
  eV[1] = (leftEncoderTicks>>16)&0xFF;
  eV[2] = (leftEncoderTicks>>8)&0xFF;
  eV[3] = leftEncoderTicks&0xFF;
  
  eV[4] = rightEncoderTicks>>24;
  eV[5] = (rightEncoderTicks>>16)&0xFF;
  eV[6] = (rightEncoderTicks>>8)&0xFF;
  eV[7] = rightEncoderTicks&0xFF;
}


// Interrupt service routines for the left motor's quadrature encoder
void HandleLeftMotorInterrupt(){
  // XOR ^: 0 if the same, 1 otherwise. Assuming they only take values in {0,1} (true for digitalReadFast)
  leftEncoderTicks -= 1 - 2*(digitalReadFast(LeftEncoderPinB)^digitalReadFast(LeftEncoderPinA));
}

void HandleRightMotorInterrupt(){
  // XOR ^: 0 if the same, 1 otherwise. Assuming they only take values in {0,1} (true for digitalReadFast)
  rightEncoderTicks -= 1 - 2*(digitalReadFast(RightEncoderPinB)^digitalReadFast(RightEncoderPinA));
}
