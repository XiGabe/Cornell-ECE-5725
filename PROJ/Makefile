# Modern C++ Makefile for YOLO Hand Detection & Omni-Wheel Robot Control
# Author: Hongxi Chen
# Date: 2025-12-09

# Project configuration
PROJECT_NAME = yolo_hand_detection
TARGET_NAME = main
TEST_TARGET = test_omni

# Directory structure
SRC_DIR = src
INCLUDE_DIR = include
LIB_DIR = lib
BIN_DIR = bin
BUILD_DIR = $(BIN_DIR)/build
RESOURCES_DIR = resources
TESTS_DIR = tests

# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++17 -O3 -Wall -Wextra -Wpedantic
LDFLAGS = -pthread

# Include paths
INCLUDES = -I$(INCLUDE_DIR) -I/usr/include/opencv4 -I/usr/local/include/ncnn

# Libraries
OPENCV_LIBS = `pkg-config --cflags --libs opencv4`
NCNN_LIBS = /usr/local/lib/ncnn/libncnn.a
WIRINGPI_LIBS = -lwiringPi
MATH_LIBS = -lm
THREAD_LIBS = -lpthread -lgomp -ldl

# All libraries together
LIBS = $(OPENCV_LIBS) $(NCNN_LIBS) $(WIRINGPI_LIBS) $(MATH_LIBS) $(THREAD_LIBS)

# Source files by module
DETECTION_SOURCES = $(SRC_DIR)/detection/yolo_detector.cpp
CONTROL_SOURCES = $(SRC_DIR)/control/motor_control.cpp \
                  $(SRC_DIR)/control/omni_control.cpp \
                  $(SRC_DIR)/control/kinematics.cpp
VISION_SOURCES = $(SRC_DIR)/vision/visual_servo.cpp
SYSTEM_SOURCES = $(SRC_DIR)/system/system_monitor.cpp
MAIN_SOURCE = $(SRC_DIR)/main.cpp

TEST_SOURCES = $(TESTS_DIR)/integration_tests/test_omni_movement.cpp

# Object files
DETECTION_OBJECTS = $(BUILD_DIR)/detection/yolo_detector.o
CONTROL_OBJECTS = $(BUILD_DIR)/control/motor_control.o \
                  $(BUILD_DIR)/control/omni_control.o \
                  $(BUILD_DIR)/control/kinematics.o
VISION_OBJECTS = $(BUILD_DIR)/vision/visual_servo.o
SYSTEM_OBJECTS = $(BUILD_DIR)/system/system_monitor.o
MAIN_OBJECT = $(BUILD_DIR)/main.o

TEST_OBJECTS = $(BUILD_DIR)/test_omni_movement.o \
               $(CONTROL_OBJECTS)

# All objects for main target
ALL_OBJECTS = $(DETECTION_OBJECTS) $(CONTROL_OBJECTS) $(VISION_OBJECTS) \
              $(SYSTEM_OBJECTS) $(MAIN_OBJECT)

# Executable paths
TARGET = $(BIN_DIR)/$(TARGET_NAME)
TEST_TARGET_EXE = $(BIN_DIR)/$(TEST_TARGET)

# Default target
.PHONY: all
all: $(TARGET)

# Main executable
$(TARGET): $(ALL_OBJECTS) | $(BIN_DIR)
	@echo "Linking $(TARGET)..."
	$(CXX) $(CXXFLAGS) -o $@ $(ALL_OBJECTS) $(LDFLAGS) $(LIBS)
	@echo "✓ Build successful: $(TARGET)"

# Test executable
$(TEST_TARGET_EXE): $(TEST_OBJECTS) | $(BIN_DIR)
	@echo "Linking $(TEST_TARGET_EXE)..."
	$(CXX) $(CXXFLAGS) -o $@ $(TEST_OBJECTS) $(WIRINGPI_LIBS) $(THREAD_LIBS)
	@echo "✓ Test build successful: $(TEST_TARGET_EXE)"

# Build object files
$(BUILD_DIR)/main.o: $(MAIN_SOURCE) | $(BUILD_DIR)
	@echo "Compiling $<..."
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

$(BUILD_DIR)/detection/%.o: $(SRC_DIR)/detection/%.cpp | $(BUILD_DIR)/detection
	@echo "Compiling $<..."
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

$(BUILD_DIR)/control/%.o: $(SRC_DIR)/control/%.cpp | $(BUILD_DIR)/control
	@echo "Compiling $<..."
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

$(BUILD_DIR)/vision/%.o: $(SRC_DIR)/vision/%.cpp | $(BUILD_DIR)/vision
	@echo "Compiling $<..."
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

$(BUILD_DIR)/system/%.o: $(SRC_DIR)/system/%.cpp | $(BUILD_DIR)/system
	@echo "Compiling $<..."
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

$(BUILD_DIR)/test_omni_movement.o: $(TEST_SOURCES) | $(BUILD_DIR)
	@echo "Compiling $<..."
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Create directories
$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/detection: | $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)/detection

$(BUILD_DIR)/control: | $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)/control

$(BUILD_DIR)/vision: | $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)/vision

$(BUILD_DIR)/system: | $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)/system

# Phony targets
.PHONY: test
test: $(TEST_TARGET_EXE)

.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -f $(TARGET)
	rm -f $(TEST_TARGET_EXE)
	@echo "✓ Clean completed"

.PHONY: clean-all
clean-all: clean
	@echo "Cleaning all generated files..."
	rm -f $(BIN_DIR)/*
	@echo "✓ All files cleaned"

.PHONY: install-deps
install-deps:
	@echo "Installing dependencies..."
	sudo apt-get update
	sudo apt-get install -y \
		build-essential \
		cmake \
		pkg-config \
		libopencv-dev \
		libncnn-dev \
		wiringpi \
		git
	@echo "✓ Dependencies installed"

.PHONY: check-deps
check-deps:
	@echo "Checking dependencies..."
	@pkg-config --exists opencv4 && echo "✓ OpenCV4 found" || echo "✗ OpenCV4 not found"
	@ldconfig -p | grep -q libncnn && echo "✓ NCNN found" || echo "✗ NCNN not found"
	@ldconfig -p | grep -q libwiringPi && echo "✓ WiringPi found" || echo "✗ WiringPi not found"
	@which $(CXX) >/dev/null && echo "✓ $(CXX) found" || echo "✗ $(CXX) not found"

.PHONY: run
run: $(TARGET)
	@echo "Starting YOLO Hand Detection System..."
	@echo "Make sure the camera is connected and motors are safely positioned!"
	cd $(BUILD_DIR) && sudo ../../$(TARGET)

.PHONY: run-test
run-test: $(TEST_TARGET_EXE)
	@echo "Running OmniWheel Test..."
	@echo "Make sure the robot is safely supported!"
	cd $(BUILD_DIR) && sudo ../../$(TEST_TARGET_EXE)

.PHONY: run-test-interactive
run-test-interactive: $(TEST_TARGET_EXE)
	@echo "Running Interactive OmniWheel Test..."
	@echo "Use keyboard commands to control the robot"
	cd $(BUILD_DIR) && sudo ../../$(TEST_TARGET_EXE) interactive

.PHONY: debug
debug: CXXFLAGS += -g -DDEBUG -O0
debug: $(TARGET)

.PHONY: debug-test
debug-test: CXXFLAGS += -g -DDEBUG -O0
debug-test: $(TEST_TARGET_EXE)

.PHONY: release
release: CXXFLAGS += -DNDEBUG -O3 -flto
release: $(TARGET)

.PHONY: format
format:
	@echo "Formatting code..."
	find $(SRC_DIR) -name "*.cpp" -o -name "*.h" | xargs clang-format -i
	find $(INCLUDE_DIR) -name "*.h" | xargs clang-format -i
	find $(TESTS_DIR) -name "*.cpp" -o -name "*.h" | xargs clang-format -i

.PHONY: tidy
tidy:
	@echo "Running clang-tidy..."
	find $(SRC_DIR) -name "*.cpp" | xargs clang-tidy -p $(BUILD_DIR)

.PHONY: valgrind
valgrind: $(TARGET)
	@echo "Running Valgrind memory check..."
	valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes $(TARGET)

.PHONY: benchmark
benchmark: $(TARGET)
	@echo "Running performance benchmark..."
	time $(TARGET)

.PHONY: docs
docs:
	@echo "Generating documentation..."
	doxygen Doxyfile 2>/dev/null || echo "Doxyfile not found. Install doxygen and create Doxyfile."

.PHONY: install
install: $(TARGET)
	@echo "Installing to system..."
	sudo cp $(TARGET) /usr/local/bin/$(PROJECT_NAME)
	sudo mkdir -p /usr/local/share/$(PROJECT_NAME)/models
	sudo cp $(LIB_DIR)/models/* /usr/local/share/$(PROJECT_NAME)/models/
	sudo mkdir -p /usr/local/share/$(PROJECT_NAME)/web
	sudo cp $(RESOURCES_DIR)/web/* /usr/local/share/$(PROJECT_NAME)/web/
	@echo "✓ Installation completed"

.PHONY: uninstall
uninstall:
	@echo "Uninstalling from system..."
	sudo rm -f /usr/local/bin/$(PROJECT_NAME)
	sudo rm -rf /usr/local/share/$(PROJECT_NAME)
	@echo "✓ Uninstallation completed"

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all                 - Build the main project (default)"
	@echo "  test                - Build test programs"
	@echo "  clean               - Remove build artifacts"
	@echo "  clean-all           - Remove all generated files"
	@echo "  install-deps        - Install required dependencies"
	@echo "  check-deps          - Check if dependencies are installed"
	@echo "  run                 - Build and run the main program"
	@echo "  run-test            - Build and run motor test"
	@echo "  run-test-interactive- Run interactive motor test"
	@echo "  debug               - Build with debug symbols"
	@echo "  debug-test          - Build test with debug symbols"
	@echo "  release             - Build optimized release version"
	@echo "  format              - Format source code with clang-format"
	@echo "  tidy                - Run clang-tidy for code analysis"
	@echo "  valgrind            - Run Valgrind memory check"
	@echo "  benchmark           - Run performance benchmark"
	@echo "  docs                - Generate documentation"
	@echo "  install             - Install to system directories"
	@echo "  uninstall           - Remove from system directories"
	@echo "  help                - Show this help message"

# Print configuration
.PHONY: info
info:
	@echo "Project Configuration:"
	@echo "  Name: $(PROJECT_NAME)"
	@echo "  Compiler: $(CXX)"
	@echo "  Flags: $(CXXFLAGS)"
	@echo "  Includes: $(INCLUDES)"
	@echo "  Libraries: $(LIBS)"
	@echo "  Source Directory: $(SRC_DIR)"
	@echo "  Include Directory: $(INCLUDE_DIR)"
	@echo "  Build Directory: $(BUILD_DIR)"
	@echo "  Target: $(TARGET)"