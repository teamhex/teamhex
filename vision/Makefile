CC=gcc
CPP=g++
APP_BINARY=vision
APP_LIB=vision.so
WARNINGS = -Wextra

CFLAGS = -std=gnu99
CPPFLAGS = $(WARNINGS) -O3

target library: CPPFLAGS = $(WARNINGS) -O3 -fPIC

OBJECTS= colors.o capture.o pixel.o vision.o


all:	app

app:	vision

lib:	library

clean:
	@echo "Cleaning up directory."
	rm -f *.a *.o $(APP_BINARY) core *~ log errlog

# Applications:
vision:	$(OBJECTS) main.o
	$(CPP) $(OBJECTS) main.o -o $(APP_BINARY)

library:$(OBJECTS)
	$(CPP) -shared -Wl,-soname,vision -o vision.so $(OBJECTS)
