#ifndef CAPTURE_H
#define CAPTURE_H

#define NBUFFERS 16
#define WIDTH 640
#define HEIGHT 480

// Useful structure with all the necessary information about the camera
struct cam {
  int fd;
  struct v4l2_format fmt;
  struct v4l2_buffer buf;
  struct v4l2_requestbuffers rb;
  void *mem[NBUFFERS];
  char captureEnabled;
};

int initCam(struct cam *c, char *device);
int enableCapture(struct cam *c);
int disableCapture(struct cam *c);
void closeCam(struct cam *c);
int capture(struct cam *c, int *buffer);
int getRGB(void *p, int *buffer);
void saveRGB(int *info, const char *filename);

#endif
