#define CLAMP(V) (((V)>255)?255:(((V)<0)?0:(V)))

void YUYVtoRGB(const void *yuvStream, int width, int height, int *buffer);
