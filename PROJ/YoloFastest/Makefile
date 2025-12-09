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
SRCS = mainFV2.cpp yolo-fastestv2.cpp system_monitor.cpp motor_control.cpp visual_servo.cpp omni_motor_control.cpp omni_kinematics.cpp
OMNI_SRCS = omni_motor_control.cpp omni_kinematics.cpp test_omni_movement.cpp

# 目标文件
OBJS = $(SRCS:.cpp=.o)
OMNI_OBJS = $(OMNI_SRCS:.cpp=.o)

# 可执行文件
TARGET = mainFV2
OMNI_TEST = test_omni

# 默认目标
all: $(TARGET)

# 全向轮测试目标
omni-test: $(OMNI_TEST)

# 编译主程序
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS) $(LDFLAGS) $(LIBS)
	@echo "Compilation successful! Executable: $(TARGET)"

# 编译全向轮测试程序 (不依赖OpenCV和NCNN)
$(OMNI_TEST): omni_motor_control.o omni_kinematics.o test_omni_movement.o
	$(CXX) $(CXXFLAGS) -o $(OMNI_TEST) omni_motor_control.o omni_kinematics.o test_omni_movement.o $(WIRINGPI_LIBS) -lpthread
	@echo "Omni test compilation successful! Executable: $(OMNI_TEST)"

# 编译目标文件
%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# 清理
clean:
	rm -f $(OBJS) $(OMNI_OBJS) $(TARGET) $(OMNI_TEST)
	@echo "Cleaned all object files and executables"

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

# 运行全向轮测试
run-omni: $(OMNI_TEST)
	@echo "Running OmniWheel Movement Test..."
	@echo "Make sure the robot is safely supported!"
	sudo ./$(OMNI_TEST)

# 交互式全向轮测试
run-omni-interactive: $(OMNI_TEST)
	@echo "Running Interactive OmniWheel Test..."
	@echo "Use keyboard commands to control the robot"
	sudo ./$(OMNI_TEST) interactive

# 调试版本
debug: CXXFLAGS += -g -DDEBUG
debug: $(TARGET)

# 全向轮调试版本
debug-omni: CXXFLAGS += -g -DDEBUG
debug-omni: $(OMNI_TEST)

# 帮助信息
help:
	@echo "Available targets:"
	@echo "  all              - Compile the main project (default)"
	@echo "  omni-test        - Compile omniwheel test program"
	@echo "  clean            - Remove object files and executables"
	@echo "  install-deps     - Install required dependencies"
	@echo "  check-deps       - Check if dependencies are installed"
	@echo "  run              - Compile and run the main program"
	@echo "  run-omni         - Compile and run omniwheel test"
	@echo "  run-omni-interactive - Run interactive omniwheel test"
	@echo "  debug            - Compile main program with debug symbols"
	@echo "  debug-omni       - Compile omni test with debug symbols"
	@echo "  help             - Show this help message"

.PHONY: all clean install-deps check-deps run run-omni run-omni-interactive debug debug-omni help omni-test