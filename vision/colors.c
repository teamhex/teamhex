#include <stdlib.h>
#include "colors.h"

void YUYVtoRGB(const void *yuvStream, int width, int height, int *buffer) {
  unsigned char *yuyv = (unsigned char *)yuvStream;
  int z,i;

  z = 0;
  for(i = 0; i < width*height; ++i) {
    int r,g,b;
    int y,u,v;

    if(!z) {
      y = yuyv[0] << 8;
    }
    else {
      y = yuyv[2] << 8;
    }
    u = yuyv[1]-128;
    v = yuyv[3]-128;

    r = CLAMP((y + (359*v)) >> 8);
    g = CLAMP((y - (88*u) - (183*v))>>8);
    b = CLAMP((y + (454*u)) >> 8);
    if(z++) {
      z = 0;
      yuyv += 4;
    }
    buffer[i] = (r<<16)+(g<<8)+b;
  }
}
