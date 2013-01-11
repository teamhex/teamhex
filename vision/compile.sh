#!/bin/sh
g++ -shared -Wl,-soname,capture -o capture.so -fPIC capture.cpp colors.c pixel.cpp vision.c
