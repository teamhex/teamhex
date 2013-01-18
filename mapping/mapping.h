extern "C" {
  // Always call robotPositioned first! Otherwise most other functions will use the wrong robot position.
  void robotPositioned(int robotX, int robotY);
  void wallDetected(int wallX, int wallY);
  void wallNotDetected(int sensorLimitX, int sensorLimitY);
  void ballDetected(int ballX, int ballY, int ballColor);
  void specialWall(int wallX, int wallY, int wallType);

  
}
