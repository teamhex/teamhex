CC=gcc
CPP=g++
APP_BINARY=mapping
APP_LIB=_mapping.so
WARNINGS = -Wextra

CFLAGS = -std=gnu99
CPPFLAGS = $(WARNINGS) -O3 -fPIC

target debug: CPPFLAGS = $(WARNINGS) -g -fPIC
target debugLibrary: CPPFLAGS = $(WARNINGS) -g -fPIC

OBJECTS= bayesianGrid.o mapping.o motionPlanner.o

all:	app

app:	mapping

debug: clean mapping

debugLibrary: clean library

lib:	library

clean:
	@echo "Cleaning up directory."
	rm -f *.a *.o $(APP_BINARY) core *~ log errlog

# Applications:
mapping:	$(OBJECTS) main.o
	$(CPP) $(OBJECTS) main.o -o $(APP_BINARY) -lpthread

library:$(OBJECTS)
	$(CPP) -shared -Wl,-soname,vision -o _mapping.so $(OBJECTS) -lpthread
