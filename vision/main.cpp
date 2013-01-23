#include <stdio.h>
#include <string>
#include "vision.h"

int main(int argc, char **argv) {
  std::string device = "/dev/maslab_camera";
  if(argc > 1) {
    device = argv[1];
  }
  printf("Starting capture and tracking on device %s\n", device.c_str());
  startCam(device.c_str());
  enableCam();
  for(int i = 0; i < 500; ++i) {
    setPicture();
    //setFilePicture((char *)"/home/rgomes/Dropbox/snapshots2/snap1");
    getInfo();
    printf("%d\n", getNAreas());
    getchar();
  }
  stopCam();
}
