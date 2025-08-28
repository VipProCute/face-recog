# CROSS_COMPILE=""
CC=$(CROSS_COMPILE)gcc
CXX=$(CROSS_COMPILE)g++

DEBUG=0

# OPENCV_INCLUDE=opencv/include
# OPENCV_LIB=opencv/lib

# VIVANTE_SDK_DIR=/home/nhantran/VeriSilicon/VivanteIDE5.10.1/cmdtools/vsimulator
# VIVANTE_SDK_DIR=./vip9000sdk-6.4.15.9/6.4.15.9

INCLUDES=-I. -I$(VIVANTE_SDK_DIR)/include/ \
 -I$(VIVANTE_SDK_DIR)/include/CL \
 -I$(VIVANTE_SDK_DIR)/include/VX \
 -I$(VIVANTE_SDK_DIR)/include/ovxlib \
 -I$(VIVANTE_SDK_DIR)/include/ovxlib/utils \
 -I$(VIVANTE_SDK_DIR)/include/ovxlib/ops \
 -I$(VIVANTE_SDK_DIR)/include/jpeg
#   $(shell pkg-config opencv4 --cflags) \

INCLUDES += -I$(OPENCV_INCLUDE)

CFLAGS=-Wall -std=c++0x $(INCLUDES) -D__linux__ -DLINUX -fpermissive -fopenmp
CFLAGS+=-O3
CFLAGS+=-shared -fpic
LFLAGS+=-O3 -Wl,-rpath-link=$(VIVANTE_SDK_DIR)/drivers
LFLAGS+=-Wl,-rpath-link=$(OPENCV_LIB)

LIBS+= -L$(VIVANTE_SDK_DIR)/drivers \
 -lOpenVX -lOpenVXU -lovxlib -ljpeg -lm -lstdc++ #$(shell pkg-config opencv4 --libs)

LIBS += -lopencv_core -lopencv_imgproc -lopencv_videoio -lopencv_dnn -lopencv_objdetect -lopencv_imgcodecs -lopencv_highgui
LIBS += -L$(OPENCV_LIB)

SRCS=${wildcard *.c}
SRCS+=${wildcard *.cpp}

BIN=main
SHARED_LIB=libFaceRecog_wrapper.so

OBJS=$(addsuffix .o, $(basename $(SRCS)))

.SUFFIXES: .cpp .c

.cpp.o:
	$(CC) $(CFLAGS) -c $<

.cpp:
	$(CXX) $(CFLAGS) $< -o $@ -lm

.c.o:
	$(CC) $(CFLAGS) -c $<

.c:
	$(CC) $(CFLAGS) $< -o $@ -lm

# all: $(BIN)
all: $(SHARED_LIB)

$(BIN): $(OBJS)
	$(CXX) $(CFLAGS) $(LFLAGS) $(EXTRALFLAGS) $(OBJS) $(LIBS) -o $@

$(SHARED_LIB): $(OBJS)
	$(CXX) $(CFLAGS) $(LFLAGS) $(EXTRALFLAGS) $(OBJS) $(LIBS) -o $@

clean:
	rm -rf *.o
	rm -rf $(BIN) $(SHARED_LIB)
	rm -rf *~
