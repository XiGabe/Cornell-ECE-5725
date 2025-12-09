#include "omni_kinematics.h"
#include <iostream>
#include <cmath>
#include <algorithm>

OmniKinematics::OmniKinematics()
    : wheel_radius(0.05f), robot_radius(0.15f), wheel_angle(M_PI/4), // 45度
      max_linear_speed(2.5f), max_angular_speed(M_PI), // 提高到2.5m/s
      current_mode(STOP), current_velocity(0, 0, 0),
      current_motor_speeds(0, 0, 0) {
}

void OmniKinematics::initialize(float wheel_r, float robot_r) {
    wheel_radius = wheel_r;
    robot_radius = robot_r;

    std::cout << "OmniKinematics initialized:" << std::endl;
    std::cout << "  Wheel radius: " << wheel_radius << "m" << std::endl;
    std::cout << "  Robot radius: " << robot_radius << "m" << std::endl;
    std::cout << "  Wheel angle: " << (wheel_angle * 180.0f / M_PI) << " degrees" << std::endl;
}

void OmniKinematics::set_speed_limits(float max_linear, float max_angular) {
    max_linear_speed = max_linear;
    max_angular_speed = max_angular;

    std::cout << "Speed limits set:" << std::endl;
    std::cout << "  Max linear: " << max_linear_speed << " m/s" << std::endl;
    std::cout << "  Max angular: " << max_angular_speed << " rad/s" << std::endl;
}

OmniKinematics::MotorSpeeds OmniKinematics::calculate_motor_speeds(MoveMode mode, float speed) {
    current_mode = mode;

    VelocityVector vel;

    switch (mode) {
        case FORWARD:
            vel = VelocityVector(0, speed, 0);
            break;
        case BACKWARD:
            vel = VelocityVector(0, -speed, 0);
            break;
        case STRAFE_LEFT:
            vel = VelocityVector(-speed, 0, 0);
            break;
        case STRAFE_RIGHT:
            vel = VelocityVector(speed, 0, 0);
            break;
        case ROTATE_LEFT:
            vel = VelocityVector(0, 0, speed);
            break;
        case ROTATE_RIGHT:
            vel = VelocityVector(0, 0, -speed);
            break;
        case DIAGONAL_FL:  // 左前斜向
            vel = VelocityVector(-speed * 0.707f, speed * 0.707f, 0);
            break;
        case DIAGONAL_FR:  // 右前斜向
            vel = VelocityVector(speed * 0.707f, speed * 0.707f, 0);
            break;
        case DIAGONAL_BL:  // 左后斜向
            vel = VelocityVector(-speed * 0.707f, -speed * 0.707f, 0);
            break;
        case DIAGONAL_BR:  // 右后斜向
            vel = VelocityVector(speed * 0.707f, -speed * 0.707f, 0);
            break;
        case STOP:
        default:
            vel = VelocityVector(0, 0, 0);
            break;
    }

    current_velocity = vel;
    return calculate_vector_speeds(vel);
}

OmniKinematics::MotorSpeeds OmniKinematics::calculate_vector_speeds(const VelocityVector& vel) {
    // 限制速度范围
    VelocityVector normalized_vel = normalize_velocity(vel);

    // 三轮麦克纳姆轮运动学解算
    // 假设轮子分布：轮子1在左侧，轮子2在右上方，轮子3在右下方
    // 轮子安装角度都是45度

    float vx = normalized_vel.vx;
    float vy = normalized_vel.vy;
    float omega = normalized_vel.omega;

    // 运动学矩阵计算
    // v1 = -sin(θ₁)*vx + cos(θ₁)*vy + R*ω
    // v2 = -sin(θ₂)*vx + cos(θ₂)*vy + R*ω
    // v3 = -sin(θ₃)*vx + cos(θ₃)*vy + R*ω

    // 根据实际照片修正轮子位置（从上往下俯视）：
    // Motor3: 正上方 = 0度
    // Motor1: 左下方 = 240度
    // Motor2: 右下方 = 120度

    float theta1 = 240.0f * M_PI / 180.0f;   // 轮子1: 240度（左下）
    float theta2 = 120.0f * M_PI / 180.0f;   // 轮子2: 120度（右下）
    float theta3 =   0.0f * M_PI / 180.0f;   // 轮子3: 0度（正上）

    // 麦克纳姆轮运动学公式（考虑45° rollers）
    float v1 = std::cos(theta1) * vx + std::sin(theta1) * vy + robot_radius * omega;
    float v2 = std::cos(theta2) * vx + std::sin(theta2) * vy + robot_radius * omega;
    float v3 = std::cos(theta3) * vx + std::sin(theta3) * vy + robot_radius * omega;

    // 转换为电机速度 (-1 到 1)
    MotorSpeeds speeds;
    // 根据实际观察修正方向：
    // Motor1: 逆时针转动符合预期，保持原方向
    // Motor2: 顺时针转动，需要反转
    // Motor3: 不动，需要检查并可能增加权重
    speeds.motor1 =  v1 / max_linear_speed;         // Motor1保持原方向
    speeds.motor2 = -v2 / max_linear_speed;        // Motor2反转
    speeds.motor3 = -v3 * 1.5f / max_linear_speed;  // Motor3反转并增加50%权重

    current_motor_speeds = normalize_motor_speeds(speeds);
    return current_motor_speeds;
}

OmniKinematics::MotorSpeeds OmniKinematics::calculate_direction_speeds(float direction_deg, float speed) {
    current_mode = CUSTOM_VECTOR;

    // 转换角度为弧度
    float direction_rad = direction_deg * M_PI / 180.0f;

    // 计算速度分量
    VelocityVector vel(
        speed * std::cos(direction_rad),
        speed * std::sin(direction_rad),
        0.0f
    );

    current_velocity = vel;
    return calculate_vector_speeds(vel);
}

OmniKinematics::VelocityVector OmniKinematics::calculate_robot_velocity(const MotorSpeeds& motor_speeds) {
    // 电机速度转换为轮子线速度
    float v1 = motor_speeds.motor1 * max_linear_speed;
    float v2 = motor_speeds.motor2 * max_linear_speed;
    float v3 = motor_speeds.motor3 * max_linear_speed;

    // 轮子角度（与正解算保持一致）：根据实际照片
    float theta1 = 240.0f * M_PI / 180.0f;  // 轮子1: 240度（左下）
    float theta2 = 120.0f * M_PI / 180.0f;  // 轮子2: 120度（右下）
    float theta3 =   0.0f * M_PI / 180.0f;  // 轮子3: 0度（正上）

    // 构建运动学矩阵的逆 (简化版本)
    // 这里使用数值解法，实际应用中可以使用精确的矩阵求逆
    float sin_sum = std::sin(theta1) + std::sin(theta2) + std::sin(theta3);
    float cos_sum = std::cos(theta1) + std::cos(theta2) + std::cos(theta3);

    VelocityVector vel;

    // 避免除零错误
    if (std::abs(sin_sum) > 0.001 && std::abs(cos_sum) > 0.001) {
        vel.vx = -(v1 * std::sin(theta1) + v2 * std::sin(theta2) + v3 * std::sin(theta3)) / sin_sum;
        vel.vy = (v1 * std::cos(theta1) + v2 * std::cos(theta2) + v3 * std::cos(theta3)) / cos_sum;
        vel.omega = (v1 + v2 + v3) / (3.0f * robot_radius);
    } else {
        vel = VelocityVector(0, 0, 0);
    }

    return vel;
}

OmniKinematics::MotorSpeeds OmniKinematics::normalize_motor_speeds(const MotorSpeeds& speeds) {
    MotorSpeeds normalized = speeds;

    // 限制每个电机速度到 [-1, 1] 范围
    normalized.motor1 = std::max(-1.0f, std::min(1.0f, speeds.motor1));
    normalized.motor2 = std::max(-1.0f, std::min(1.0f, speeds.motor2));
    normalized.motor3 = std::max(-1.0f, std::min(1.0f, speeds.motor3));

    return normalized;
}

OmniKinematics::VelocityVector OmniKinematics::normalize_velocity(const VelocityVector& vel) {
    VelocityVector normalized = vel;

    // 限制线速度
    float current_speed = std::sqrt(vel.vx * vel.vx + vel.vy * vel.vy);
    if (current_speed > max_linear_speed) {
        float scale = max_linear_speed / current_speed;
        normalized.vx *= scale;
        normalized.vy *= scale;
    }

    // 限制角速度
    normalized.omega = std::max(-max_angular_speed, std::min(max_angular_speed, vel.omega));

    return normalized;
}

void OmniKinematics::print_status() const {
    std::cout << "=== OmniKinematics Status ===" << std::endl;
    std::cout << "Mode: " << get_mode_name(current_mode) << std::endl;
    std::cout << "Velocity: vx=" << current_velocity.vx
              << ", vy=" << current_velocity.vy
              << ", omega=" << current_velocity.omega << std::endl;
    std::cout << "Motor speeds: M1=" << current_motor_speeds.motor1
              << ", M2=" << current_motor_speeds.motor2
              << ", M3=" << current_motor_speeds.motor3 << std::endl;
}

std::string OmniKinematics::get_mode_name(MoveMode mode) const {
    switch (mode) {
        case STOP: return "Stop";
        case FORWARD: return "Forward";
        case BACKWARD: return "Backward";
        case STRAFE_LEFT: return "Strafe Left";
        case STRAFE_RIGHT: return "Strafe Right";
        case ROTATE_LEFT: return "Rotate Left";
        case ROTATE_RIGHT: return "Rotate Right";
        case DIAGONAL_FL: return "Diagonal Front-Left";
        case DIAGONAL_FR: return "Diagonal Front-Right";
        case DIAGONAL_BL: return "Diagonal Back-Left";
        case DIAGONAL_BR: return "Diagonal Back-Right";
        case CUSTOM_VECTOR: return "Custom Vector";
        default: return "Unknown";
    }
}