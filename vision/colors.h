#ifndef COLORS_H
#define COLORS_H

#define MAX(I,J) ((I)>(J)?(I):(J))
#define MIN(I,J) ((I)<(J)?(I):(J))
#define CLAMP(V) (((V)>255)?255:(((V)<0)?0:(V)))

void YUYVtoRGB(const void *yuvStream, int width, int height, int *buffer);
int RGBtoHSL(int rgbValue);

#endif
