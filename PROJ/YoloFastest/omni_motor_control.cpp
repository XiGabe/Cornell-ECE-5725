#include "omni_motor_control.h"
#include <iostream>
#include <algorithm>
#include <thread>
#include <chrono>
#include <cmath>
#include <wiringPi.h>
#include <softPwm.h>

OmniMotorController::OmniMotorController()
    : initialized(false), current_speeds{0.0f, 0.0f, 0.0f},
      motor1_pins{17, 6, 26, "Motor1"},      // 第一组引脚
      motor2_pins{20, 12, 16, "Motor2"},     // 第二组引脚
      motor3_pins{22, 27, 23, "Motor3"} {    // 第三组引脚
}

OmniMotorController::~OmniMotorController() {
    cleanup();
}

int OmniMotorController::initialize() {
    if (initialized) {
        std::cout << "OmniMotorController already initialized" << std::endl;
        return 0;
    }

    std::cout << "Initializing three-wheel omni motor controller..." << std::endl;

    // 初始化GPIO (复用原有的wiringPi初始化)
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Failed to initialize BCM GPIO - need root permission!" << std::endl;
        return -1;
    }

    // 初始化三个电机的GPIO引脚
    MotorPins motors[] = {motor1_pins, motor2_pins, motor3_pins};

    for (auto& motor : motors) {
        // 设置IN1, IN2为输出
        pinMode(motor.IN1, OUTPUT);
        pinMode(motor.IN2, OUTPUT);

        // 设置软件PWM
        pinMode(motor.PWM, OUTPUT);
        softPwmCreate(motor.PWM, 0, 100);
        softPwmWrite(motor.PWM, 0);

        // 初始状态：所有引脚设为LOW
        digitalWrite(motor.IN1, LOW);
        digitalWrite(motor.IN2, LOW);
        softPwmWrite(motor.PWM, 0);

        std::cout << "Initialized " << motor.name << " motor: "
                  << "IN1=" << motor.IN1 << ", IN2=" << motor.IN2
                  << ", PWM=" << motor.PWM << std::endl;
    }

    // 初始化运动学控制器
    kinematics.initialize(0.05f, 0.15f);
    kinematics.set_speed_limits(1.0f, 3.14159f); // π ≈ 3.14159

    initialized = true;
    std::cout << "Three-wheel omni motor controller initialized successfully!" << std::endl;
    return 0;
}

void OmniMotorController::cleanup() {
    if (!initialized) return;

    std::cout << "Cleaning up omni motor controller..." << std::endl;

    stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    initialized = false;
    std::cout << "Omni motor controller cleanup complete" << std::endl;
}

void OmniMotorController::set_motor_speeds(float m1_speed, float m2_speed, float m3_speed) {
    if (!initialized) {
        std::cerr << "OmniMotorController not initialized!" << std::endl;
        return;
    }

    // 限制速度范围到 [-100, 100] PWM占空比
    current_speeds[0] = std::max(-100.0f, std::min(100.0f, m1_speed));
    current_speeds[1] = std::max(-100.0f, std::min(100.0f, m2_speed));
    current_speeds[2] = std::max(-100.0f, std::min(100.0f, m3_speed));

    set_single_motor(motor1_pins, current_speeds[0]);
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    set_single_motor(motor2_pins, current_speeds[1]);
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    set_single_motor(motor3_pins, current_speeds[2]);
}

void OmniMotorController::stop_all_motors() {
    if (!initialized) return;

    // Removed motor stop logging to reduce console output
    set_motor_speeds(0.0f, 0.0f, 0.0f);

    // 设置所有IN引脚为LOW
    MotorPins motors[] = {motor1_pins, motor2_pins, motor3_pins};
    for (auto& motor : motors) {
        digitalWrite(motor.IN1, LOW);
        digitalWrite(motor.IN2, LOW);
    }

    current_speeds[0] = current_speeds[1] = current_speeds[2] = 0.0f;
}

void OmniMotorController::move_forward(float speed) {
    std::cout << "Moving forward at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_motor_speeds(OmniKinematics::FORWARD, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::move_backward(float speed) {
    std::cout << "Moving backward at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_motor_speeds(OmniKinematics::BACKWARD, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::strafe_left(float speed) {
    std::cout << "Strafing left at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_motor_speeds(OmniKinematics::STRAFE_LEFT, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::strafe_right(float speed) {
    std::cout << "Strafing right at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_motor_speeds(OmniKinematics::STRAFE_RIGHT, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::rotate_left(float speed) {
    std::cout << "Rotating left at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_motor_speeds(OmniKinematics::ROTATE_LEFT, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::rotate_right(float speed) {
    std::cout << "Rotating right at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_motor_speeds(OmniKinematics::ROTATE_RIGHT, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::move_diagonal_fl(float speed) {
    std::cout << "Moving diagonal front-left at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_motor_speeds(OmniKinematics::DIAGONAL_FL, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::move_diagonal_fr(float speed) {
    std::cout << "Moving diagonal front-right at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_motor_speeds(OmniKinematics::DIAGONAL_FR, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::move_diagonal_bl(float speed) {
    std::cout << "Moving diagonal back-left at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_motor_speeds(OmniKinematics::DIAGONAL_BL, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::move_diagonal_br(float speed) {
    std::cout << "Moving diagonal back-right at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_motor_speeds(OmniKinematics::DIAGONAL_BR, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::move_direction(float direction_deg, float speed) {
    std::cout << "Moving in direction " << direction_deg << "° at " << speed << "% speed" << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_direction_speeds(direction_deg, speed / 100.0f);
    apply_motor_speeds(speeds);
}

void OmniMotorController::move_vector(const OmniKinematics::VelocityVector& vel) {
    std::cout << "Moving with vector vx=" << vel.vx << ", vy=" << vel.vy << ", omega=" << vel.omega << std::endl;
    OmniKinematics::MotorSpeeds speeds = kinematics.calculate_vector_speeds(vel);
    apply_motor_speeds(speeds);
}

void OmniMotorController::set_max_speeds(float max_linear, float max_angular) {
    kinematics.set_speed_limits(max_linear, max_angular);
}

OmniKinematics::MoveMode OmniMotorController::get_current_mode() const {
    return kinematics.get_current_mode();
}

void OmniMotorController::get_motor_speeds(float& m1, float& m2, float& m3) const {
    m1 = current_speeds[0];
    m2 = current_speeds[1];
    m3 = current_speeds[2];
}

void OmniMotorController::print_status() const {
    if (!initialized) {
        std::cout << "OmniMotorController: Not initialized" << std::endl;
        return;
    }

    std::cout << "=== OmniMotorController Status ===" << std::endl;
    kinematics.print_status();
    std::cout << "PWM speeds: M1=" << current_speeds[0]
              << "%, M2=" << current_speeds[1]
              << "%, M3=" << current_speeds[2] << "%" << std::endl;
}

void OmniMotorController::print_motor_status() const {
    if (!initialized) {
        std::cout << "Motors not initialized" << std::endl;
        return;
    }

    std::cout << "Motor Status:" << std::endl;
    std::cout << "  Motor1: IN1=" << digitalRead(motor1_pins.IN1)
              << ", IN2=" << digitalRead(motor1_pins.IN2)
              << ", PWM=" << current_speeds[0] << "%" << std::endl;
    std::cout << "  Motor2: IN1=" << digitalRead(motor2_pins.IN1)
              << ", IN2=" << digitalRead(motor2_pins.IN2)
              << ", PWM=" << current_speeds[1] << "%" << std::endl;
    std::cout << "  Motor3: IN1=" << digitalRead(motor3_pins.IN1)
              << ", IN2=" << digitalRead(motor3_pins.IN2)
              << ", PWM=" << current_speeds[2] << "%" << std::endl;
}

void OmniMotorController::set_single_motor(const MotorPins& motor, float speed) {
    // 设置方向
    if (speed > 0) {
        digitalWrite(motor.IN1, HIGH);
        digitalWrite(motor.IN2, LOW);
    } else if (speed < 0) {
        digitalWrite(motor.IN1, LOW);
        digitalWrite(motor.IN2, HIGH);
        speed = -speed; // PWM总是正值
    } else {
        digitalWrite(motor.IN1, LOW);
        digitalWrite(motor.IN2, LOW);
    }

    // 设置PWM
    softPwmWrite(motor.PWM, static_cast<int>(speed));
}

void OmniMotorController::apply_motor_speeds(const OmniKinematics::MotorSpeeds& speeds) {
    // 转换归一化速度 [-1, 1] 到PWM占空比 [0, 100]
    float pwm1 = speed_to_pwm(speeds.motor1);
    float pwm2 = speed_to_pwm(speeds.motor2);
    float pwm3 = speed_to_pwm(speeds.motor3);

    set_motor_speeds(pwm1, pwm2, pwm3);
}

float OmniMotorController::speed_to_pwm(float normalized_speed) {
    // 限制输入范围
    normalized_speed = std::max(-1.0f, std::min(1.0f, normalized_speed));

    // 转换到PWM占空比 [0, 100]，使用最大速度的95%以获得更高速度
    return normalized_speed * 95.0f;
}

// 全局控制器实例
OmniMotorController omni_controller;

// 兼容性函数实现
void set_omni_motor_speeds(float m1_speed, float m2_speed, float m3_speed) {
    omni_controller.set_motor_speeds(m1_speed, m2_speed, m3_speed);
}

void stop_all_omni_motors() {
    omni_controller.stop_all_motors();
}

void omni_move_forward(float speed) {
    omni_controller.move_forward(speed);
}

void omni_move_backward(float speed) {
    omni_controller.move_backward(speed);
}