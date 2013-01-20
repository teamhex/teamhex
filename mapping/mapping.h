extern "C" {
  struct CPosition {
    double x;
    double y;
  };
  
  // Always call robotPositioned first! Otherwise most other functions will use the wrong robot position.
  void initMapping();
  void robotPositioned(double robotX, double robotY);
  void wallDetected(double wallX, double wallY);
  void wallNotDetected(double sensorLimitX, double sensorLimitY);
  void ballDetected(double ballX, double ballY, int ballColor);
  void specialWall(double wallX, double wallY, int wallType);
  void closestBall(CPosition *res);

  void setConfigSpace();
  void goPlan(double goalX, double goalY);
  int getPlanLength();
  void getPlanWP(int wpI, CPosition *WP);

  void printCells();

  int getWall(int x, int y);
}
