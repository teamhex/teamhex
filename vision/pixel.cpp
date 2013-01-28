#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#include "general.h"
#include "pixel.h"

extern "C" {
#include "colors.h"
}

int nAreas = 0;
PixelArea *areas[WIDTH*HEIGHT];
int picture[HEIGHT][WIDTH];
int operationID;
int visited[HEIGHT][WIDTH];
Position *queue[WIDTH*HEIGHT];
int front,back;
PixelArea *area;

Position *allNeighbors[HEIGHT][WIDTH][NNEIGHBORS];
int allnNeighbors[HEIGHT][WIDTH];

Position::Position(): l(0),c(0) {}
Position::Position(int line, int column): l(line),c(column) {}

HueMatcher::HueMatcher(int h, int t, int mSize, int mSat, int mLum):
  hue(h), tolerance(t), minSize(mSize), minSat(mSat), maxLum(mLum) {}
void HueMatcher::fill(HueMatcher **hueVector) {
  for(int i = -tolerance; i <= tolerance; ++i) {
    hueVector[(hue+i+360)%360] = this;
  }
}
bool HueMatcher::operator ()(int current, int neighbor) {
  return
    ANGLE_DIST(hue,neighbor>>16) < tolerance &&
    ((neighbor>>8)&0xFF) > minSat &&
    (neighbor&0xFF) < maxLum;
}
bool HueMatcher::operator ()(PixelArea *area) {
  return
    area != NULL &&
    (*this)(area->startPixel, area->startPixel) &&
    //area->size > minSize;
    (area->bottomRight.l - area->topLeft.l)*(area->bottomRight.c-area->topLeft.c) > minSize;
}

MultiHueMatcher::MultiHueMatcher(HueMatcher **matchers, int nMatchers) {
  memset(match, 0, sizeof(HueMatcher **)*360);
  for(int i = 0; i < nMatchers; ++i) {
    matchers[i]->fill(match);
  }
}
bool MultiHueMatcher::operator ()(int current, int neighbor) {
  if(match[neighbor>>16] != NULL && match[current>>16] == match[neighbor>>16]) {
    return (*match[neighbor>>16])(current, neighbor);
  }
  return false;
}
bool MultiHueMatcher::operator ()(PixelArea *area) {
  if(area != NULL && match[(area->startPixel)>>16] != NULL) {
    return (*match[(area->startPixel)>>16])(area);
  }
  return false;
}

HueMatcher COLOR_GREEN = HueMatcher(125,35,100,20,80);
HueMatcher COLOR_RED = HueMatcher(0,20,100,30,80);
HueMatcher COLOR_YELLOW = HueMatcher(55,10,300,45,70);
HueMatcher COLOR_PURPLE = HueMatcher(255,10,300,45,70);
HueMatcher *lookerHues[] = {
  &COLOR_GREEN,
  &COLOR_RED,
  &COLOR_YELLOW,
  &COLOR_PURPLE
};

HueMatcher BLUE_WALLS = HueMatcher(217,10,400,30,60);
MultiHueMatcher LOOKER = MultiHueMatcher(lookerHues,4);

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
  if(visited[start->l][start->c] == operationID || !matches(picture[start->l][start->c], picture[start->l][start->c])) {
    delete start;
    area = NULL;
    return;
  }
  int nNeighbors;
  Position **neighbors;
  Position *neigh,*current;
  int curHSL;

  area = new PixelArea();
  area->startPosition = start;
  area->startPixel = picture[start->l][start->c];
  area->size = 0;
  area->center.l = 0;
  area->center.c = 0;
  area->topLeft.l = start->l;
  area->topLeft.c = start->c;
  area->bottomRight.l = start->l;
  area->bottomRight.c = start->c;
  
  front = back = 0;
  queue[back++] = start;
  visited[start->l][start->c] = operationID;

  while(back > front) {
    current = queue[front++];

    ++area->size;
    area->center.l += (current)->l;
    area->center.c += (current)->c;

    nNeighbors = allnNeighbors[current->l][current->c];
    neighbors = allNeighbors[current->l][current->c];

    for(int i = 0; i < nNeighbors; ++i) {
      neigh = neighbors[i];
      
      if(matches(picture[current->l][current->c], picture[neigh->l][neigh->c]) && visited[neigh->l][neigh->c] != operationID) {
	// Bounding square
	if(neigh->l < area->bottomRight.l) {
	  area->bottomRight.l = neigh->l;
	}
	else if(neigh->l > area->topLeft.l) {
	  area->topLeft.l = neigh->l;
	}
	if(neigh->c < area->bottomRight.c) {
	  area->bottomRight.c = neigh->c;
	}
	else if(neigh->c > area->topLeft.c) {
	  area->topLeft.c = neigh->c;
	}

	queue[back++] = neigh;
	visited[neigh->l][neigh->c] = operationID;
      }
    }
  }

  area->center.l /= area->size;
  area->center.c /= area->size;
}

void startNeighbors() {
  Position p;
  for(p.l = 0; p.l < HEIGHT; ++p.l) {
    for(p.c = 0; p.c < WIDTH; ++p.c) {
      setNeighbors(p);
    }
  }
  operationID = 0;
  memset(visited, 0, sizeof(int)*WIDTH*HEIGHT);
}

void startHSL(int *rgb) {
  for(int l = 0; l < HEIGHT; ++l) {
    for(int c = 0; c < WIDTH; ++c) {
      picture[l][c] = RGBtoHSL(rgb[l*WIDTH+c]);
    }
  }
}

void findObjectsInImage(Matcher &matches, Matcher &stopMatch) {
  ++operationID;
  area = NULL;
  // Clear previous areas
  for(int i = 0; i < nAreas; ++i) {
    delete areas[i]->startPosition;
    delete areas[i];
  }
  memset(areas, 0, sizeof(PixelArea *)*HEIGHT*WIDTH);
  nAreas = 0;

  for(int l = HEIGHT-1; l >= 0; --l) {
    for(int c = 0; c < WIDTH; ++c) {
      setArea(new Position(l,c), matches);
      if(matches(area)) {
	areas[nAreas++] = area;
      }
      else if(area != NULL) {
	delete area->startPosition;
	delete area;
      }
      setArea(new Position(l,c), stopMatch);
      if(stopMatch(area)) {
	delete area->startPosition;
	delete area;
	return;
      }
      if(area != NULL) {
	delete area->startPosition;
	delete area;
      }
    }
  }
}
