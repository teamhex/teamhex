#include <string.h>
#include <stdlib.h>

#include "general.h"
#include "pixel.h"

extern "C" {
#include "colors.h"
}

int hslPicture[HEIGHT][WIDTH];
bool visited[HEIGHT][WIDTH];
Position *queue[WIDTH*HEIGHT];
int front,back;
int count = 0;
PixelArea *area;

PixelArea *largestArea;

Position *allNeighbors[HEIGHT][WIDTH][NNEIGHBORS];
int allnNeighbors[HEIGHT][WIDTH];

Position::Position(): l(0),c(0) {}
Position::Position(int line, int column): l(line),c(column) {}

HueMatcher::HueMatcher(int h, int t): hue(h), tolerance(t) {}
bool HueMatcher::operator ()(Position *start, Position *neighbor) {
  return ANGLE_DIST(hue,hslPicture[neighbor->l][neighbor->c]>>14) < tolerance;
}

// Checks if two HSL vectors are similar.
// HSL vector: least significant 7 bits are light, next 7 are saturation, next are hue
// Strategy: subtract and see if resulting vector's magnitude is withing threshold
GroupMatcher::GroupMatcher(int t): tolerance(t) {}
bool GroupMatcher::operator ()(Position *current, Position *neighbor) {
  int dh,ds,dl;
  int v1 = hslPicture[current->l][current->c];
  int v2 = hslPicture[neighbor->l][neighbor->c];
  dh = (v1>>14) - (v2>>14);
  //ds = ((v1>>7)&BIT7) - ((v2>>7)&BIT7);
  dl = (v1&BIT7)-(v2&BIT7);

  return (dh*dh+ds*ds+dl*dl) < tolerance;
}

HueMatcher COLOR_GREEN = HueMatcher(140,30);
HueMatcher COLOR_RED = HueMatcher(350,30);
HueMatcher COLOR_PURPLE = HueMatcher(25,30);
HueMatcher COLOR_YELLOW = HueMatcher(64,30);

GroupMatcher GROUP = GroupMatcher(30);

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
    if(IS_VALID(*possibleNeighbors[i],WIDTH,HEIGHT)) {
      allNeighbors[p.l][p.c][allnNeighbors[p.l][p.c]++] = possibleNeighbors[i];
    }
    else {
      delete possibleNeighbors[i];
    }
  }
}

void setArea(Position *start, Matcher &matches) {
  if(visited[start->l][start->l] || !matches(start, start)) {
    area = NULL;
    return;
  }
  int nNeighbors;
  Position **neighbors;
  Position *neigh,*current;
  int curHSL;

  area = new PixelArea();
  area->start = start;
  area->size = 0;
  area->center.l = 0;
  area->center.c = 0;
  
  front = back = 0;
  queue[back++] = start;
  visited[start->l][start->c] = true;

  while(back > front) {
    current = queue[front++];
    curHSL = hslPicture[(current)->l][(current)->c];

    ++area->size;
    area->center.l += (current)->l;
    area->center.c += (current)->c;
    area->hue += curHSL>>14;

    nNeighbors = allnNeighbors[current->l][current->c];
    neighbors = allNeighbors[current->l][current->c];
    
    for(int i = 0; i < nNeighbors; ++i) {
      neigh = neighbors[i];
      
      if(matches((current), neigh) && !visited[neigh->l][neigh->c]) {
	queue[back++] = neigh;
	visited[neigh->l][neigh->c] = true;
	++count;
      }
    }
  }

  area->center.l /= area->size;
  area->center.c /= area->size;
  area->hue /= area->size;
}

void startNeighbors() {
  Position p;
  for(p.l = 0; p.l < HEIGHT; ++p.l) {
    for(p.c = 0; p.c < WIDTH; ++p.c) {
      setNeighbors(p);
    }
  }
}

void startHSL(int *rgb) {
  for(int l = 0; l < HEIGHT; ++l) {
    for(int c = 0; c < WIDTH; ++c) {
      hslPicture[l][c] = RGBtoHSL(rgb[l*WIDTH+c]);
    }
  }
}  

void findObjectsInImage(Matcher &matches) {
  int maxSize = -1;
  largestArea = NULL;
  memset(visited, false, sizeof(bool)*WIDTH*HEIGHT);

  for(int l = 0; l < HEIGHT; ++l) {
    for(int c = 0; c < WIDTH; ++c) {
      setArea(new Position(l,c), matches);
      if(area != NULL) {
	if(area->size > maxSize) {
	  if(maxSize != -1) {
	    delete largestArea->start;
	    delete largestArea;
	  }
	  maxSize = area->size;
	  largestArea = area;
	}
	else {
	  delete area->start;
	  delete area;
	}
      }
    }
  }
}

PixelArea *getLargestArea() {
  return largestArea;
}
