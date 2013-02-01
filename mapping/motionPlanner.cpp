#include "bayesianGrid.h"
#include "motionPlanner.h"
#include <string.h>

int configMap[HEIGHT][WIDTH];
Position *plan[HEIGHT*WIDTH];
int planLength;
static Position *queue[HEIGHT*WIDTH];
static int queueFront,queueBack;
static int operationID;
static int visited[HEIGHT][WIDTH];

void startPlanning() {
  operationID = 0;
  memset(visited,0,sizeof(int)*WIDTH*HEIGHT);
}

void wallExpand(int l, int c, int radius) {
  double dist;
  Position start;
  Position *cur;
  start.l = l;
  start.c = c;
  
  int nNeighbors;
  Position **neighbors;

  ++operationID;
  visited[l][c] = operationID;

  queueFront = queueBack = 0;
  queue[queueBack++] = &start;;

  while(queueBack > queueFront) {
    cur = queue[queueFront++];

    nNeighbors = allnNeighbors[cur->l][cur->c];
    neighbors= allNeighbors[cur->l][cur->c];

    dist = distanceSqr(start,*cur);

    if(dist <= (radius+smoothSLACK)*(radius+smoothSLACK)) {
      configMap[cur->l][cur->c] = 2;
    }
    else if(dist <= (radius+planSLACK)*(radius+planSLACK)) {
      configMap[cur->l][cur->c] = 1;
    }

    for(int i = 0; i < nNeighbors; ++i) {
      if(visited[neighbors[i]->l][neighbors[i]->c] != operationID) {
	visited[neighbors[i]->l][neighbors[i]->c] = operationID;
	if(distanceSqr(start, *neighbors[i]) <= (radius+planSLACK)*(radius+planSLACK)) {
	  queue[queueBack++] = neighbors[i];
	}
      }
    }
  }
}

void setConfigurationSpace() {
  memset(configMap, 0, sizeof(int)*HEIGHT*WIDTH);
  for(int l = 0; l < HEIGHT; ++l) {
    for(int c = 0; c < WIDTH; ++c) {
      if(isWall(theMap[l][c])) {
	wallExpand(l,c,ROBOT_RADIUS);
      }
    }
  }
}

#include <stdio.h>

bool makePlan(Position &start, Position &goal) {
  Position **neighbors;
  int nNeighbors;
  Position *cur;

  double minDist,d;

  planLength = 0;
  
  // Start or goal blocked
  if(configMap[start.l][start.c] || configMap[goal.l][goal.c]) {
    printf("Should not happen\n");
    return false;
  }
  ++operationID;
  cur = new Position();
  cur->l = start.l;
  cur->c = start.c;

  while(cur != NULL) {
    visited[cur->l][cur->c] = operationID;
    minDist = -1;
    
    plan[planLength++] = cur;
    if(cur->l == goal.l && cur->c == goal.c) {
      printf("A plan exists ...\n");
      return true;
    }
    
    neighbors = allNeighbors[cur->l][cur->c];
    nNeighbors = allnNeighbors[cur->l][cur->c];

    cur = NULL;

    for(int i = 0; i < nNeighbors; ++i) {
      d = distanceSqr(goal, *neighbors[i]);
      if((!configMap[neighbors[i]->l][neighbors[i]->c]) &&
	 visited[neighbors[i]->l][neighbors[i]->c] != operationID &&
	 (minDist == -1 || d < minDist)) {
        minDist = d;
	cur = neighbors[i];
      }
    }
  }
  planLength = 0;
  return false;
}

bool isLineClear(Position &start, Position &end) {
  Position **neighbors;
  int nNeighbors;
  Position *cur = &start;
  double minDist = distanceSqr(start, end),d;

  do {
    if(configMap[cur->l][cur->c] >= 2) {
      return false;
    }
    neighbors = allNeighbors[cur->l][cur->c];
    nNeighbors = allnNeighbors[cur->l][cur->c];

    cur = NULL;

    for(int i = 0; i < nNeighbors; ++i) {
      d = distanceSqr(start, *neighbors[i]);
      if(d < minDist) {
	minDist = d;
	cur = neighbors[i];
      }
    }
  } while(cur != NULL);
  return true;
}

void smoothPlan() {
  if(planLength <= 2) {
    return;
  }
  Position *cur = plan[0];
  int nextPointInd = 1;
  for(int i = 2; i < planLength; ++i) {
    if(!isLineClear(*cur,*plan[i])) {
      cur = plan[i-1];
      plan[nextPointInd++] = cur;
    }
  }
  plan[nextPointInd++] = plan[planLength-1];
  planLength = nextPointInd;
}

Position *findClosest(RealPosition &robotPos, Condition &cond) {  
  int nNeighbors;
  Position **neighbors;
  Position *cur;

  Position start = realToGrid(robotPos);

  ++operationID;
  visited[start.l][start.c] = operationID;

  queueFront = queueBack = 0;
  queue[queueBack++] = &start;

  while(queueBack > queueFront) {
    cur = queue[queueFront++];

    nNeighbors = allnNeighbors[cur->l][cur->c];
    neighbors = allNeighbors[cur->l][cur->c];

    for(int i = 0; i < nNeighbors; ++i) {
      if(visited[neighbors[i]->l][neighbors[i]->c] != operationID &&
	 !configMap[neighbors[i]->l][neighbors[i]->c]) {
	if(cond(theMap[neighbors[i]->l][neighbors[i]->c])) {
	  return neighbors[i];
	}
	if(distanceSqr(start, *neighbors[i]) <= FIELD_DIAMETER*FIELD_DIAMETER) {
	  visited[neighbors[i]->l][neighbors[i]->c] = operationID;
	  queue[queueBack++] = neighbors[i];
	}
      }
    }
  }
  return NULL;
}

bool BallCond::operator ()(Cell &c) {
  return isBall(c);
}

bool UnvisitedCond::operator ()(Cell &c) {
  return !c.visited;
}
