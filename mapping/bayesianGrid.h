#ifndef BAYESIAN_GRID_H
#define BAYESIAN_GRID_H

#define P_DETECT_GIVEN_BALL 0.999
#define P_DETECT_GIVEN_NBALL 0.01
#define P_DETECT_GIVEN_WALL 0.99
#define P_DETECT_GIVEN_NWALL 0.01

#define PRIOR_BALL 0.2
#define PRIOR_WALL 0.3

#define NORMAL_WALL 0
#define YELLOW_WALL 1
#define PURPLE_WALL 2
#define BLACK_WALL 3

#define RED_BALL 4
#define GREEN_BALL 5

#define ROBOT_BODY 6

#define WALL_THRESHOLD 0.8
#define BALL_THRESHOLD 0.8

#define isWall(C) ((C).pWall > WALL_THRESHOLD)
#define isBall(C) ((C).pBall > BALL_THRESHOLD)
#define isValid(P) (((P).l >= 0 && (P).l < HEIGHT) && ((P).c >= 0 && (P).c < WIDTH))

#define WIDTH 300
#define HEIGHT 300
#define REAL_WIDTH 450.0
#define REAL_HEIGHT 450.0
#define CELL_WIDTH ((double)REAL_WIDTH/(double)WIDTH)
#define CELL_HEIGHT ((double)REAL_HEIGHT/(double)HEIGHT)

#define BALL_RADIUS 1.25
#define ROBOT_RADIUS 7.0
#define FIELD_DIAMETER 640

#define NNEIGHBORS 8

#define MAX(I,J) ((I)>(J)?(I):(J))
#define MIN(I,J) ((I)<(J)?(I):(J))

// Grid defined the following way:
//   Top left corner is (0,0) in real coordinates.
//   The coordinates of a grid cell are defined by its top left vertex.

struct Cell {
  double pBall;
  double pWall;
  int ballType;
  int wallType;
  bool visited;
};

struct Position {
  int l;
  int c;

  Position();
  Position(int line, int column);
};

struct RealPosition {
  double x;
  double y;
};

// Given p(X) (prior) and p(D\X), p(D\~X), and whether D or ~D happened, return new p(X)
// D is an event, X is a random variable.
double bayesianUpdate(double prior, double pDGivenX, double pDGivenNX, bool dHappened);

Position realToGrid(RealPosition &real);
RealPosition gridToReal(Position &grid);
double distanceSqr(Position &p1, Position &p2);

void setNeighbors(Position &p);
void bfsMark(int type, bool detect, Position &start, int radius);

void sensorUpdate(int type, bool detect, RealPosition &worldPos, RealPosition &robotPos);
bool setWallType(int type, RealPosition &orientation, RealPosition &robotPos);

void initialize();

void printMap();

extern Position *allNeighbors[HEIGHT][WIDTH][NNEIGHBORS];
extern int allnNeighbors[HEIGHT][WIDTH];

extern Cell theMap[HEIGHT][WIDTH];

#endif
