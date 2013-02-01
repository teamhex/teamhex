#ifndef MOTION_PLANNER_H
#define MOTION_PLANNER_H

#include "bayesianGrid.h"

#define smoothSLACK 4
#define planSLACK 5

class Condition {
 public:
  virtual bool operator ()(Cell &c) = 0;
};

class BallCond: public Condition {
 public:
  bool operator ()(Cell &c);
};

class UnvisitedCond: public Condition {
 public:
  bool operator ()(Cell &c);
};

extern int configMap[HEIGHT][WIDTH];
extern Position *plan[HEIGHT*WIDTH];
extern int planLength;

void startPlanning();
void wallExpand(int l, int c, int radius);
void setConfigurationSpace();
bool makePlan(Position &start, Position &goal);
bool isLineClear(Position &start, Position &end);
void smoothPlan();
Position *findClosest(RealPosition &robotPos, Condition &cond);

#endif
