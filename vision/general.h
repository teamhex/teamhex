#ifndef GENERAL_H
#define GENERAL_H

// Parameters
#define WIDTH 640
#define HEIGHT 480
#define BIT7 (0b1111111)

// Useful macros
#define MAX(I,J) ((I)>(J)?(I):(J))
#define MIN(I,J) ((I)<(J)?(I):(J))
#define CLAMP(V) (((V)>255)?255:(((V)<0)?0:(V)))
// Handles 360 degree wrap around and finds the smallest angular distance between two angles.
#define ANGLE_DIST(A1,A2) (((A1)>(A2))?(((A1)-(A2) > 180)?360-((A1)-(A2)):((A1)-(A2))):(((A2)-(A1) > 180)?360-((A2)-(A1)):((A2)-(A1))))

#endif
