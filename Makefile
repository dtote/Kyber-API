# Makefile for compiling ml-kem-API.cpp

# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -std=c++17 -I./cpp-base64/ -I./asio-1.30.2/include -I./Crow/include 

# Linker flags
LDFLAGS = -L./liboqs/build/lib -loqs -lcrypto -pthread

# Target executable
TARGET = mlKemAPIDil

# Source file
SRC = ./ml-kem-API.cpp ./cpp-base64/base64.cpp

# Build rules
all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(SRC) $(CXXFLAGS) $(LDFLAGS) -o $(TARGET)

clean:
	rm -f $(TARGET)
	