CXX=g++
CXXFLAGS=-pthread -Wall -Wno-switch -Wpedantic -Wno-unused-function -std=c++17
ROOT_DIR=CppClient
BASE_SRC_DIR=${ROOT_DIR}/client/
INCLUDES=-I${BASE_SRC_DIR} #-I${ROOT_DIR}
SHARED_LIB_DIRS=${ROOT_DIR}/lib
SHARD_LIBS=TwsSocketClient.lib
TARGET=main

#$(BASE_SRC_DIR)/lib/libbid.lib

# $(TARGET):
# 	$(CXX) $(CXXFLAGS) $(INCLUDES) ./*.cpp $(BASE_SRC_DIR)/lib/libbid.lib $(SHARED_LIB_DIRS)/$(SHARD_LIBS) -o$(TARGET)

$(TARGET):
	$(CXX) $(CXXFLAGS) $(INCLUDES) ./*.cpp $(BASE_SRC_DIR)/lib/libbid.so -o$(TARGET)

clean:
	rm -f $(TARGET) $(TARGET)Static *.o

# CXX=g++
# CXXFLAGS=-DIB_USE_STD_STRING -Wall -Wno-switch
# ROOT_DIR=/home/rholowczak/ib/IBJts
# BASE_SRC_DIR=${ROOT_DIR}/source/PosixClient/src
# INCLUDES=-I${ROOT_DIR}/source/PosixClient/Shared/ -I${BASE_SRC_DIR}
# TARGET=PosixSocketClientTest

# $(TARGET):
#     $(CXX) $(CXXFLAGS) $(INCLUDES) -o EClientSocketBase.o -c $(BASE_SRC_DIR)/EClientSocketBase.cpp
#     $(CXX) $(CXXFLAGS) $(INCLUDES) -o EPosixClientSocket.o -c $(BASE_SRC_DIR)/EPosixClientSocket.cpp
#     $(CXX) $(CXXFLAGS) $(INCLUDES) -o PosixTestClient.o -c PosixTestClient.cpp
#     $(CXX) $(CXXFLAGS) $(INCLUDES) -o Main.o -c Main.cpp
#     $(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ EClientSocketBase.o EPosixClientSocket.o PosixTestClient.o Main.o

# clean:
#     rm -f $(TARGET) *.o