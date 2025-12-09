#ifndef VISUAL_SERVO_H_
#define VISUAL_SERVO_H_

#include <vector>
#include <opencv2/opencv.hpp>
#include "motor_control.h"
#include "yolo-fastestv2.h"

// 视觉伺服控制器类
class VisualServoController {
private:
    bool initialized;
    int frame_width;
    int frame_height;

    // 跟踪参数
    float target_x;          // 目标位置（画面中心）
    float target_y;
    float dead_zone_x;       // 死区范围
    float dead_zone_y;
    float last_error_x;      // 上一次误差
    float last_error_y;
    float integral_x;        // 积分项
    float integral_y;

    // PID控制参数
    float kp_linear;        // 线性控制比例系数
    float ki_linear;        // 线性控制积分系数
    float kd_linear;        // 线性控制微分系数
    float kp_angular;       // 角度控制比例系数
    float ki_angular;       // 角度控制积分系数
    float kd_angular;       // 角度控制微分系数

    // 跟踪历史
    std::vector<float> hand_positions_x;  // 手部位置历史
    std::vector<float> hand_positions_y;
    std::vector<float> hand_sizes;        // 手部大小历史
    const int MAX_HISTORY = 10;           // 最大历史记录数

    
    // 手势识别
    bool is_hand_open;        // 手是否张开
    bool is_hand_closed;      // 手是否握紧
    float last_hand_size;     // 上次手部大小
    float gesture_threshold;  // 手势识别阈值

public:
    VisualServoController();
    ~VisualServoController();

    // 初始化
    int initialize();

    // 清理资源
    void cleanup();

    // 处理检测结果并控制电机
    void process_detection(const std::vector<TargetBox>& boxes);

    // 设置控制参数
    void set_pid_parameters(float kp_lin, float ki_lin, float kd_lin,
                           float kp_ang, float ki_ang, float kd_ang);

    // 设置死区
    void set_dead_zone(float dead_x, float dead_y);

    // 跟踪单个目标
    void track_target(float target_x, float target_y, float target_size);

    // 高级跟踪功能
    void update_hand_history(float x, float y, float size);
    bool detect_gesture(float current_size);
    float predict_movement(float& predicted_x, float& predicted_y);
    void smooth_tracking(float& x, float& y, float alpha = 0.7f);

    // 停止所有运动
    void stop_motion();

    // 获取状态信息
    bool is_initialized() const { return initialized; }
    void get_status() const;
    bool get_gesture_status() const { return is_hand_open; }
};

#endif // VISUAL_SERVO_H_