#include <linux/videodev2.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

#include "general.h"
#include "pixel.h"

extern "C" {
#include "colors.h"
#include "capture.h"
}

#include "vision.h"

struct cam c;
int rgbPicture[WIDTH*HEIGHT];
int rgbPictureTemp[WIDTH*HEIGHT];
int rgbPictureMeh[WIDTH*HEIGHT];
PixelArea *interestArea;

pthread_t captureThread;
pthread_mutex_t pictureLock = PTHREAD_MUTEX_INITIALIZER;
bool newPicture = false;
pthread_mutex_t newPictureLock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t newPictureCond = PTHREAD_COND_INITIALIZER;
bool terminate = false;

void startCam(const char *device) {
  initCam(&c, device);
  resetControl(&c, V4L2_CID_BRIGHTNESS);
  resetControl(&c, V4L2_CID_CONTRAST);
  resetControl(&c, V4L2_CID_SATURATION);
  resetControl(&c, V4L2_CID_GAIN);
  startNeighbors();
}

void *continuousCapture(void *ptr) {
  while(!terminate) {
    capture(&c, rgbPictureTemp);
    pthread_mutex_lock(&pictureLock);
    memcpy(rgbPicture, rgbPictureTemp, sizeof(int)*WIDTH*HEIGHT);
    pthread_mutex_unlock(&pictureLock);

    pthread_mutex_lock(&newPictureLock);
    newPicture = true;
    pthread_cond_signal(&newPictureCond);
    pthread_mutex_unlock(&newPictureLock);
  }
}

void enableCam() {
  enableCapture(&c);
  // Continuously capture until stopCam() is called.
  pthread_create(&captureThread, NULL, continuousCapture, NULL);
}

void stopCam() {
  terminate = true;
  pthread_join(captureThread, NULL);
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
      rgbPictureMeh[neighbor->l*WIDTH+neighbor->c] = 0;
      return true;
    }
    else {
      return false;
    }
  }
};

// Checks if two HSL vectors are similar.
// HSL vector: least significant 7 bits are light, next 7 are saturation, next are hue
// Strategy: subtract and see if resulting vector's magnitude is withing threshold
class DrawGroup: public Matcher {
private:
  int tolerance;
public:
  DrawGroup(int t): tolerance(t) {}
  bool operator ()(Position *current, Position *neighbor) {
    int dh,ds,dl;
    int v1 = hslPicture[current->l][current->c];
    int v2 = hslPicture[neighbor->l][neighbor->c];
    dh = (v1>>14) - (v2>>14);
    ds = ((v1>>7)&BIT7) - ((v2>>7)&BIT7);
    dl = (v1&BIT7)-(v2&BIT7);
    
    if( (dh*dh+ds*ds+dl*dl) < tolerance) {
      rgbPictureMeh[neighbor->l*WIDTH+neighbor->c] = 0;
      return true;
    }
    else {
      return false;
    }
  }
};

DrawGroup GROUP_DRAW = DrawGroup(30);

DrawingMatcher GREEN_DRAW = DrawingMatcher(140,20);
DrawingMatcher RED_DRAW = DrawingMatcher(350,20);
DrawingMatcher YELLOW_DRAW = DrawingMatcher(64,20);

void getInfo() {
  //capture(&c,rgbPicture);
  // Wait for new picture!
  if(!newPicture) {
    pthread_mutex_lock(&newPictureLock);
    pthread_cond_wait(&newPictureCond, &newPictureLock);
    newPicture = false;
    pthread_mutex_unlock(&newPictureLock);
  }
  
  pthread_mutex_lock(&pictureLock);
  memcpy(rgbPictureMeh, rgbPicture, sizeof(int)*WIDTH*HEIGHT);
  pthread_mutex_unlock(&pictureLock);

  startHSL(rgbPictureMeh);
  findObjectsInImage(GROUP);
  interestArea = getLargestArea();
  memset(visited, false, sizeof(bool)*WIDTH*HEIGHT);
  setArea(interestArea->start, GROUP_DRAW);
  saveRGB(rgbPictureMeh, "tmp/snap");
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
  //saveRGB(rgbPicture, "snap");
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

int getHue() {
  if(interestArea == NULL) {
    return 0;
  }
  return interestArea->hue;
}
