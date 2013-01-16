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

// Matcher that is givena a matcher and draws on the matching cells.
class DrawMatcher: public Matcher {
private:
  Matcher *matches;
public:
  DrawMatcher(Matcher *m): matches(m) {}
  bool operator ()(Position *current, Position *neighbor) {
    if((*matches)(current, neighbor)) {
      rgbPictureMeh[neighbor->l*WIDTH+neighbor->c] = 0;
      return true;
    }
    else {
      return false;
    }
  }
};

DrawMatcher m = DrawMatcher(&MATCHER);

void getInfo() {
  //capture(&c,rgbPicture);
  // Wait for new picture!
  newPicture = true;
  if(!newPicture) {
    pthread_mutex_lock(&newPictureLock);
    pthread_cond_wait(&newPictureCond, &newPictureLock);
    newPicture = false;
    pthread_mutex_unlock(&newPictureLock);
  }
  
  pthread_mutex_lock(&pictureLock);
  //memcpy(rgbPictureMeh, rgbPicture, sizeof(int)*WIDTH*HEIGHT);
  pthread_mutex_unlock(&pictureLock);

  memset(rgbPictureMeh, 0, sizeof(int)*WIDTH*HEIGHT);
  
  blur(rgbPictureMeh);
  startHSL(rgbPictureMeh);
  m = DrawMatcher(&COLOR_GREEN);
  findObjectsInImage(COLOR_GREEN);
  interestArea = getLargestArea();
  if(interestArea != NULL) {
    memset(visited, false, sizeof(bool)*WIDTH*HEIGHT);
    setArea(interestArea->start, m);
  }
  m = DrawMatcher(&COLOR_RED);
  findObjectsInImage(COLOR_RED);
  interestArea = getLargestArea();
  if(interestArea != NULL) {
    memset(visited, false, sizeof(bool)*WIDTH*HEIGHT);
    setArea(interestArea->start, m);
  }
  m = DrawMatcher(&COLOR_YELLOW);
  findObjectsInImage(COLOR_YELLOW);
  interestArea = getLargestArea();
  if(interestArea != NULL) {
    memset(visited, false, sizeof(bool)*WIDTH*HEIGHT);
    setArea(interestArea->start, m);
  }
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
