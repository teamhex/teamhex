#ifndef PIXEL_H
#define PIXEL_H

using namespace std;
#include "colors.h"
#include <vector>
#define IS_VALID(POS,W,H) (((POS).l<(H)) && ((POS).l>=0) && ((POS).c<(W)) && ((POS).c>=0))
#define NNEIGHBORS 8

struct Position {
  long l;
  long c;

  Position();
  Position(int line, int column);
};

struct ColorParameters {
  const int hue;
  const int tolerance;
  const int minSize;

  ColorParameters(int h, int t, int mS);
};

class Pixel {
 private:
  bool area;
  struct hsl hslValues;
  Position p;

 public:
  bool inQueue;
  Pixel *neighbors[NNEIGHBORS];
  int nNeighbors;

  Pixel(const Position &p, int rgb);
  void addNeighbor(Pixel *neigh);
  void setArea();
  bool inArea();

  int getHue();
  int getSat();
  int getLight();
  struct hsl getHSL();
  
  Position getPosition();
};

// Pixel grid class
class PixelLine {
 private:
  int width, line;
  Pixel *data;

 public:
  PixelLine(int width, int line);
  void setPixels(int *rgbLine);
  Pixel &operator [](int c);
};

class PixelGrid {
 private:
  int width, height;
  PixelLine *data;
  
  void setNeighbors(const Position &p);

 public:
  PixelGrid(int height, int width);
  void setPixels(int *rgbGrid);
  PixelLine &operator [](int l);
};

// Area of similar pixels
class PixelArea {
 private:
  int size;
  Position center;
  bool centerSet;
  vector<Pixel> pixels;

 public:
  int hue;
  int minX, maxX, minY, maxY;

  PixelArea();
  PixelArea(int hue, Pixel &startPixel, int tolerance);
  PixelArea(Pixel &startPixel, int maxDiff);
  int getSize();
  Position getCenter();
  void addPixel(Pixel *pixel);
  void color(int *rgbPicture, int color);
};

// Search image and find areas with interesting hues.
class Grabber {
 private:
  const int width, height;
  PixelGrid pixels;
  vector<const ColorParameters*> colorsToFind;
  PixelArea *largestArea;
  
 public:
  vector<PixelArea*> areas;
  const ColorParameters COLOR_GREEN;
  const ColorParameters COLOR_RED;
  const ColorParameters COLOR_PURPLE;
  const ColorParameters COLOR_YELLOW;
  Grabber(int w, int h);

  void findObjectsInImage(int *rgb);
  
  PixelArea *getLargestArea();
  double getProportionalHorizontalOffset(int x);
};


#endif
