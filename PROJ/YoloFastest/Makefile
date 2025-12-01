# Makefile for YOLO + Motor Control System
# 原型1: 视觉伺服跟手系统

# 编译器和选项
CXX = g++
CXXFLAGS = -std=c++11 -O3 -Wall -Wextra
LDFLAGS = -pthread

# OpenCV 库
OPENCV_LIBS = `pkg-config --cflags --libs opencv4`
# 如果上面的不行，试试这个：
OPENCV_LIBS_MANUAL = -I/usr/include/opencv4 -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lopencv_videoio

# NCNN 库 (需要根据你的安装路径调整)
NCNN_LIBS = /usr/local/lib/ncnn/libncnn.a
NCNN_INCLUDES = -I/usr/local/include/ncnn

# WiringPi 库
WIRINGPI_LIBS = -lwiringPi

# 包含路径
INCLUDES = $(NCNN_INCLUDES) -I/usr/include/opencv4 -I.

# 库路径
LIBS = $(OPENCV_LIBS) $(NCNN_LIBS) $(WIRINGPI_LIBS) -lgomp -lpthread

# 源文件
SRCS = mainFV2.cpp yolo-fastestv2.cpp system_monitor.cpp motor_control.cpp visual_servo.cpp

# 目标文件
OBJS = $(SRCS:.cpp=.o)

# 可执行文件
TARGET = mainFV2

# 默认目标
all: $(TARGET)

# 编译可执行文件
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS) $(LDFLAGS) $(LIBS)
	@echo "Compilation successful! Executable: $(TARGET)"

# 编译目标文件
%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# 清理
clean:
	rm -f $(OBJS) $(TARGET)
	@echo "Cleaned all object files and executable"

# 安装依赖 (Ubuntu/Debian)
install-deps:
	@echo "Installing dependencies..."
	sudo apt-get update
	sudo apt-get install -y libopencv-dev libncnn-dev wiringpi
	@echo "Dependencies installed!"

# 检查依赖
check-deps:
	@echo "Checking dependencies..."
	@pkg-config --exists opencv4 && echo "✓ OpenCV4 found" || echo "✗ OpenCV4 not found"
	@ldconfig -p | grep -q libncnn && echo "✓ NCNN found" || echo "✗ NCNN not found"
	@ldconfig -p | grep -q libwiringPi && echo "✓ WiringPi found" || echo "✗ WiringPi not found"

# 运行程序
run: $(TARGET)
	@echo "Running YOLO + Motor Control System..."
	@echo "Make sure motors are safely supported!"
	sudo ./$(TARGET)

# 调试版本
debug: CXXFLAGS += -g -DDEBUG
debug: $(TARGET)

# 帮助信息
help:
	@echo "Available targets:"
	@echo "  all         - Compile the project (default)"
	@echo "  clean       - Remove object files and executable"
	@echo "  install-deps- Install required dependencies"
	@echo "  check-deps  - Check if dependencies are installed"
	@echo "  run         - Compile and run the program"
	@echo "  debug       - Compile with debug symbols"
	@echo "  help        - Show this help message"

.PHONY: all clean install-deps check-deps run debug help