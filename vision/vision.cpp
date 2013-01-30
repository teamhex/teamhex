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
int rgbBuffers[2][WIDTH*HEIGHT];
int currentBuffer;
int *rgbPicture;
int *rgbPictureMeh;
int rgbPictureTemp[WIDTH*HEIGHT];

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
  currentBuffer = 0;
  rgbPicture = rgbBuffers[0];
  rgbPictureMeh = rgbBuffers[1];
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
  //newPicture = true;
  if(!newPicture) {
    pthread_mutex_lock(&newPictureLock);
    pthread_cond_wait(&newPictureCond, &newPictureLock);
    newPicture = false;
    pthread_mutex_unlock(&newPictureLock);
  }
  pthread_mutex_lock(&pictureLock);
  //memcpy(rgbPictureMeh, rgbPicture, WIDTH*HEIGHT*sizeof(int));
  rgbPictureMeh = rgbBuffers[currentBuffer];
  currentBuffer = (currentBuffer+1)&1;
  rgbPicture = rgbBuffers[currentBuffer];
  pthread_mutex_unlock(&pictureLock);
}

int i = 0;
char str[20];

void getInfo() {
  //blur(rgbPictureMeh);
  startHSL(rgbPictureMeh);
  findObjectsInImage(LOOKER,BLUE_WALLS);
  sprintf(str, "tmp/snap%d", i++);
  saveRGB(rgbPictureMeh, str);
}

int getNAreas() {
  return nAreas;
}

void getArea(int i, struct CPixelArea *res) {
  if(i >= 0 && i < nAreas) {
    res->pixel = areas[i]->startPixel;
    res->topLeftL = areas[i]->topLeft.l;
    res->topLeftC = areas[i]->topLeft.c;
    res->bottomRightL = areas[i]->bottomRight.l;
    res->bottomRightC = areas[i]->bottomRight.c;
    res->centerL = (areas[i]->topLeft.l+areas[i]->bottomRight.l)/2.0;
    res->centerC = (areas[i]->topLeft.c+areas[i]->bottomRight.c)/2.0;
    res->size = areas[i]->size;
  }
  else {
    res->pixel = -1;
    res->centerL = -1;
    res->centerC = -1;
    res->size = -1;
  }
}
