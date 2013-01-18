#ifndef PIXEL_H
#define PIXEL_H

#define IS_VALID(POS,W,H) (((POS).l<(H)) && ((POS).l>=0) && ((POS).c<(W)) && ((POS).c>=0))
#define NNEIGHBORS 8

class Position {
 public:
  int l;
  int c;

  Position();
  Position(int line, int column);
};

class PixelArea {
 public:
  Position *startPosition;
  int startPixel;
  Position topLeft,bottomRight;
  int size;
  Position center;
};

extern PixelArea *areas[WIDTH*HEIGHT];
extern int nAreas;

// Abstract class for creating tests on whether an edge between current and neighbor exists.
class Matcher {
 public:
  virtual bool operator ()(int current, int neighbor) = 0;
  virtual bool operator ()(PixelArea *area) = 0;
};

// Pixels are included if they're in a specific hue range
class HueMatcher: public Matcher {
private:
  int hue;
  int tolerance;
  int minSize;
  int minSat;
  int maxLum;
  
public:
  HueMatcher(int h, int t, int mSize, int mSat, int mLum);
  void fill(HueMatcher **hueVector);
  bool operator ()(int current, int neighbor);
  bool operator ()(PixelArea *area);
};

class MultiHueMatcher: public Matcher {
 private:
  HueMatcher *match[360];
  
 public:
  MultiHueMatcher(HueMatcher **matchers, int nMatchers);
  bool operator ()(int current, int neighbor);
  bool operator ()(PixelArea *area);
};

extern MultiHueMatcher LOOKER;
extern HueMatcher BLUE_WALLS;

// Given a position, set the neighbors array with valid neighboring position
void setNeighbors(Position &p);

// Sets the area starting at position start with pixels obeying matches condition.
void setArea(Position *start, Matcher &matches);

void startNeighbors();

void startHSL(int *rgb);

void findObjectsInImage(Matcher &matches, Matcher &stopMatch);

#endif
