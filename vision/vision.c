#include <linux/videodev2.h>
#include "colors.h"
#include "capture.h"
#include "pixel.h"
#include <stdlib.h>

extern "C" {
struct cam c;
Grabber g = Grabber(WIDTH,HEIGHT);
int *rgbPicture = (int *) malloc(WIDTH*HEIGHT*sizeof(int));
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
extern "C" {
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
  free(rgbPicture);
  closeCam(&c);
}

void getInfo() {
  capture(&c,rgbPicture);
  g.findObjectsInImage(rgbPicture);
  interestArea = g.getLargestArea();
}

int getX() {
  return interestArea->getCenter().c;
}

int getSize() {
  return interestArea->getSize();
}

}}
