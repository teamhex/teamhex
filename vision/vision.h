extern "C" {
  void startCam(const char *device);
  void enableCam();
  void stopCam();
  void setFilePicture(char *filename);
  void setPicture();
  void getInfo();
  
  struct CPixelArea {
    int pixel;
    int centerL,centerC;
    int topLeftL,topLeftC;
    int bottomRightL,bottomRightC;
    int size;
  };

  int getNAreas();
  void getArea(int i, struct CPixelArea *res);
}
