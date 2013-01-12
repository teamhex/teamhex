#ifndef PIXEL_H
#define PIXEL_H

#define IS_VALID(POS,W,H) (((POS).l<(H)) && ((POS).l>=0) && ((POS).c<(W)) && ((POS).c>=0))
#define NNEIGHBORS 8

/** remove **/
extern int hslPicture[HEIGHT][WIDTH];
extern bool visited[HEIGHT][WIDTH];
/** end remove **/

class Position {
 public:
  int l;
  int c;

  Position();
  Position(int line, int column);
};

// Abstract class for creating tests on whether an edge between current and neighbor exists.
class Matcher {
 public:
  virtual bool operator ()(Position *current, Position *neighbor) = 0;
};

// Pixels are included if they're in a specific hue range
class HueMatcher: public Matcher {
private:
  int hue;
  int tolerance;
  
public:
  HueMatcher(int h, int t);
  bool operator ()(Position *current, Position *neighbor);
};

// Pixels are included if they're similar to their neighbors
class GroupMatcher: public Matcher {
private:
  int tolerance;
public:
  GroupMatcher(int t);
  bool operator ()(Position *current, Position *neighbor);
};

extern HueMatcher COLOR_GREEN;
extern HueMatcher COLOR_RED;
extern HueMatcher COLOR_PURPLE;
extern HueMatcher COLOR_YELLOW;

extern GroupMatcher GROUP;

class PixelArea {
 public:
  Position *start;
  int size;
  int hue;
  Position center;
};

// Given a position, set the neighbors array with valid neighboring position
void setNeighbors(Position &p);

// Sets the area starting at position start with pixels obeying matches condition.
void setArea(Position *start, Matcher &matches);

void startNeighbors();

void startHSL(int *rgb);

void findObjectsInImage(Matcher &matches);

PixelArea *getLargestArea();

#endif
