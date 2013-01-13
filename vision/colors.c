#include <stdlib.h>
#include <math.h>
#include <stdio.h>

#include "general.h"
#include "colors.h"

int aux[HEIGHT*WIDTH];

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
    buffer[i] = (r<<16)|(g<<8)|b;
  }
}

int RGBtoHSL(int rgbValue) {
  double r,g,b;
  double h,s,l;
  double maxVal,minVal,maxDelta;
  int finalH, finalS, finalL;

  r = ((rgbValue>>16)&BIT8) / 255.0;
  g = ((rgbValue>>8)&BIT8) / 255.0;
  b = ((rgbValue)&BIT8) / 255.0;

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
  finalH = (int) (h*360);
  finalS = (int) (s*100);
  finalL = (int) (l*100);

  return (finalH<<16) | (finalS<<8) | finalL;
}

int RGBtoLab(int rgbValue) {
  double r,g,b;
  double x,y,z;
  int l,a,b2;
  r = (rgbValue>>16)/255.0;
  g = ((rgbValue>>8)&BIT8)/255.0;
  b = (rgbValue&BIT8)/255.0;

  // RGB to XYZ
  r = ((r>0.04045)?pow((r+0.055)/1.055, 2.4):(r/12.92))*100;
  g = ((g>0.04045)?pow((g+0.055)/1.055, 2.4):(g/12.92))*100;
  b = ((b>0.04045)?pow((b+0.055)/1.055, 2.4):(b/12.92))*100;

  x = r*0.4124 + g*0.3576 + b*0.1805;
  y = r*0.2126 + g*0.7152 + b*0.0722;
  z = r*0.0193 + g*0.1192 + b*0.9505;

  // XYZ to Lab
  x = x/95.047;
  y = y/100.0;
  z = z/108.883;

  x = (x>0.008856)?pow(x,1.0/3.0):(7.787*x + 16.0/116.0);
  y = (y>0.008856)?pow(y,1.0/3.0):(7.787*y + 16.0/116.0);
  z = (z>0.008856)?pow(z,1.0/3.0):(7.787*z + 16.0/116.0);

  l = (int) (116.0*y - 16);
  a = (int) (500.0*(x-y) + 128);
  b2 = (int) (200.0*(y-z) + 128);

  if(l > 255 || b2 > 255 || a > 255 || l < 0 || b2 < 0 || a < 0) {
    printf("%d %d %d\n", l, a, b2);
  }

  return (l<<16) | (a<<8) | (b2);
}

int LabDiffSqr(int lab1, int lab2) {
  int l1,a1,b1,l2,a2,b2;
  double dL,dC,dHSqr, c1;
  l1 = (lab1>>16);
  a1 = ((lab1>>8)&BIT8) - 128;
  b1 = (lab1&BIT8) - 128;

  l2 = lab2>>16;
  a2 = (lab2>>8)&BIT8 - 128;
  b2 = (lab2&BIT8) - 128;

  c1 = sqrt((double) (a1*a1+b1*b1));
  dL = (double) (l1-l2);
  dC = c1 - sqrt((double)(a2*a2 + b2*b2));
  dHSqr = (double)((a1-a2)*(a1-a2) + (b1-b2)*(b1-b2)) - dC*dC;

  return (int) (dL*dL + dC*dC/((1.0+0.045*c1)*(1.0+0.045*c1)) + dHSqr/((1.0+0.015*c1)*(1.0+0.015*c1)));
}

// Blurs an image of dimensions WIDTH*HEIGHT using separate vertical+horizontal blurs.
void blur(int *rgb) {
  int r,g,b,rgbPixel;
  int l,c,i;

  // Horizontal blur:
  for(l = 0; l < HEIGHT; ++l) {
    r=g=b=0;
    // Process the first pixel:
    for(i = -RADIUS; i <= RADIUS; ++i) {
      rgbPixel = rgb[l*WIDTH+CLIP(i,0,WIDTH)];
      r += (rgbPixel>>16);
      g += ((rgbPixel>>8)&BIT8);
      b += (rgbPixel&BIT8);
    }
    aux[l*WIDTH] = ((r/(RADIUS*2+1))<<16) | ((g/(RADIUS*2+1))<<8) | (b/(RADIUS*2+1));

    for(c = 1; c < WIDTH; ++c) {
      rgbPixel = rgb[l*WIDTH+CLIP(c-RADIUS-1,0,WIDTH)];
      r -= (rgbPixel>>16);
      g -= ((rgbPixel>>8)&BIT8);
      b -= (rgbPixel&BIT8);
      rgbPixel = rgb[l*WIDTH+CLIP(c+RADIUS,0,WIDTH)];
      r += (rgbPixel>>16);
      g += ((rgbPixel>>8)&BIT8);
      b += (rgbPixel&BIT8);
      aux[l*WIDTH+c] = ((r/(RADIUS*2+1))<<16) | ((g/(RADIUS*2+1))<<8) | (b/(RADIUS*2+1));
    }
  }


  // Vertical blur:
  for(c = 0; c < WIDTH; ++c) {
    r=g=b=0;
    // Process the first pixel:
    for(i = -RADIUS; i <= RADIUS; ++i) {
      rgbPixel = aux[CLIP(i,0,HEIGHT)*WIDTH+c];
      r += (rgbPixel>>16);
      g += ((rgbPixel>>8)&BIT8);
      b += (rgbPixel&BIT8);
    }
    rgb[c] = ((r/(RADIUS*2+1))<<16) | ((g/(RADIUS*2+1))<<8) | (b/(RADIUS*2+1));

    for(l = 1; l < WIDTH; ++l) {
      rgbPixel = aux[CLIP(l-RADIUS-1,0,HEIGHT)*WIDTH+c];
      r -= (rgbPixel>>16);
      g -= ((rgbPixel>>8)&BIT8);
      b -= (rgbPixel&BIT8);
      rgbPixel = aux[CLIP(l+RADIUS,0,HEIGHT)*WIDTH+c];
      r += (rgbPixel>>16);
      g += ((rgbPixel>>8)&BIT8);
      b += (rgbPixel&BIT8);
      rgb[l*WIDTH+c] = ((r/(RADIUS*2+1))<<16) | ((g/(RADIUS*2+1))<<8) | (b/(RADIUS*2+1));
    }
  }
}
