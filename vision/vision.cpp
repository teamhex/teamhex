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

void setFilePicture(char *filename) {
  char s[255];
  int r,g,b;
  FILE *fp = NULL;
  while(fp == NULL) {
    fp = fopen(filename, "r");
  }
  fgets(s, 255, fp);
  fgets(s, 255, fp);
  fgets(s, 255, fp);
  for(int l = 0; l < HEIGHT; ++l) {
    for(int c = 0; c < WIDTH; ++c) {
      r = fgetc(fp);
      g = fgetc(fp);
      b = fgetc(fp);
      rgbPictureMeh[l*WIDTH+c] = (r<<16) | (g<<8) | b;
    }
  }
  fclose(fp);
}

void setPicture() {
  // Wait for new picture!
  newPicture = true;
  if(!newPicture) {
    pthread_mutex_lock(&newPictureLock);
    pthread_cond_wait(&newPictureCond, &newPictureLock);
    newPicture = false;
    pthread_mutex_unlock(&newPictureLock);
  }
  pthread_mutex_lock(&pictureLock);
  memcpy(rgbPictureMeh, rgbPicture, sizeof(int)*WIDTH*HEIGHT);
  pthread_mutex_unlock(&pictureLock);
}

void getInfo() {
  //blur(rgbPictureMeh);
  startHSL(rgbPictureMeh);
  findObjectsInImage(LOOKER,BLUE_WALLS);
  //saveRGB(rgbPictureMeh, "tmp/snap");
}

int getNAreas() {
  return nAreas;
}

void getArea(int i, struct CPixelArea *res) {
  if(i >= 0 && i < nAreas) {
    res->pixel = areas[i]->startPixel;
    res->centerL = areas[i]->center.l;
    res->centerC = areas[i]->center.c;
    res->size = areas[i]->size;
  }
  else {
    res->pixel = -1;
    res->centerL = -1;
    res->centerC = -1;
    res->size = -1;
  }
}
