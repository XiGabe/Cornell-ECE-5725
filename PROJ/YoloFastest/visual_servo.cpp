#include "visual_servo.h"
#include <iostream>
#include <algorithm>
#include <cmath>

VisualServoController::VisualServoController()
    : initialized(false), frame_width(640), frame_height(480),
      target_x(320.0f), target_y(240.0f),
      dead_zone_x(50.0f), dead_zone_y(50.0f),
      last_error_x(0.0f), last_error_y(0.0f),
      integral_x(0.0f), integral_y(0.0f),
      kp_linear(1.0f), ki_linear(0.1f), kd_linear(0.05f),
      kp_angular(1.5f), ki_angular(0.0f), kd_angular(0.1f) {
}

VisualServoController::~VisualServoController() {
    cleanup();
}

int VisualServoController::initialize() {
    std::cout << "Initializing Visual Servo Controller..." << std::endl;

    // 初始化电机控制
    if (init_motors() != 0) {
        std::cerr << "Failed to initialize motor control!" << std::endl;
        return -1;
    }

    // 设置PID参数
    set_pid_parameters(1.0f, 0.1f, 0.05f, 1.5f, 0.0f, 0.1f);

    // 设置死区
    set_dead_zone(50.0f, 50.0f);

    initialized = true;
    std::cout << "Visual Servo Controller initialized successfully!" << std::endl;
    return 0;
}

void VisualServoController::cleanup() {
    if (initialized) {
        std::cout << "Cleaning up Visual Servo Controller..." << std::endl;
        stop_motion();
        cleanup_motors();
        initialized = false;
    }
}

void VisualServoController::process_detection(const std::vector<TargetBox>& boxes) {
    if (!initialized) {
        std::cerr << "Visual Servo Controller not initialized!" << std::endl;
        return;
    }

    if (boxes.empty()) {
        // 没有检测到目标，停止运动
        stop_motion();
        return;
    }

    // 找到置信度最高的目标（通常是手部）
    const TargetBox* best_target = nullptr;
    float max_confidence = 0.0f;

    for (const auto& box : boxes) {
        if (box.score > max_confidence) {
            max_confidence = box.score;
            best_target = &box;
        }
    }

    if (best_target && max_confidence > 0.5f) { // 置信度阈值
        // 计算目标中心位置
        float center_x = (best_target->x1 + best_target->x2) / 2.0f;
        float center_y = (best_target->y1 + best_target->y2) / 2.0f;
        float target_size = std::max<float>(best_target->x2 - best_target->x1,
                                           best_target->y2 - best_target->y1);

        // 跟踪目标
        track_target(center_x, center_y, target_size);
    } else {
        // 置信度太低，停止运动
        stop_motion();
    }
}

void VisualServoController::set_pid_parameters(float kp_lin, float ki_lin, float kd_lin,
                                             float kp_ang, float ki_ang, float kd_ang) {
    kp_linear = kp_lin;
    ki_linear = ki_lin;
    kd_linear = kd_lin;
    kp_angular = kp_ang;
    ki_angular = ki_ang;
    kd_angular = kd_ang;

    std::cout << "PID parameters set:" << std::endl;
    std::cout << "  Linear:  Kp=" << kp_linear << ", Ki=" << ki_linear << ", Kd=" << kd_linear << std::endl;
    std::cout << "  Angular: Kp=" << kp_angular << ", Ki=" << ki_angular << ", Kd=" << kd_angular << std::endl;
}

void VisualServoController::set_dead_zone(float dead_x, float dead_y) {
    dead_zone_x = dead_x;
    dead_zone_y = dead_y;
    std::cout << "Dead zone set: X=" << dead_zone_x << ", Y=" << dead_zone_y << std::endl;
}

void VisualServoController::track_target(float target_center_x, float target_center_y, float target_size) {
    if (!initialized) return;

    // 计算误差（目标位置 - 当前目标位置）
    float error_x = target_center_x - target_x;
    float error_y = target_center_y - target_y;

    // 死区检查
    if (std::abs(error_x) < dead_zone_x && std::abs(error_y) < dead_zone_y) {
        stop_motion();
        return;
    }

    // 计算PID控制输出
    // X方向（左右运动）
    integral_x += error_x;
    float derivative_x = error_x - last_error_x;
    float control_x = kp_angular * error_x + ki_angular * integral_x + kd_angular * derivative_x;

    // Y方向（前后运动）和距离控制
    integral_y += error_y;
    float derivative_y = error_y - last_error_y;
    float control_y = kp_linear * error_y + ki_linear * integral_y + kd_linear * derivative_y;

    // 目标大小控制（距离远近）
    float size_error = 150.0f - target_size; // 期望目标大小为150像素
    float size_control = kp_linear * size_error * 0.5f; // 距离控制

    // 保存当前误差
    last_error_x = error_x;
    last_error_y = error_y;

    // 转换为电机速度指令
    float left_speed = 0.0f;
    float right_speed = 0.0f;

    // 基础前进/后退速度（基于目标大小和Y位置）
    float base_speed = std::max(0.0f, size_control);
    if (control_y < -10) {
        // 目标在上方，前进
        base_speed += std::abs(control_y) * 0.3f;
    } else if (control_y > 10) {
        // 目标在下方，后退（可选）
        base_speed = -std::abs(control_y) * 0.2f;
    }

    // 左右转向控制
    float turn_speed = control_x * 0.5f;

    if (turn_speed > 0) {
        // 右转
        left_speed = base_speed + turn_speed;
        right_speed = base_speed;
    } else {
        // 左转
        left_speed = base_speed;
        right_speed = base_speed - turn_speed;
    }

    // 限制速度范围
    left_speed = std::max(-60.0f, std::min(80.0f, left_speed));
    right_speed = std::max(-60.0f, std::min(80.0f, right_speed));

    // 执行电机控制
    if (std::abs(left_speed) > 1.0f || std::abs(right_speed) > 1.0f) {
        if (base_speed > 0) {
            // 前进转向
            move_forward(std::max(std::abs(left_speed), std::abs(right_speed)));
            if (turn_speed > 5) {
                turn_right(30.0f);
            } else if (turn_speed < -5) {
                turn_left(30.0f);
            }
        } else if (base_speed < 0) {
            // 后退
            move_backward(std::abs(base_speed));
        } else {
            // 原地转向
            if (turn_speed > 10) {
                rotate_right(25.0f);
            } else if (turn_speed < -10) {
                rotate_left(25.0f);
            }
        }

        std::cout << "Tracking: error=(" << error_x << "," << error_y
                  << "), size=" << target_size
                  << ", speeds=(" << left_speed << "," << right_speed << ")" << std::endl;
    } else {
        stop_motion();
    }
}

void VisualServoController::stop_motion() {
    if (initialized) {
        stop_all_motors();
        // 重置PID积分项
        integral_x = 0.0f;
        integral_y = 0.0f;
        last_error_x = 0.0f;
        last_error_y = 0.0f;
    }
}

void VisualServoController::get_status() const {
    if (!initialized) {
        std::cout << "Visual Servo Controller: Not initialized" << std::endl;
        return;
    }

    std::cout << "=== Visual Servo Controller Status ===" << std::endl;
    std::cout << "Frame size: " << frame_width << "x" << frame_height << std::endl;
    std::cout << "Target position: (" << target_x << ", " << target_y << ")" << std::endl;
    std::cout << "Dead zone: (" << dead_zone_x << ", " << dead_zone_y << ")" << std::endl;
    std::cout << "PID Linear: Kp=" << kp_linear << ", Ki=" << ki_linear << ", Kd=" << kd_linear << std::endl;
    std::cout << "PID Angular: Kp=" << kp_angular << ", Ki=" << ki_angular << ", Kd=" << kd_angular << std::endl;
    print_motor_status();
}