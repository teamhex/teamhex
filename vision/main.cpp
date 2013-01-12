#include <stdio.h>
#include <string>
#include "vision.h"

int main(int argc, char **argv) {
  std::string device = "/dev/video1";
  if(argc > 1) {
    device = argv[1];
  }
  printf("Starting capture and tracking on device %s\n", device.c_str());
  startCam(device.c_str());
  enableCam();
  for(int i = 0; i < 500; ++i) {
    getInfo();
    printf("%d %d\n", getX(), getSize());
    //getchar();
  }
  stopCam();
}
