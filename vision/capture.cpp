#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "capture.h"
#include "colors.h"
#include <unistd.h>
#include <fcntl.h>
#include "pixel.h"

/*
  Initializes the camera drivers and the cam structure.
  Receives as input an empty cam structure and the device path.
  Opens the device, sets the format of YUY2 and starts the devices's buffers.
  The cam buffer will contain all the information needed for other functions.
  Returns 0 on success, -1 on failure.
*/

int initCam(struct cam *c, char *device) {
  int i;

  // Check if input is valid.
  if(c == NULL || device == NULL) {
    return -1;
  }
  // Start cam structure
  // capture needs to be enabled on camera.
  c->captureEnabled = 0;

  // Allocate buffer
  c->buffer = malloc(WIDTH*HEIGHT*2);

  // Opens file
  if((c->fd = open(device, O_RDWR)) == -1) {
    return -1;
  }

  /*
    Set format:
    640x480 size
    3-byte RGB format
  */
  memset(&c->fmt,0,sizeof(struct v4l2_format));
  c->fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
  c->fmt.fmt.pix.width = WIDTH;
  c->fmt.fmt.pix.height = HEIGHT;
  c->fmt.fmt.pix.field = V4L2_FIELD_ANY;
  c->fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
  if(ioctl(c->fd, VIDIOC_S_FMT, &c->fmt) < 0) {
    return -1;
  }

  // Request buffers
  memset(&c->rb, 0, sizeof(struct v4l2_requestbuffers));
  c->rb.count = NBUFFERS;
  c->rb.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
  c->rb.memory = V4L2_MEMORY_MMAP;
  if(ioctl(c->fd, VIDIOC_REQBUFS, &c->rb) < 0) {
    return -1;
  }

  // Map and queue buffers
  for(i = 0; i < NBUFFERS; ++i) {
    memset(&c->buf, 0, sizeof(struct v4l2_buffer));
    c->buf.index = i;
    c->buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    c->buf.memory = V4L2_MEMORY_MMAP;
    if(ioctl(c->fd, VIDIOC_QUERYBUF, &c->buf) < 0) {
      return -1;
    }
    c->mem[i] = mmap(0, c->buf.length, PROT_READ, MAP_SHARED, c->fd, c->buf.m.offset);
    if(c->mem[i] == MAP_FAILED) {
      return -1;
    }
  }
  for(i = 0; i < NBUFFERS; ++i) {
    memset(&c->buf, 0, sizeof(struct v4l2_buffer));
    c->buf.index = i;
    c->buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    c->buf.memory = V4L2_MEMORY_MMAP;
    if(ioctl(c->fd, VIDIOC_QBUF, &c->buf) < 0) {
      return -1;
    }
  }
  return 0;
}

/*
  Call when done with camera (this should be called for a clean exit!)
 */
void closeCam(struct cam *c) {
  int i;
  disableCapture(c);
  // Release memory maps
  for(i = 0; i < NBUFFERS; ++i) {
    munmap(c->mem[i], c->buf.length);
  }

  // Finish
  close(c->fd);
}

/*
  Turn on the camera for streaming.
 */
int enableCapture(struct cam *c) {
  // Enable video capture
  int type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
  if(c->captureEnabled) {
    return 0;
  }
  if(ioctl(c->fd, VIDIOC_STREAMON, &type) < 0) {
    return -1;
  }
  c->captureEnabled = 1;
  return 0;
}

/*
  Disable the camera's streaming.
*/
int disableCapture(struct cam *c) {
  // Disable video capture
  int type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
  if(!c->captureEnabled) {
    return 0;
  }
  if(ioctl(c->fd, VIDIOC_STREAMOFF, &type) < 0) {
    return -1;
  }
  c->captureEnabled = 0;
  return 0;
}

/*
  Take a picture and return an RGB array representing it.
  RGB is encoded in the following fashion:
  Each pixel is represented by an int: 8 bits for r, 8 bits for g, 8 bits for b, in this order.
*/
int capture(struct cam *c, int *buffer) {
  if(enableCapture(c)) {
    return -1;
  }
  memset(&c->buf, 0, sizeof(struct v4l2_buffer));
  c->buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
  c->buf.memory = V4L2_MEMORY_MMAP;
  // Dequeue buffer
  if(ioctl(c->fd, VIDIOC_DQBUF, &c->buf) < 0) {
    return -1;
  }
  // Get result from camera
  memcpy(c->buffer, c->mem[c->buf.index], c->buf.bytesused);
  // Queue buffer back
  if(ioctl(c->fd, VIDIOC_QBUF, &c->buf) < 0) {
    return -1;
  }
  // Convert it to RGB.
  YUYVtoRGB(c->mem[c->buf.index], WIDTH, HEIGHT, buffer);
  return 0;
}

// Reset the camera controls.
int resetControl(struct cam *c, int control) {
  struct v4l2_control control_s;
  struct v4l2_queryctrl queryctrl;
  
  // Is control a control?
  queryctrl.id = control;
  if(ioctl(c->fd, VIDIOC_QUERYCTRL, queryctrl) < 0) {
    return -1;
  }
  else if(queryctrl.flags & V4L2_CTRL_FLAG_DISABLED) {
    return -1;
  }
  else if(!(queryctrl.type & V4L2_CTRL_TYPE_INTEGER)) {
    return -1;
  }
  
  control_s.id = control;
  control_s.value = queryctrl.default_value;
  if(ioctl(c->fd, VIDIOC_S_CTRL, &control_s) < 0) {
    return -1;
  }
  return 0;
}

/*
  Saves RGB information into a file.
 */
void saveRGB(int *info, const char *filename) {
  FILE *fp = fopen(filename, "w");
  int i;
  unsigned char r,g,b;
  fprintf(fp, "P6\n");
  fprintf(fp, "%d %d\n", WIDTH, HEIGHT);
  fprintf(fp, "255\n");
  for(i = 0; i < WIDTH*HEIGHT; ++i) {
    r = (unsigned char)((info[i]>>16)&0xFF);
    g = (unsigned char)((info[i]>>8)&0xFF);
    b = (unsigned char)(info[i]&0xFF);
    fprintf(fp, "%c%c%c", r, g, b);
  }
  fclose(fp);
}

// int main() {
//   char *device = (char *)"/dev/video1";
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
//   colors.push_back(&g.COLOR_GREEN);
//   Position p = g.getCenterOfLargestArea(colors, rgbPicture);
//   saveRGB(rgbPicture, "snap");
//   printf("%d %d\n", p.l, p.c);
//   for(int i = 0; i < 1000; ++i) {
//     capture(&c,rgbPicture);
//     g.findObjectsInImage(rgbPicture);
//     p = g.getCenterOfLargestArea(colors,rgbPicture);
//     saveRGB(rgbPicture, "snap");
//     printf("%d %d\n", p.l, p.c);
//   }
//   free(rgbPicture);
//   closeCam(&c);
// }
