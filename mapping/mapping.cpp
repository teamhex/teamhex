#include "motionPlanner.h"
#include "bayesianGrid.h"
#include "mapping.h"
#include <stdio.h>

RealPosition robotPosition;

void initMapping() {
  initialize();
  startPlanning();
}

void robotPositioned(double robotX, double robotY) {
  robotPosition.x = robotX;
  robotPosition.y = robotY;
  sensorUpdate(ROBOT_BODY, false, robotPosition, robotPosition);
}

void wallDetected(double wallX, double wallY) {
  RealPosition wallPos;
  wallPos.x = wallX;
  wallPos.y = wallY;
  sensorUpdate(NORMAL_WALL, true, wallPos, robotPosition);
}

void wallNotDetected(double sensorLimitX, double sensorLimitY) {
  RealPosition wallPos;
  wallPos.x = sensorLimitX;
  wallPos.y = sensorLimitY;
  sensorUpdate(NORMAL_WALL, false, wallPos, robotPosition);
}

void ballDetected(double ballX, double ballY, int ballColor) {
  RealPosition ballPos;
  ballPos.x = ballX;
  ballPos.y = ballY;
  sensorUpdate(ballColor, true, ballPos, robotPosition);
}

void specialWall(double wallX, double wallY, int wallType) {
  RealPosition wallPos;
  wallPos.x = wallX;
  wallPos.y = wallY;
  setWallType(wallType, wallPos, robotPosition);
}

void closestBall(CPosition *res) {
  BallCond bc;
  Position *r = findClosest(robotPosition,bc);
  if(r == NULL) {
    res->x = -1;
    res->y = -1;
  }
  else {
    RealPosition realBall = gridToReal(*r);
    res->x = realBall.x;
    res->y = realBall.y;
  }
}

void closestUnvisited(CPosition *res) {
  UnvisitedCond uc;
  Position *r = findClosest(robotPosition, uc);
  if(r == NULL) {
    res->x = -1;
    res->y = -1;
  }
  else {
    RealPosition realUnvisited = gridToReal(*r);
    res->x = realUnvisited.x;
    res->y = realUnvisited.y;
  }
}

void setConfigSpace() {
  setConfigurationSpace();
}

void goPlan(double goalX, double goalY) {
  RealPosition goal;
  goal.x = goalX;
  goal.y = goalY;
  Position goalPos = realToGrid(goal);
  Position startPos = realToGrid(robotPosition);
  makePlan(startPos, goalPos);
  smoothPlan();
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
  else {
    WP->x = -1;
    WP->y = -1;
  }
}

void printCells() {
  printMap();
}

int getConfigWall(int x, int y) {
  RealPosition realPos = {x,y};
  Position gridPos = realToGrid(realPos);
  return (int)configMap[gridPos.l][gridPos.c];
}

int getWall(int x, int y) {
  RealPosition realPos = {x,y};
  Position gridPos = realToGrid(realPos);
  return (int)isWall(theMap[gridPos.l][gridPos.c]);
}

int getWallType(int x, int y) {
  RealPosition realPos = {x,y};
  Position gridPos = realToGrid(realPos);
  if(!isWall(theMap[gridPos.l][gridPos.c])) {
    return -1;
  }
  else {
    return theMap[gridPos.l][gridPos.c].wallType;
  }
}

int getBall(int x, int y) {
  RealPosition realPos = {x,y};
  Position gridPos = realToGrid(realPos);
  return (int)isBall(theMap[gridPos.l][gridPos.c]);
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
