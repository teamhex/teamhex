#include "bayesianGrid.h"
#include "motionPlanner.h"
#include "mapping.h"
#include <stdio.h>

RealPosition robotPosition;

void initMapping() {
  initialize();
}

void robotPositioned(int robotX, int robotY) {
  robotPosition.x = robotX;
  robotPosition.y = robotY;
  sensorUpdate(ROBOT_BODY, false, robotPosition, robotPosition);
}

void wallDetected(int wallX, int wallY) {
  RealPosition wallPos;
  wallPos.x = wallX;
  wallPos.y = wallY;
  sensorUpdate(NORMAL_WALL, true, wallPos, robotPosition);
}

void wallNotDetected(int sensorLimitX, int sensorLimitY) {
  RealPosition wallPos;
  wallPos.x = sensorLimitX;
  wallPos.y = sensorLimitY;
  sensorUpdate(NORMAL_WALL, false, wallPos, robotPosition);
}

void ballDetected(int ballX, int ballY, int ballColor) {
  RealPosition ballPos;
  ballPos.x = ballX;
  ballPos.y = ballY;
  sensorUpdate(ballColor, true, ballPos, robotPosition);
}

void specialWall(int wallX, int wallY, int wallType) {
  RealPosition wallPos;
  wallPos.x = wallX;
  wallPos.y = wallY;
  setWallType(wallType, wallPos, robotPosition);
}

void closestBall(CPosition *res) {
  Position *r = findClosestBall(robotPosition);
  if(r == NULL) {
    res->x = robotPosition.x;
    res->y = robotPosition.y;
  }
  else {
    RealPosition realBall = gridToReal(*r);
    res->x = realBall.x;
    res->y = realBall.y;
  }
}

void setConfigSpace() {
  setConfigurationSpace();
}

void makePlan(int goalX, int goalY) {
  RealPosition goal;
  goal.x = goalX;
  goal.y = goalY;
  Position goalPos = realToGrid(goal);
  Position startPos = realToGrid(robotPosition);
  makePlan(startPos, goalPos);
}

int getPlanLength() {
  return planLength;
}

void getPlanWP(int wpI, CPosition *WP) {
  if(wpI < planLength) {
    RealPosition pos = gridToReal(*plan[wpI]);
    WP->x = pos.x;
    WP->y = pos.y;
  }
}

void printCells() {
  printMap();
}

// int main() {
//   char command;
//   RealPosition robotPos, hitPos;
//   CPosition res;
//   initMapping();
//   for(;;) {
//     printMap();
//     scanf("%c %lf %lf %lf %lf", &command, &robotPos.x, &robotPos.y, &hitPos.x, &hitPos.y);
//     while(command == '\n') {
//       scanf("%c %lf %lf %lf %lf", &command, &robotPos.x, &robotPos.y, &hitPos.x, &hitPos.y);
//     }
//     if(command == 'n') {
//       continue;
//     }
//     robotPositioned(robotPos.x, robotPos.y);
//     switch(command) {
//     case 'q':
//       return 0;
//     case 'w':
//       wallDetected(hitPos.x, hitPos.y);
//       break;
//     case 'r':
//       ballDetected(hitPos.x, hitPos.y, RED_BALL);
//       break;
//     case 'g':
//       ballDetected(hitPos.x, hitPos.y, GREEN_BALL);
//       break;
//     default:
//       break;
//     }
//     closestBall(&res);
//   }
// }
