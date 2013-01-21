#include <digitalWriteFast.h>  // library for high performance reads and writes by jrraines
                               // see http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1267553811/0
                               // and http://code.google.com/p/digitalwritefast/
 
// It turns out that the regular digitalRead() calls are too slow and bring the arduino down when
// I use them in the interrupt routines while the motor runs at full speed.

// Quadrature encoders
// Left encoder
#define LeftEncoderIntA 0
#define LeftEncoderPinA 2
#define LeftEncoderPinB 4
#define LeftEncoderPinAOutput 6
#define LeftEncoderPinBOutput 7
#define LeftEncoderIsReversed

// Right encoder
#define RightEncoderIntA 1
#define RightEncoderPinA 3
#define RightEncoderPinB 5
#define RightEncoderPinAOutput 8
#define RightEncoderPinBOutput 9
#define RightEncoderIsReversed

#define DivisionFactor 5

volatile long leftEncoderTicks = 0;
volatile long rightEncoderTicks = 0;
volatile char leftPinA = 1;
volatile char rightPinA = 1;

void setup(){
  // Encoder output
  pinMode(LeftEncoderPinAOutput, OUTPUT);
  pinMode(LeftEncoderPinBOutput, OUTPUT);
  pinMode(RightEncoderPinAOutput, OUTPUT);
  pinMode(RightEncoderPinBOutput, OUTPUT);
  digitalWrite(LeftEncoderPinAOutput, LOW);
  digitalWrite(LeftEncoderPinBOutput, LOW);
  digitalWrite(RightEncoderPinBOutput, LOW);
  digitalWrite(RightEncoderPinAOutput, LOW);

  // Quadrature encoders
  // Left encoder
  pinMode(LeftEncoderPinA, INPUT);      // sets pin A as input
  digitalWrite(LeftEncoderPinA, LOW);  // turn on pullup resistors
  pinMode(LeftEncoderPinB, INPUT);      // sets pin B as input
  digitalWrite(LeftEncoderPinB, LOW);  // turn on pullup resistors
  attachInterrupt(LeftEncoderIntA, HandleLeftMotorInterrupt, RISING);
  // Right encoder
  pinMode(RightEncoderPinA, INPUT);      // sets pin A as input
  digitalWrite(RightEncoderPinA, LOW);  // turn on pullup resistors
  pinMode(RightEncoderPinB, INPUT);      // sets pin B as input
  digitalWrite(RightEncoderPinB, LOW);  // turn on pullup resistors
  attachInterrupt(RightEncoderIntA, HandleRightMotorInterrupt, RISING);
}

void loop(){
}

// Interrupt service routines for the left motor's quadrature encoder
void HandleLeftMotorInterrupt(){
  // XOR ^: 0 if the same, 1 otherwise. Assuming they only take values in {0,1} (true for digitalReadFast)
  leftEncoderTicks -= 1 - 2*(digitalReadFast(LeftEncoderPinB)^digitalReadFast(LeftEncoderPinA));
  if(leftEncoderTicks == DivisionFactor) {
    leftPinA ^= 1;
    digitalWriteFast(LeftEncoderPinBOutput, leftPinA^1);
    digitalWriteFast(LeftEncoderPinAOutput, leftPinA);
    leftEncoderTicks = 0;
  }
  else if(leftEncoderTicks == -DivisionFactor) {
    leftPinA ^= 1;
    digitalWriteFast(LeftEncoderPinBOutput, leftPinA);
    digitalWriteFast(LeftEncoderPinAOutput, leftPinA);
    leftEncoderTicks = 0;
  }
}

void HandleRightMotorInterrupt(){
  // XOR ^: 0 if the same, 1 otherwise. Assuming they only take values in {0,1} (true for digitalReadFast)
  rightEncoderTicks += 1 - 2*(digitalReadFast(RightEncoderPinB)^digitalReadFast(RightEncoderPinA));
  if(rightEncoderTicks == DivisionFactor) {
    rightPinA ^= 1;
    digitalWriteFast(RightEncoderPinBOutput, rightPinA^1);
    digitalWriteFast(RightEncoderPinAOutput, rightPinA);
    rightEncoderTicks = 0;
  }
  else if(rightEncoderTicks == -DivisionFactor) {
    rightPinA ^= 1;
    digitalWriteFast(RightEncoderPinBOutput, rightPinA);
    digitalWriteFast(RightEncoderPinAOutput, rightPinA);
    rightEncoderTicks = 0;
  }
}
