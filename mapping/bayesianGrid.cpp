#include "bayesianGrid.h"
#include <string.h>
#include <stdio.h>

Cell theMap[HEIGHT][WIDTH];
Position *queue[HEIGHT*WIDTH];
int queueFront, queueBack;
bool visited[HEIGHT][WIDTH];

Position *allNeighbors[HEIGHT][WIDTH][NNEIGHBORS];
int allnNeighbors[HEIGHT][WIDTH];

Position::Position(): l(-1),c(-1) {}
Position::Position(int line, int column): l(line),c(column) {}

double bayesianUpdate(double prior, double pDGivenX, double pDGivenNX, bool dHappened) {
  double pXAndEvent, pNXAndEvent;
  if(dHappened) {
    pXAndEvent = prior*pDGivenX;
    pNXAndEvent = (1-prior)*pDGivenNX;
  }
  else {
    pXAndEvent = prior*(1-pDGivenX);
    pNXAndEvent = (1-prior)*(1-pDGivenNX);
  }
  return pXAndEvent/(pXAndEvent + pNXAndEvent);
}

Position realToGrid(RealPosition &real) {
  Position grid;
  grid.l = real.x/CELL_HEIGHT;
  grid.c = real.y/CELL_WIDTH;
  return grid;
}

RealPosition gridToReal(Position &grid) {
  RealPosition real;
  real.x = (grid.l)*CELL_HEIGHT;
  real.y = (grid.c)*CELL_WIDTH;
  return real;
}

double distanceSqr(Position &p1, Position &p2) {
  RealPosition rp1 = gridToReal(p1);
  RealPosition rp2 = gridToReal(p2);
  return (rp1.x-rp2.x)*(rp1.x-rp2.x) + (rp1.y-rp2.y)*(rp1.y-rp2.y);
}

void setNeighbors(Position &p) {
  allnNeighbors[p.l][p.c] = 0;
  Position *possibleNeighbors[NNEIGHBORS] = {
    new Position(p.l-1,p.c-1),
    new Position(p.l-1,p.c),
    new Position(p.l-1,p.c+1),
    new Position(p.l,p.c-1),
    new Position(p.l,p.c+1),
    new Position(p.l+1,p.c-1),
    new Position(p.l+1,p.c),
    new Position(p.l+1,p.c+1)
  };
  for(int i = 0; i < NNEIGHBORS; ++i) {
    if(isValid(*possibleNeighbors[i])) {
      allNeighbors[p.l][p.c][allnNeighbors[p.l][p.c]++] = possibleNeighbors[i];
    }
    else {
      delete possibleNeighbors[i];
    }
  }
}

// BFS to mark every square around in a radius.
void bfsMark(int type, bool detect, Position &start, int radius) {
  int nNeighbors;
  Position **neighbors;
  Position *cur;

  memset(visited, false, HEIGHT*WIDTH*sizeof(bool));
  visited[start.l][start.c] = true;

  queueFront = queueBack = 0;
  queue[queueBack++] = &start;

  while(queueBack > queueFront) {
    cur = queue[queueFront++];
    
    nNeighbors = allnNeighbors[cur->l][cur->c];
    neighbors = allNeighbors[cur->l][cur->c];

    switch(type) {
    case ROBOT_BODY:
      theMap[cur->l][cur->c].pWall = bayesianUpdate(theMap[cur->l][cur->c].pWall, P_DETECT_GIVEN_WALL, P_DETECT_GIVEN_NWALL, detect);
    default:
      theMap[cur->l][cur->c].pBall = bayesianUpdate(theMap[cur->l][cur->c].pBall, P_DETECT_GIVEN_BALL, P_DETECT_GIVEN_NBALL, detect);
    }
    if(type == RED_BALL || type == GREEN_BALL) {
      theMap[cur->l][cur->c].ballType = type;
    }

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

// Gets sensor information: either wall detection/no detection or ball detection.
void sensorUpdate(int type, bool detect, RealPosition &worldPos, RealPosition &robotPos) {
  Position gridPos = realToGrid(worldPos);
  Position robotGridPos = realToGrid(robotPos);
  int l,c;
  double minDist, d;

  Position **neighbors;
  int nNeighbors;
  
  // Ball detection
  if(type == RED_BALL || type == GREEN_BALL) {
    // BFS to mark spots in the BALL_RADIUS.
    bfsMark(type, detect, gridPos, BALL_RADIUS);
  }

  // Robot clearing
  else if(type == ROBOT_BODY) {
    bfsMark(type, detect, robotGridPos, ROBOT_RADIUS);
  }

  // Wall detection/no detection
  else {
    // Do a best first search to find a line from robot to wall and clear it:
    minDist = distanceSqr(gridPos, robotGridPos);
    while(robotGridPos.l != gridPos.l || robotGridPos.c != gridPos.c) {
      l = robotGridPos.l;
      c = robotGridPos.c;

      theMap[l][c].pWall = bayesianUpdate(theMap[l][c].pWall, P_DETECT_GIVEN_WALL, P_DETECT_GIVEN_NWALL, false);

      nNeighbors = allnNeighbors[l][c];
      neighbors = allNeighbors[l][c];
      
      for(int i = 0; i < nNeighbors; ++i) {
	d = distanceSqr(gridPos, *neighbors[i]);
	if(d < minDist) {
	  minDist = d;
	  robotGridPos.l = neighbors[i]->l;
	  robotGridPos.c = neighbors[i]->c;
	}
      }
    }
    
    // Update detected/undetected spot
    l = gridPos.l;
    c = gridPos.c;
    if(isValid(gridPos)) {
      if(detect) {
	theMap[l][c].pBall = bayesianUpdate(theMap[l][c].pBall, P_DETECT_GIVEN_BALL, P_DETECT_GIVEN_NBALL, false);
      }
      theMap[l][c].pWall = bayesianUpdate(theMap[l][c].pWall, P_DETECT_GIVEN_WALL, P_DETECT_GIVEN_NWALL, detect);
    }
  }
}

bool setWallType(int type, RealPosition &orientation, RealPosition &robotPos) {
  double minDist,d;
  Position gridOri = realToGrid(orientation);
  Position robotGridPos = realToGrid(robotPos);
  if(!isValid(robotGridPos)) {
    return false;
  }

  Position **neighbors;
  int nNeighbors;

  // Do a best first search to "draw" a line in the provided orientation and see if any walls intersect
  int l=-1,c=-1;
  minDist = distanceSqr(gridOri, robotGridPos);
  do {
    l = robotGridPos.l;
    c = robotGridPos.c;
    
    if(isWall(theMap[l][c])) {
      theMap[l][c].wallType = type;
      return true;
    }

    neighbors = allNeighbors[l][c];
    nNeighbors = allnNeighbors[l][c];
    
    for(int i = 0; i < nNeighbors; ++i) {
      d = distanceSqr(gridOri, *neighbors[i]);
      if(d < minDist) {
	minDist = d;
	robotGridPos.l = neighbors[i]->l;
	robotGridPos.c = neighbors[i]->c;
      }
    }
  } while(l != gridOri.l || c != gridOri.c);
  return false;
}

Position *findClosestBall(RealPosition &robotPos) {
  int nNeighbors;
  Position **neighbors;
  Position *cur;

  Position start = realToGrid(robotPos);

  memset(visited, false, HEIGHT*WIDTH*sizeof(bool));
  visited[start.l][start.c] = true;

  queueFront = queueBack = 0;
  queue[queueBack++] = &start;

  while(queueBack > queueFront) {
    cur = queue[queueFront++];

    nNeighbors = allnNeighbors[cur->l][cur->c];
    neighbors = allNeighbors[cur->l][cur->c];

    for(int i = 0; i < nNeighbors; ++i) {
      if(!visited[neighbors[i]->l][neighbors[i]->c]) {
	if(isBall(theMap[neighbors[i]->l][neighbors[i]->c])) {
	  return neighbors[i];
	}
	if(distanceSqr(start, *neighbors[i]) <= FIELD_DIAMETER*FIELD_DIAMETER) {
	  visited[neighbors[i]->l][neighbors[i]->c] = true;
	  queue[queueBack++] = neighbors[i];
	}
      }
    }
  }
  return NULL;
}


void initialize() {
  Position p;
  for(int l = 0; l < HEIGHT; ++l) {
    for(int c = 0; c < WIDTH; ++c) {
      theMap[l][c].pWall = PRIOR_WALL;
      theMap[l][c].pBall = PRIOR_BALL;
      theMap[l][c].wallType = NORMAL_WALL;
      p.l = l;
      p.c = c;
      setNeighbors(p);
    }
  }
}

void printMap() {
  for(int l = 0; l < HEIGHT; ++l) {
    for(int c = 0; c < WIDTH; ++c) {
      if(isWall(theMap[l][c])) {
	printf("#");
      }
      else if(isBall(theMap[l][c])) {
	if(theMap[l][c].ballType == RED_BALL) {
	  printf("R");
	}
	else {
	  printf("G");
	}
      }
      else {
	printf(".");
      }
    }
    printf("\n");
  }
  printf("\n");
}

