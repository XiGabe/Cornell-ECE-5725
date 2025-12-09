# YOLO Hand Detection & Omni-Wheel Robot Control

A modern C++ computer vision system that combines YOLO-based hand detection with omni-directional robot control for real-time visual servoing applications.

---

## 🎯 Features

- **Real-time Hand Detection**: Uses YOLO-FastestV2 for efficient hand detection
- **Omni-directional Movement**: Three-wheel kinematics for smooth 360° movement
- **Visual Servoing**: Intelligent robot control based on visual feedback
- **Web Interface**: Live camera streaming and system status via web browser
- **Modern Architecture**: Clean, modular C++17 codebase with professional build system

---

## 🚀 Quick Start

### 1. Build the Project
```bash
make
```

### 2. Run the Application
```bash
./scripts/run.sh
```

### 3. Access Web Interface
Open browser and navigate to: `http://<your-pi-ip>:8080`

---

## 📁 Project Structure

```
PROJ/
├── src/                    # Source code
│   ├── main.cpp           # Main application entry point
│   ├── detection/         # YOLO hand detection module
│   ├── control/           # Motor and kinematics control
│   ├── vision/            # Visual servoing algorithms
│   └── system/            # System monitoring
├── include/               # Header files
├── lib/models/           # AI model files
├── resources/web/        # Web interface files
├── bin/                  # Compiled executables
└── scripts/              # Helper scripts
```

---

## 🛠️ Dependencies

### System Requirements
- **OS**: Linux (tested on Raspberry Pi OS)
- **Compiler**: GCC 7+ with C++17 support
- **Architecture**: ARM64/x86_64

### Libraries
- **OpenCV 4.x**: Computer vision and image processing
- **NCNN**: Neural network inference framework
- **WiringPi**: GPIO control for Raspberry Pi

### Install Dependencies
```bash
make install-deps
```

---

## 🎮 Usage

### Basic Commands
```bash
# Build the project
make

# Run main application
./scripts/run.sh

# Test motor control
make run-test

# Clean build artifacts
make clean

# Show all available commands
make help
```

### Web Interface Features
- **Live Video**: MJPEG streaming (30 FPS)
- **System Monitoring**: CPU, memory, temperature display
- **API Endpoints**: `/system-info` for system status JSON

---

## ⚙️ Configuration

### Motor Pin Configuration
```cpp
// GPIO pins for three motors (BCM numbering)
Motor1: {IN1=17, IN2=6, PWM=26}
Motor2: {IN1=20, IN2=12, PWM=16}
Motor3: {IN1=22, IN2=27, PWM=23}
```

### Detection Parameters
- Confidence threshold: 0.6
- Input resolution: 416x416
- Detection class: Hand

---

## 🔧 Troubleshooting

### Common Issues

**Camera not detected**
```bash
ls /dev/video*  # Check camera devices
```

**GPIO permission issues**
```bash
sudo usermod -a -G gpio $USER  # Add user to gpio group
```

**Compilation errors**
```bash
make check-deps    # Check dependencies
make install-deps  # Install missing dependencies
```

---

## 📊 Performance

### Benchmarks (Raspberry Pi 4)
- **Detection Speed**: 25-30 FPS
- **Web Latency**: <50ms
- **Memory Usage**: ~150MB
- **CPU Usage**: 60-80%

---

## 🔧 Development

### Build Modes
```bash
# Debug build
make debug

# Release build (optimized)
make release

# Build tests
make test
```

### Code Quality
```bash
# Format code
make format

# Run static analysis
make tidy
```

---

## 📚 API Reference

### REST Endpoints
- `GET /stream` - MJPEG video stream
- `GET /system-info` - System status JSON
- `GET /` - Web interface

### Key Classes
- `yoloFastestv2` - Hand detection engine
- `VisualServoController` - Visual servoing control
- `OmniMotorController` - Omni-directional motor control
- `SystemMonitor` - System performance monitoring

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation

---

## 📜 License

This project is licensed under the BSD 3-Clause License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **NCNN Framework**: Tencent's neural network inference framework
- **OpenCV**: Open Source Computer Vision Library
- **WiringPi**: GPIO control library for Raspberry Pi
- **YOLO**: Real-time object detection system

---

**Author**: Hongxi Chen
**Date**: 2025-12-09
**Version**: 2.0