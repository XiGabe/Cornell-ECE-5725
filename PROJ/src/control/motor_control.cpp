#include "control/motor_control.h"
#include <wiringPi.h>
#include <softPwm.h>
#include <iostream>
#include <chrono>
#include <thread>
#include <unistd.h>

// 引脚配置 (直接使用BCM编号，完全对应motor_test.py)
// Python (BCM):  Left: {5, 6, 26}, Right: {20, 12, 16}
// C++ (BCM):     Left: {5, 6, 26}, Right: {20, 12, 16}
MotorPins MOTOR_LEFT = {5, 6, 26, "Left"};      // BCM: 5, 6, 26
MotorPins MOTOR_RIGHT = {20, 12, 16, "Right"};   // BCM: 20, 12, 16

// 控制参数
const int PWM_FREQUENCY_HZ = 100;
const float MAX_SPEED_DC = 95.0;  // 与Python测试代码一致

// 内部状态变量
static bool motors_initialized = false;

// GPIO和PWM初始化
int init_motors() {
    if (motors_initialized) {
        std::cout << "Motors already initialized" << std::endl;
        return 0;
    }

    std::cout << "Initializing GPIO and motor control..." << std::endl;

    // 初始化wiringPi (使用BCM模式，与Python一致)
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Failed to initialize BCM GPIO - 需要root权限!" << std::endl;
        return -1;
    }

    // 检查权限
    if (geteuid() != 0) {
        std::cout << "警告: 非root用户运行，GPIO控制可能无效" << std::endl;
    } else {
        std::cout << "✓ root权限，GPIO控制应该正常" << std::endl;
    }

    // 设置电机引脚
    MotorPins motors[] = {MOTOR_LEFT, MOTOR_RIGHT};

    for (auto& motor : motors) {
        // 设置IN1, IN2为输出
        pinMode(motor.IN1, OUTPUT);
        pinMode(motor.IN2, OUTPUT);

        // 设置PWM - 使用softPwm (软件PWM)
        pinMode(motor.PWM, OUTPUT);
        softPwmCreate(motor.PWM, 0, 100);  // 初始值0，范围0-100
        softPwmWrite(motor.PWM, 0);  // 初始为0

        // 初始状态：所有引脚设为LOW
        digitalWrite(motor.IN1, LOW);
        digitalWrite(motor.IN2, LOW);
        softPwmWrite(motor.PWM, 0);

        std::cout << "Initialized " << motor.name << " motor: "
                  << "IN1=" << motor.IN1 << ", IN2=" << motor.IN2
                  << ", PWM=" << motor.PWM << std::endl;
    }

    motors_initialized = true;
    std::cout << "Motor initialization complete" << std::endl;
    return 0;
}

// 清理资源
void cleanup_motors() {
    if (!motors_initialized) return;

    std::cout << "Cleaning up motor control..." << std::endl;

    stop_all_motors();

    // 延迟一下确保停止
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    motors_initialized = false;
    std::cout << "Motor cleanup complete" << std::endl;
}

// 设置单个电机方向
void set_motor_direction(const MotorPins& motor, int direction) {
    if (!motors_initialized) {
        std::cerr << "Motors not initialized!" << std::endl;
        return;
    }

    switch (direction) {
        case 1:  // CW (正转)
            digitalWrite(motor.IN1, HIGH);
            digitalWrite(motor.IN2, LOW);
            break;
        case -1: // CCW (反转)
            digitalWrite(motor.IN1, LOW);
            digitalWrite(motor.IN2, HIGH);
            break;
        case 0:  // STOP (停止)
        default:
            digitalWrite(motor.IN1, LOW);
            digitalWrite(motor.IN2, LOW);
            break;
    }
}

// 设置单个电机速度
void set_motor_speed(const MotorPins& motor, float speed_dc) {
    if (!motors_initialized) {
        std::cerr << "Motors not initialized!" << std::endl;
        return;
    }

    // 限制速度范围
    if (speed_dc < 0) speed_dc = 0;
    if (speed_dc > MAX_SPEED_DC) speed_dc = MAX_SPEED_DC;

    std::cout << "设置 " << motor.name << " 电机速度: " << (int)speed_dc << "%" << std::endl;
    softPwmWrite(motor.PWM, (int)speed_dc);
}

// 设置双电机速度
void set_motor_speeds(float left_speed, float right_speed) {
    set_motor_speed(MOTOR_LEFT, left_speed);
    // 添加小延迟确保PWM稳定
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    set_motor_speed(MOTOR_RIGHT, right_speed);
}

// 停止所有电机
void stop_all_motors() {
    if (!motors_initialized) return;

    std::cout << "Stopping all motors..." << std::endl;

    // 停止PWM输出
    set_motor_speeds(0, 0);

    // 设置所有IN引脚为LOW
    set_motor_direction(MOTOR_LEFT, 0);
    set_motor_direction(MOTOR_RIGHT, 0);

    std::cout << "All motors stopped" << std::endl;
}

// 前进
void move_forward(float speed) {
    std::cout << "Moving forward at " << speed << "% speed" << std::endl;
    // 先设置方向
    set_motor_direction(MOTOR_LEFT, 1);    // CW
    set_motor_direction(MOTOR_RIGHT, 1);   // CW
    // 添加小延迟确保方向设置稳定
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    // 然后设置速度
    set_motor_speeds(speed, speed);
}

// 后退
void move_backward(float speed) {
    std::cout << "Moving backward at " << speed << "% speed" << std::endl;
    set_motor_direction(MOTOR_LEFT, -1);   // CCW
    set_motor_direction(MOTOR_RIGHT, -1);  // CCW
    set_motor_speeds(speed, speed);
}

// 左转 (右轮快，左轮慢)
void turn_left(float speed) {
    std::cout << "Turning left at " << speed << "% speed" << std::endl;
    set_motor_direction(MOTOR_LEFT, 1);    // CW
    set_motor_direction(MOTOR_RIGHT, 1);   // CW
    set_motor_speeds(speed * 0.3, speed);  // 左轮慢，右轮快
}

// 右转 (左轮快，右轮慢)
void turn_right(float speed) {
    std::cout << "Turning right at " << speed << "% speed" << std::endl;
    set_motor_direction(MOTOR_LEFT, 1);    // CW
    set_motor_direction(MOTOR_RIGHT, 1);   // CW
    set_motor_speeds(speed, speed * 0.3);  // 左轮快，右轮慢
}

// 原地左转
void rotate_left(float speed) {
    std::cout << "Rotating left in place at " << speed << "% speed" << std::endl;
    set_motor_direction(MOTOR_LEFT, -1);   // CCW
    set_motor_direction(MOTOR_RIGHT, 1);   // CW
    set_motor_speeds(speed, speed);
}

// 原地右转
void rotate_right(float speed) {
    std::cout << "Rotating right in place at " << speed << "% speed" << std::endl;
    set_motor_direction(MOTOR_LEFT, 1);    // CW
    set_motor_direction(MOTOR_RIGHT, -1);  // CCW
    set_motor_speeds(speed, speed);
}

// 打印电机状态
void print_motor_status() {
    if (!motors_initialized) {
        std::cout << "Motors not initialized" << std::endl;
        return;
    }

    std::cout << "Motor Status:" << std::endl;
    std::cout << "  Left Motor:  IN1=" << digitalRead(MOTOR_LEFT.IN1)
              << ", IN2=" << digitalRead(MOTOR_LEFT.IN2)
              << ", PWM=" << MOTOR_LEFT.PWM << std::endl;
    std::cout << "  Right Motor: IN1=" << digitalRead(MOTOR_RIGHT.IN1)
              << ", IN2=" << digitalRead(MOTOR_RIGHT.IN2)
              << ", PWM=" << MOTOR_RIGHT.PWM << std::endl;
}