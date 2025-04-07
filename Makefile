# Makefile for compiling ml-kem-API.cpp

# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -std=c++17 -I./cpp-base64/ -I./asio-1.30.2/include -I./Crow/include -I./liboqs/build/include -I/opt/homebrew/opt/openssl@3/include

# Linker flags
LDFLAGS = -L./liboqs/build/lib -L/opt/homebrew/opt/openssl@3/lib -loqs -lcrypto

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
	