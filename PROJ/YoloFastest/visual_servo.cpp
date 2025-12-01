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
      kp_linear(1.0f), ki_linear(0.08f), kd_linear(0.12f),
      kp_angular(1.0f), ki_angular(0.0f), kd_angular(0.15f) {
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

    // 设置PID参数（优化前进响应）
    set_pid_parameters(1.0f, 0.08f, 0.12f, 1.0f, 0.0f, 0.15f);

    // 设置死区（增大死区以减少微小抖动）
    set_dead_zone(30.0f, 40.0f);

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
    // 限制积分饱和
    integral_x = std::max(-50.0f, std::min(50.0f, integral_x));
    float derivative_x = error_x - last_error_x;
    float control_x = kp_angular * error_x + ki_angular * integral_x + kd_angular * derivative_x;

    // Y方向（前后运动）和距离控制
    integral_y += error_y;
    // 限制积分饱和
    integral_y = std::max(-50.0f, std::min(50.0f, integral_y));
    float derivative_y = error_y - last_error_y;
    float control_y = kp_linear * error_y + ki_linear * integral_y + kd_linear * derivative_y;

    // 目标大小控制（距离远近）
    float size_error = 150.0f - target_size; // 期望目标大小为150像素
    float size_control = kp_linear * size_error * 0.8f; // 增加距离控制权重

    // 保存当前误差
    last_error_x = error_x;
    last_error_y = error_y;

    // 转换为电机速度指令
    float left_speed = 0.0f;
    float right_speed = 0.0f;

    // 重新设计速度计算逻辑
    float base_speed = 0.0f;

    // 基于Y位置的速度控制（增强响应）
    if (control_y < -5) {
        // 目标在上方，前进 - 提高响应性
        base_speed = std::abs(control_y) * 0.9f; // 大幅增加前进速度系数
    } else if (control_y > 8) {
        // 目标在下方，后退
        base_speed = -std::abs(control_y) * 0.7f; // 增加后退速度系数
    }

    // 结合目标大小控制 - 增强前进响应
    if (size_error > 15) { // 降低阈值，更积极前进
        base_speed += std::abs(size_control) * 1.2f; // 增加前进权重
    } else if (size_error < -25) { // 目标太大，需要后退远离
        base_speed -= std::abs(size_control) * 0.8f; // 减少后退权重
    } else {
        // 在合理距离范围内，使用size_control微调
        if (base_speed > 0) { // 如果已经在前进，增强前进
            base_speed += std::abs(size_control) * 0.7f;
        } else {
            base_speed += size_control * 0.3f; // 后退时减少影响
        }
    }

    // 确保最小移动速度（避免过慢）- 更积极的前进保证
    if (std::abs(base_speed) > 3) { // 降低触发阈值
        if (base_speed > 0 && base_speed < 30) { // 前进时最小速度更高
            base_speed = 30.0f;
        } else if (base_speed < 0 && std::abs(base_speed) < 25) { // 后退保持原逻辑
            base_speed = -25.0f;
        }
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

    // 限制速度范围（提高后退最大速度）
    left_speed = std::max(-50.0f, std::min(60.0f, left_speed));
    right_speed = std::max(-50.0f, std::min(60.0f, right_speed));

    // 执行电机控制 - 优化后的差速控制逻辑
    if (std::abs(left_speed) > 3.0f || std::abs(right_speed) > 3.0f) {
        if (base_speed > 5) {
            // 前进时使用差速转向，避免指令冲突
            float max_forward_speed = std::max(std::abs(left_speed), std::abs(right_speed));
            move_forward(max_forward_speed);

            // 如果需要转向，调整左右电机速度差而不是额外调用转向函数
            if (std::abs(turn_speed) > 3) {
                // 计算转向比例
                float turn_ratio = std::abs(turn_speed) / 100.0f; // 归一化转向强度
                turn_ratio = std::min(0.4f, turn_ratio); // 限制转向强度最大40%

                if (turn_speed > 0) {
                    // 右转：左电机保持速度，右电机减速
                    set_motor_speeds(max_forward_speed, max_forward_speed * (1.0f - turn_ratio));
                } else {
                    // 左转：右电机保持速度，左电机减速
                    set_motor_speeds(max_forward_speed * (1.0f - turn_ratio), max_forward_speed);
                }
            } else {
                // 直线前进
                set_motor_speeds(max_forward_speed, max_forward_speed);
            }
        } else if (base_speed < -5) {
            // 后退
            move_backward(std::abs(base_speed));
        } else {
            // 原地转向（降低转向速度）
            if (std::abs(turn_speed) > 8) {
                float rotate_speed = std::min(20.0f, std::abs(turn_speed) * 0.3f);
                if (turn_speed > 0) {
                    rotate_right(rotate_speed);
                } else {
                    rotate_left(rotate_speed);
                }
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