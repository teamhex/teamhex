#include <linux/videodev2.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>

#include "general.h"
#include "pixel.h"

extern "C" {
#include "colors.h"
#include "capture.h"
}

#include "vision.h"

struct cam c;
int rgbPicture[WIDTH*HEIGHT];
PixelArea *interestArea;

void startCam(const char *device) {
  initCam(&c, device);
  resetControl(&c, V4L2_CID_BRIGHTNESS);
  resetControl(&c, V4L2_CID_CONTRAST);
  resetControl(&c, V4L2_CID_SATURATION);
  resetControl(&c, V4L2_CID_GAIN);
  startNeighbors();
}

void enableCam() {
  enableCapture(&c);
}

void stopCam() {
  closeCam(&c);
}

class DrawingMatcher: public Matcher {
private:
  int hue;
  int tolerance;
public:
  DrawingMatcher(int h, int t): hue(h), tolerance(t) {}
  bool operator ()(Position *start, Position *neighbor) {
    if(ANGLE_DIST(hue, hslPicture[neighbor->l][neighbor->c]>>14) < tolerance) {
      rgbPicture[neighbor->l*WIDTH+neighbor->c] = 0;
      return true;
    }
    else {
      return false;
    }
  }
};

DrawingMatcher GREEN_DRAW = DrawingMatcher(140,30);
DrawingMatcher RED_DRAW = DrawingMatcher(350,20);

void getInfo() {
  capture(&c,rgbPicture);
  startHSL(rgbPicture);
  findObjectsInImage(RED_DRAW);
  interestArea = getLargestArea();
  //int col = 255;
  //int color = col;
  /* for(vector<PixelArea*>::iterator i = g.areas.begin(); i != g.areas.end(); ++i) { */
  /*   (*i)->color(rgbPicture,color); */
  /*   color <<= 8; */
  /*   if(color > (255<<16)+(255<<8)+255) { */
  /* 	col /= 2; */
  /* 	color = col; */
  /*   } */
  /* } */
  saveRGB(rgbPicture, "snap");
  //printf("%d\n", g.areas.size());
}

int getX() {
  if(interestArea == NULL) {
    return 0;
  }
  return interestArea->center.c;
}

int getSize() {
  if(interestArea == NULL) {
    return 0;
  }
  return interestArea->size;
}
