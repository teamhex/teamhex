#include <stdlib.h>
#include <stdio.h>
#include "colors.h"

void YUYVtoRGB(const void *yuvStream, int width, int height, int *buffer) {
  unsigned char *yuyv = (unsigned char *)yuvStream;
  int z,i;
  int r,g,b;
  int y,u,v;

  z = 0;
  for(i = 0; i < width*height; ++i) {
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

struct hsl RGBtoHSL(int rgbValue) {
  double r,g,b;
  double h,s,l;
  double maxVal,minVal,maxDelta;
  struct hsl res;

  r = ((rgbValue>>16)&0xFF) / 255.0;
  g = ((rgbValue>>8)&0xFF) / 255.0;
  b = ((rgbValue)&0xFF) / 255.0;

  maxVal = MAX(MAX(r,g),b);
  minVal = MIN(MIN(r,g),b);
  maxDelta = maxVal-minVal;

  l = (maxVal+minVal)/2.0;
  
  if(maxDelta == 0) {
    h = 0;
    s = 0;
  } // gray
  else { // Chroma
    double dR,dG,dB;
    s = maxDelta/((l < 0.5)?(maxVal+minVal):(2-maxVal-minVal));
    dR = (((maxVal-r)/6.0)+(maxDelta/2.0))/maxDelta;
    dG = (((maxVal-g)/6.0)+(maxDelta/2.0))/maxDelta;
    dB = (((maxVal-b)/6.0)+(maxDelta/2.0))/maxDelta;

    if(r == maxVal) {
      h = dB-dG;
    }
    else if(g == maxVal) {
      h = (1.0/3.0) + dR-dB;
    }
    else {
      h = (2.0/3.0) + dG-dR;
    }

    if(h < 0) {
      h += 1;
    }
    else if(h > 1) {
      h -= 1;
    }
  }
  res.h = (int) (h*360);
  res.s = (int) (s*100);
  res.l = (int) (l*100);
  if(res.h > 360)
    printf("Total chaos oO\n");
  return res;
}
