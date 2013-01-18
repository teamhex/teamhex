#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <opencv/cv.h>
#include <opencv/highgui.h>

using namespace std;
using namespace cv;

int main()
{
  namedWindow("output", CV_GUI_NORMAL);

  char *filename = (char *)"/home/rgomes/Dropbox/snapshots2/snap1\0\0\0";

  IplImage *src = cvLoadImage(filename);
  IplImage *imgHSV = cvCreateImage(cvGetSize(src), 8, 3);
  cvCvtColor(src, imgHSV, CV_RGB2HSV);
  IplImage *imgThreshed = cvCreateImage(cvGetSize(src), 8, 1);
  cvInRangeS(imgHSV, cvScalar(30,0,0), cvScalar(60,255, 255), imgThreshed);

  int x =0;
  for(;;) {
    cvShowImage("output", imgThreshed);
    waitKey(0);
  }
}
  
  
//         const char      * wndName = "Source image",
//                                 * wndNameGray = "Gray img", 
//                                 * wndNameOut = "Out",
//                                 * filename = "/home/rgomes/Dropbox/snapshots2/snap1\0\0\0";

//         Mat src, gray, thresh, binary;
//         Mat out;
//         vector<KeyPoint> keyPoints;
//         vector< vector <Point> > contours;
//         vector< vector <Point> > approxContours;

//         SimpleBlobDetector::Params params;
//         params.minThreshold = 40;
//         params.maxThreshold = 60;
//         params.thresholdStep = 5;

//         params.minArea = 100; 
//         params.minConvexity = 0.3;
//         params.minInertiaRatio = 0.01;

//         params.maxArea = 10000000;
//         params.maxConvexity = 10;

//         params.filterByColor = false;
//         params.filterByCircularity = false;

//         namedWindow( wndNameOut, CV_GUI_NORMAL );

//         //line( src, Point(0, src.rows-1), Point( src.cols-1, src.rows-1 ), Scalar::all(255) );

//         SimpleBlobDetector blobDetector( params );
//         blobDetector.create("SimpleBlob");

//         for(int i = 1; i < 3000; ++i)
//         {
// 	  //snprintf(filename, "/home/rgomes/Dropbox/snapshots2/snap%d", i);
// 	  blobDetector.detect( src, keyPoints );
// 	  //blobDetector.detectEx( src, keyPoints, contours );
// 	  drawKeypoints( src, keyPoints, out, CV_RGB(0,255,0), DrawMatchesFlags::DEFAULT);
// 	  //approxContours.resize( contours.size() );

//                 for( int i = 0; i < contours.size(); ++i )
//                 {
// 		  //approxPolyDP( Mat(contours[i]), approxContours[i], 4, 1 );
// 		  //drawContours( out, contours, i, CV_RGB(rand()&255, rand()&255, rand()&255) );

// 		  //drawContours( out, approxContours, i, CV_RGB(rand()&255, rand()&255, rand()&255) );
//                 }
//                 cout << "Keypoints " << keyPoints.size() << endl;
        
//                 imshow( wndNameOut, out );
//                 waitKey(0);
//         }
// }
