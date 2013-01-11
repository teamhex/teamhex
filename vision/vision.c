#include <linux/videodev2.h>
#include "colors.h"
#include "capture.h"
#include "general.h"
#include "pixel.h"
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>

extern "C" {
  struct cam c;
  Grabber g = Grabber(WIDTH,HEIGHT);
  int rgbPicture[WIDTH*HEIGHT];
  PixelArea *interestArea;
  
  // int main() {
  //   char *device = (char *)"/dev/video0";
  //   int *rgbPicture = (int *)malloc(WIDTH*HEIGHT*sizeof(int));
  //   struct cam c;
  //   initCam(&c, device);
  //   resetControl(&c, V4L2_CID_BRIGHTNESS);
  //   resetControl(&c, V4L2_CID_CONTRAST);
  //   resetControl(&c, V4L2_CID_SATURATION);
  //   resetControl(&c, V4L2_CID_GAIN);
  //   PixelGrid grid(HEIGHT,WIDTH);
  //   grid.setPixels(rgbPicture);
  //   capture(&c,rgbPicture);
  //   Grabber g = Grabber(WIDTH, HEIGHT);
  //   g.findObjectsInImage(rgbPicture);
  //   vector<const ColorParameters*> colors;
  //   colors.push_back(&g.COLOR_PURPLE);
  //   Position p = g.getCenterOfLargestArea(colors, rgbPicture);
  //   printf("%d %d\n", p.l, p.c);
  //   for(int i = 0; i < 10; ++i) {
  //     capture(&c,rgbPicture);
  //     g.findObjectsInImage(rgbPicture);
  //     p = g.getCenterOfLargestArea(colors,rgbPicture);
  //     printf("%d %d\n", p.l, p.c);
  //   }
  //   saveRGB(rgbPicture, "snap");
  //   free(rgbPicture);
  //   closeCam(&c);
  // }
  void startCam(char *device) {
    initCam(&c, device);
    resetControl(&c, V4L2_CID_BRIGHTNESS);
    resetControl(&c, V4L2_CID_CONTRAST);
    resetControl(&c, V4L2_CID_SATURATION);
    resetControl(&c, V4L2_CID_GAIN);
  }

  void enableCam() {
    enableCapture(&c);
  }

  void stopCam() {
    closeCam(&c);
  }

  void getInfo() {
    capture(&c,rgbPicture);
    g.findObjectsInImage(rgbPicture);
    interestArea = g.getLargestArea();
    int col = 255;
    int color = col;
    /*for(vector<PixelArea*>::iterator i = g.areas.begin(); i != g.areas.end(); ++i) {
      (*i)->color(rgbPicture,color);
      color <<= 8;
      if(color > (255<<16)+(255<<8)+255) {
	col /= 2;
	color = col;
      }
      }*/
    //saveRGB(rgbPicture, "snap");
    //printf("%d\n", g.areas.size());
  }

  int getX() {
    if(interestArea == NULL) {
      return 0;
    }
    return interestArea->getCenter().c;
  }

  int getSize() {
    if(interestArea == NULL) {
      return 0;
    }
    return interestArea->hue;
  }

  int main() {
    startCam((char *)"/dev/video1");
    enableCam();
    
    for(int i = 0; i < 100; ++i) {
      getInfo();
      printf("%d %d\n", getX(), getSize());
      //getchar();
    }
    stopCam();
  }

}
