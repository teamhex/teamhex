using namespace std;
#include "pixel.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <deque>

// http://stackoverflow.com/questions/2063709/degree-range-0-360-wrap-around-woes
double angleDistance(double a1, double a2) {
  double t = MAX(a1,a2)-MIN(a1,a2);
  if(t > 180) {
    t = 360-t;
  }
  return t;
}

Position::Position() {}
Position::Position(int line, int column): l(line),c(column) {}

ColorParameters::ColorParameters(int h, int t, int mS): hue(h),tolerance(t),minSize(mS) {}

//Individual Pixel class
Pixel::Pixel(const Position &p, int rgb) {
  hslValues = RGBtoHSL(rgb);
  memcpy(&(this->p), &p, sizeof(Position));
  area = false;
  nNeighbors = 0;
}

void Pixel::addNeighbor(Pixel *neigh) {
  if(neigh != NULL && neigh != this) { // make sure neighbor is valid and isn't self
    neighbors[nNeighbors++] = neigh;
  }
}

void Pixel::setArea() {
  area = true;
}

bool Pixel::inArea() {
  return area;
}

int Pixel::getHue() {
  return hslValues.h;
}

int Pixel::getSat() {
  return hslValues.s;
}

int Pixel::getLight() {
  return hslValues.l;
}

Position Pixel::getPosition() {
  return p;
}

// Pixel grid class
PixelLine::PixelLine(int width, int line) {
  this->width = width;
  this->line = line;
  data = (Pixel *)malloc(sizeof(Pixel)*width);
}

void PixelLine::setPixels(int *rgbLine) {
  Pixel *dataPtr = data;
  Position p;
  p.l = line;
  for(int *i = rgbLine; i < (rgbLine+width); ++i) {
    p.c = i-rgbLine;
    *(dataPtr++) = Pixel(p, *i);
  }
}

Pixel &PixelLine::operator [](int c) {
  return data[c];
}

PixelGrid::PixelGrid(int height, int width) {
  this->width = width;
  this->height = height;
  data = (PixelLine*)malloc(sizeof(PixelLine)*height);
  for(int i = 0; i < height; ++i) {
    data[i] = PixelLine(width, i);
  }
}

void PixelGrid::setNeighbors(const Position &p) {
  Pixel &origin = data[p.l][p.c];
  if(!IS_VALID(p,width,height)) {
    return;
  }
  Position neighbors[NNEIGHBORS] = {
    Position(p.l-1,p.c-1),
    Position(p.l-1,p.c),
    Position(p.l-1,p.c+1),
    Position(p.l,p.c-1),
    Position(p.l,p.c+1),
    Position(p.l+1,p.c-1),
    Position(p.l+1,p.c),
    Position(p.l+1,p.c+1)
  };
  for(int i = 0; i < NNEIGHBORS; ++i) {
    if(IS_VALID(neighbors[i],width,height)) {
      origin.addNeighbor(&(data[neighbors[i].l][neighbors[i].c]));
    }
  }
}

void PixelGrid::setPixels(int *rgbGrid) {
  Position p;
  for(int i = 0; i < height; ++i) {
    data[i].setPixels(rgbGrid);
    rgbGrid += width;
  }
  for(int l = 0; l < height; ++l) {
    for(int c = 0; c < width; ++c) {
      p = Position(l,c);
      setNeighbors(p);
    }
  }
}

PixelLine &PixelGrid::operator [](int l) {
  return data[l];
}

// Area of similar pixels, PixelArea
PixelArea::PixelArea(int hue, Pixel &startPixel, int tolerance) {
  this->hue = hue;
  Position p = startPixel.getPosition();
  minX = p.c;
  maxX = p.c;
  minY = p.l;
  maxY = p.l;
  centerSet = false;
  size = 0;
  pixels = vector<Pixel*>();

  deque<Pixel*> pixelsToTest;
  pixelsToTest.push_back(&startPixel);
  
  Pixel *pixel;
  while (!pixelsToTest.empty()) {
    pixel = pixelsToTest.front();
    pixelsToTest.pop_front();
    
    if (!pixel->inArea() && angleDistance(pixel->getHue(), hue) < tolerance && pixel->getSat() >= 0) {
      pixel->setArea();
      addPixel(pixel);
      for(int i = 0; i < pixel->nNeighbors; ++i) {
	pixelsToTest.push_back(pixel->neighbors[i]);
      }
    }
  }
}

int PixelArea::getSize() {
  return size;
}

Position PixelArea::getCenter() {
  if (!centerSet) {
    center.c = (minX+maxX)/2.0;
    center.l = (minY+maxY)/2.0;
    centerSet = true;
  }
  return center;
}

void PixelArea::addPixel(Pixel *pixel) {
  Position p = pixel->getPosition();
  minX = MIN(p.l,minX);
  maxX = MAX(p.l,maxX);
  minY = MIN(p.c,minY);
  maxY = MAX(p.c,maxY);
  ++size;
  pixels.push_back(pixel);
}

// Search image and find areas with interesting hues
Grabber::Grabber(int w, int h): width(w),height(h),pixels(PixelGrid(h,w)),
				//COLOR_GREEN(ColorParameters(125, 35, 1000)),
				//COLOR_RED(ColorParameters(350, 10, 1000)),
				COLOR_PURPLE(ColorParameters(350, 20, 5000)) {
				//COLOR_YELLOW(ColorParameters(255, 10, 5000)) {

  colorsToFind.push_back(&COLOR_PURPLE);
  //colorsToFind.push_back(&COLOR_GREEN);
  //colorsToFind.push_back(&COLOR_RED);
  //colorsToFind.push_back(&COLOR_YELLOW);
}

vector<PixelArea> Grabber::findObjectsInImage(int *rgb) {
  // Sets the RGB and HSL values for every pixel
  pixels.setPixels(rgb);
  // Finds areas in the picture which are of the same hue
  for (int i = 0; i < width; i++) {
    for (int j = 0; j < height; j++) {
      if (!pixels[j][i].inArea()) {
	for (unsigned int k = 0; k < colorsToFind.size(); k++) {
	  if(angleDistance(pixels[j][i].getHue(), colorsToFind[k]->hue) < colorsToFind[k]->tolerance
	     && pixels[j][i].getSat() >= 0) {
	    PixelArea area = PixelArea(colorsToFind[k]->hue, pixels[j][i], colorsToFind[k]->tolerance);

	    // Only if the area is large enough then we care
	    // about it
	    if (area.getSize() > colorsToFind[k]->minSize) {
	      areas.push_back(area);
	    }
	    break;
	  }
	}
      }
    }
  }
  return areas;
}

Position Grabber::getCenterOfLargestArea(vector<const ColorParameters*> colors, int *rgbPicture) {
  Position centerOfLargestArea = Position(0,0);
  int maxArea = -1;
  PixelArea *largestArea = NULL;
  for (vector<PixelArea>::iterator area = areas.begin(); area != areas.end(); ++area) {
    if (area->getSize() > maxArea) {
      for (vector<const ColorParameters*>::iterator color = colors.begin(); color != colors.end(); ++color) {
	if (area->hue == (*color)->hue) {
	  largestArea = &(*area);
	  centerOfLargestArea = area->getCenter();
	  maxArea = area->getSize();
	  break;
	}
      }
    }
  }
  if(largestArea != NULL) {
    for(vector<Pixel*>::iterator i = largestArea->pixels.begin(); i != largestArea->pixels.end(); ++i) {
      Position p = (*i)->getPosition();
      rgbPicture[p.l*640+p.c] = (255<<16)+(255<<8)+255;
    }
  }
  return centerOfLargestArea;
}

double Grabber::getProportionalHorizontalOffset(int x) {
  return (1.0-x/(width/2.0));
}
