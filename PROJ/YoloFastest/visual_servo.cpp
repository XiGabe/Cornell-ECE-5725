#include "visual_servo.h"
#include <iostream>
#include <algorithm>
#include <cmath>
#include "omni_motor_control.h"

VisualServoController::VisualServoController()
    : initialized(false), frame_width(640), frame_height(480),
      target_x(320.0f), target_y(240.0f),
      dead_zone_x(50.0f), dead_zone_y(50.0f),
      last_error_x(0.0f), last_error_y(0.0f),
      integral_x(0.0f), integral_y(0.0f),
      kp_linear(1.0f), ki_linear(0.08f), kd_linear(0.12f),
      kp_angular(1.0f), ki_angular(0.0f), kd_angular(0.15f),
      is_hand_open(true), is_hand_closed(false), last_hand_size(0.0f),
      gesture_threshold(0.3f) {
}

VisualServoController::~VisualServoController() {
    cleanup();
}

int VisualServoController::initialize() {
    std::cout << "Initializing Visual Servo Controller..." << std::endl;

    // 初始化三轮全向电机控制
    if (omni_controller.initialize() != 0) {
        std::cerr << "Failed to initialize omni motor control!" << std::endl;
        return -1;
    }

    // 设置PID参数（优化前进响应）
    set_pid_parameters(1.0f, 0.08f, 0.12f, 1.0f, 0.0f, 0.15f);

    // 设置死区（减小死区增加灵敏度）
    set_dead_zone(15.0f, 20.0f);

    initialized = true;
    std::cout << "Visual Servo Controller initialized successfully!" << std::endl;
    return 0;
}

void VisualServoController::cleanup() {
    if (initialized) {
        std::cout << "Cleaning up Visual Servo Controller..." << std::endl;
        stop_motion();
        omni_controller.cleanup();
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

    // 调试信息：显示手的位置
    std::cout << "Hand position: (" << target_center_x << ", " << target_center_y << ")" << std::endl;

    // 更新手部跟踪历史
    update_hand_history(target_center_x, target_center_y, target_size);

    // 检测手势
    detect_gesture(target_size);

    // 平滑跟踪
    float smooth_x = target_center_x;
    float smooth_y = target_center_y;
    smooth_tracking(smooth_x, smooth_y);

    // 预测运动
    float predicted_x, predicted_y;
    float prediction_confidence = predict_movement(predicted_x, predicted_y);

    // 使用平滑或预测位置
    if (prediction_confidence > 0.5f) {
        smooth_x = smooth_x * 0.7f + predicted_x * 0.3f;
        smooth_y = smooth_y * 0.7f + predicted_y * 0.3f;
    }

    // 计算误差（目标位置 - 当前目标位置）
    float error_x = target_x - smooth_x;  // 水平翻转：画面左=现实右，所以翻转X轴误差
    float error_y = smooth_y - target_y;  // 正值=手在下方

    // 调试信息：显示误差和方向（考虑水平翻转）
    std::cout << "Error: (" << error_x << ", " << error_y << ") - ";
    if (error_x > 50) std::cout << "现实:手在右侧(画面左) ";
    else if (error_x < -50) std::cout << "现实:手在左侧(画面右) ";
    else std::cout << "现实:手在中央X ";

    if (error_y > 50) std::cout << "现实:手在下方 ";
    else if (error_y < -50) std::cout << "现实:手在上方 ";
    else std::cout << "现实:手在中央Y ";
    std::cout << std::endl;

    // 握拳检测已禁用 - 只根据手位置控制运动
    // 不再检测握拳停止功能

    // 使用固定死区，不再依赖手势检测
    float adaptive_dead_zone_x = dead_zone_x;
    float adaptive_dead_zone_y = dead_zone_y;

    // 死区检查
    if (std::abs(error_x) < adaptive_dead_zone_x && std::abs(error_y) < adaptive_dead_zone_y) {
        stop_motion();
        return;
    }

    // 移除PID计算，直接使用误差控制
    // 不再需要control_x和control_y变量

    // 移除目标大小控制，只根据位置控制
    // float size_error = 150.0f - target_size; // 注释掉距离控制
    // float size_control = kp_linear * size_error * 0.6f;

    // 保存当前误差
    last_error_x = error_x;
    last_error_y = error_y;

    // 基于Motor3方向的全向移动控制
    float vx = 0.0f;  // 右方为正X
    float vy = 0.0f;  // 前方为正Y（Motor3方向）
    float omega = 0.0f;  // 角速度

    // 坐标系定义：
    // 画面上方 = Motor3方向（机器人前方）
    // 画面下方 = 后方
    // 画面左侧 = 左方
    // 画面右侧 = 右方

    // 手在画面上方 = 向Motor3方向前进
    // 手在画面下方 = 向Motor3反方向后退
    // 手在画面左侧 = 向左侧平移
    // 手在画面右侧 = 向右侧平移

    // 修正后的全向移动控制
    // 手在画面上方 = 前进（正vy），手在画面下方 = 后退（负vy）
    // 手在画面右侧 = 右移（正vx），手在画面左侧 = 左移（负vx）

    if (std::abs(error_x) > 25 || std::abs(error_y) > 25) {  // 增大死区减少干扰
        // 反转vy方向：上方误差负数 = 后退负值（因为当前方向反了）
        vx = error_x * 0.025f;    // 右方误差正 = 正vx
        vy = error_y * 0.025f;    // 上方误差负 = 负vy，对应后退，但实际会前进

        // 微小偏移过滤：当手在中央X区域时，强制vx=0
        if (std::abs(error_x) < 30) {
            vx = 0;
            std::cout << "过滤微小X偏移，强制vx=0" << std::endl;
        }

        std::cout << "修正移动: vx=" << vx << "(右正), vy=" << vy << "(前正) - ";
        if (vy > 0.5) std::cout << "前进 ";
        else if (vy < -0.5) std::cout << "后退 ";
        if (vx > 0.5) std::cout << "右移 ";
        else if (vx < -0.5) std::cout << "左移 ";
        std::cout << "[修正坐标系]" << std::endl;
    } else {
        // 在死区内，确保完全停止
        vx = 0;
        vy = 0;
        std::cout << "在死区内，停止移动" << std::endl;
    }

    // 使用更激进的速度倍数，实现rush效果
    float speed_multiplier = 2.0f;  // 进一步增加速度
    vx *= speed_multiplier;
    vy *= speed_multiplier;

    // 确保最小移动速度 - 提高最小速度
    float total_speed = std::sqrt(vx * vx + vy * vy);
    if (total_speed > 1 && total_speed < 20) {  // 降低触发阈值，提高最大速度
        float scale = 20.0f / total_speed;  // 提高最小速度
        vx *= scale;
        vy *= scale;
    }

    // 移除所有旋转辅助，使用纯平移
    // 现在只使用前后左右的平移，不再额外添加旋转
    // omega保持为0，只使用vx, vy进行全向移动

    // 创建速度向量并限制范围
    OmniKinematics::VelocityVector vel(vx, vy, omega);

    // 简化的执行逻辑
    if (std::abs(vx) > 0.1 || std::abs(vy) > 0.1 || std::abs(omega) > 0.05) {
        omni_controller.move_vector(vel);
        std::cout << "执行移动: vx=" << vx << ", vy=" << vy << ", omega=" << omega << std::endl;
    } else {
        stop_motion();
        std::cout << "速度过小，停止移动" << std::endl;
    }
}

void VisualServoController::stop_motion() {
    if (initialized) {
        omni_controller.stop_all_motors();
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
    std::cout << "Hand Status: " << (is_hand_open ? "Open" : "Closed") << std::endl;
    std::cout << "History Size: " << hand_positions_x.size() << " frames" << std::endl;
    omni_controller.print_status();
}

void VisualServoController::update_hand_history(float x, float y, float size) {
    // 添加新数据到历史记录
    hand_positions_x.push_back(x);
    hand_positions_y.push_back(y);
    hand_sizes.push_back(size);

    // 限制历史记录长度
    if (hand_positions_x.size() > static_cast<size_t>(MAX_HISTORY)) {
        hand_positions_x.erase(hand_positions_x.begin());
        hand_positions_y.erase(hand_positions_y.begin());
        hand_sizes.erase(hand_sizes.begin());
    }
}

bool VisualServoController::detect_gesture(float current_size) {
    if (last_hand_size == 0.0f) {
        last_hand_size = current_size;
        return false;
    }

    float size_change = (current_size - last_hand_size) / last_hand_size;
    last_hand_size = current_size;

    // 检测快速大小变化为手势
    if (size_change > gesture_threshold) {
        // 手变大 = 张开
        is_hand_open = true;
        is_hand_closed = false;
        std::cout << "Gesture detected: Hand OPEN" << std::endl;
        return true;
    } else if (size_change < -gesture_threshold) {
        // 手变小 = 握拳
        is_hand_open = false;
        is_hand_closed = true;
        std::cout << "Gesture detected: Hand CLOSED" << std::endl;
        return true;
    }

    return false;
}

float VisualServoController::predict_movement(float& predicted_x, float& predicted_y) {
    if (hand_positions_x.size() < 3) {
        predicted_x = hand_positions_x.empty() ? 0 : hand_positions_x.back();
        predicted_y = hand_positions_y.empty() ? 0 : hand_positions_y.back();
        return 0.0f;
    }

    // 使用简单的线性预测
    int n = hand_positions_x.size();

    // 计算最近几帧的平均速度
    float vx = (hand_positions_x[n-1] - hand_positions_x[n-3]) / 2.0f;
    float vy = (hand_positions_y[n-1] - hand_positions_y[n-3]) / 2.0f;

    // 预测下一帧位置
    predicted_x = hand_positions_x[n-1] + vx;
    predicted_y = hand_positions_y[n-1] + vy;

    // 计算预测置信度（基于速度稳定性）
    float speed = std::sqrt(vx*vx + vy*vy);
    float confidence = std::min(1.0f, speed / 20.0f); // 速度越快，置信度越高

    return confidence;
}

void VisualServoController::smooth_tracking(float& x, float& y, float alpha) {
    if (hand_positions_x.size() < 2) {
        return; // 没有历史数据，不平滑
    }

    // 使用指数移动平均进行平滑
    float last_x = hand_positions_x[hand_positions_x.size() - 1];
    float last_y = hand_positions_y[hand_positions_y.size() - 1];

    x = alpha * x + (1.0f - alpha) * last_x;
    y = alpha * y + (1.0f - alpha) * last_y;
}