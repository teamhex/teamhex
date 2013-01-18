#include "bayesianGrid.h"

bool configMap[HEIGHT][WIDTH];
Position *plan[HEIGHT*WIDTH];
int planLength;

void wallExpand(int l, int c, int radius) {
  Position start;
  Position *cur;
  start.l = l;
  start.c = c;
  
  int nNeighbors;
  Position **neighbors;

  memset(visited, false, HEIGHT*WIDTH*sizeof(bool));
  visited[l][c] = true;

  queueFront = queueBack = 0;
  queue[queueBack++] = &start;;

  while(queueBack > queueFront) {
    cur = queue[queueFront++];

    nNeighbors = allnNeighbors[cur->l][cur->c];
    neighbors= allNeighbors[cur->l][cur->c];

    configMap[cur->l][cur->c] = true;

    for(int i = 0; i < nNeighbors; ++i) {
      if(!visited[neighbors[i]->l][neighbors[i]->c]) {
	visited[neighbors[i]->l][neighbors[i]->c] = true;
	if(distanceSqr(start, *neighbors[i]) <= radius*radius) {
	  queue[queueBack++] = neighbors[i];
	}
      }
    }
  }
}

void setConfigurationSpace(struct Cell *bayesianMap) {
  memset(configMap, false, sizeof(bool)*HEIGHT*WIDTH);
  for(int l = 0; l < HEIGHT; ++l) {
    for(int c = 0; c < WIDTH; ++c) {
      if(isWall(bayesianMap[l][c])) {
	wallExpand(l,c,ROBOT_RADIUS);
      }
    }
  }
}

bool makePlan(Position &start, Position &goal) {
  Position **neighbors;
  int nNeighbors;
  Position *cur;

  double minDist;
  
  // Start or goal blocked
  if(configMap[start.l][start.c] || configMap[goal.l][goal.c]) {
    return false;
  }
  memset(visited, false, HEIGHT*WIDTH*sizeof(bool));
  Position *cur = new Position();
  cur->l = start.l;
  cur->c = start.c;

  while(cur != NULL) {
    minDist = -1;
    
    plan[planLength++] = cur;
    visited[cur->l][cur->c] = true;
    if(cur->l == goal.l && cur->c == goal.c) {
      return true;
    }
    
    neighbors = allNeighbors[cur->l][cur->c];
    nNeighbors = allnNeighbors[cur->l][cur->c];

    cur = NULL;

    for(int i = 0; i < nNeighbors; ++i) {
      d = distanceSqr(goal, *neihbors[i]);
      if(!visited[neighbors[i]->l][neighbors[i]->c] && (minDist == -1 || d < minDist)) {
        d = minDist;
	cur = neighbors[i];
      }
    }
  }
  delete cur;
  return false;
}

bool isLineClear(Position &start, Position &end) {
  Position **neighbors;
  int nNeighbors;
  Position *cur = &start;
  double minDist = distanceSqr(start, end);

  do {
    if(configMap[cur->l][cur->c]) {
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
