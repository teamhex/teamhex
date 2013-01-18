#ifndef MOTION_PLANNER_H
#define MOTION_PLANNER_H

extern Position *plan[HEIGHT*WIDTH];
extern int planLength;

void wallExpand(int l, int c, int radius);
void setConfigurationSpace();
bool makePlan(Position &start, Position &goal);
bool isLineClear(Position &start, Position &end);
void smoothPlan();

#endif
