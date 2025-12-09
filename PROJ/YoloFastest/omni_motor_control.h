#ifndef OMNI_MOTOR_CONTROL_H_
#define OMNI_MOTOR_CONTROL_H_

#include "motor_control.h"
#include "omni_kinematics.h"

// 三轮全向电机控制类
class OmniMotorController {
private:
    bool initialized;

    // 三个电机引脚配置
    MotorPins motor1_pins;    // 使用注释中的第一组: 17/6/26
    MotorPins motor2_pins;    // 使用注释中的第二组: 20/12/16
    MotorPins motor3_pins;    // 使用注释中的第三组: 22/27/23

    // 当前速度设置
    float current_speeds[3];  // [-100, 100] 范围的PWM占空比

    // 运动学控制器
    OmniKinematics kinematics;

public:
    OmniMotorController();
    ~OmniMotorController();

    // 初始化三轮电机控制
    int initialize();

    // 清理资源
    void cleanup();

    // 基本电机控制 (兼容原有接口)
    void set_motor_speeds(float m1_speed, float m2_speed, float m3_speed);
    void stop_all_motors();

    // 全向移动控制 (使用运动学解算)
    void move_forward(float speed);
    void move_backward(float speed);
    void strafe_left(float speed);
    void strafe_right(float speed);
    void rotate_left(float speed);
    void rotate_right(float speed);

    // 斜向移动
    void move_diagonal_fl(float speed);   // 左前
    void move_diagonal_fr(float speed);   // 右前
    void move_diagonal_bl(float speed);   // 左后
    void move_diagonal_br(float speed);   // 右后

    // 自定义方向移动 (角度为度数，0度=右方，90度=上方)
    void move_direction(float direction_deg, float speed);

    // 使用运动学向量的高级控制
    void move_vector(const OmniKinematics::VelocityVector& vel);

    // 速度设置
    void set_max_speeds(float max_linear, float max_angular);

    // 状态查询
    bool is_initialized() const { return initialized; }
    OmniKinematics::MoveMode get_current_mode() const;
    void get_motor_speeds(float& m1, float& m2, float& m3) const;

    // 调试和监控
    void print_status() const;
    void print_motor_status() const;

private:
    // 内部电机控制函数
    void set_single_motor(const MotorPins& motor, float speed);
    void apply_motor_speeds(const OmniKinematics::MotorSpeeds& speeds);

    // 速度转换 (-1到1) -> PWM占空比 (0到100)
    float speed_to_pwm(float normalized_speed);
};

// 全局三轮控制器实例 (用于向后兼容)
extern OmniMotorController omni_controller;

// 兼容性函数 (保持与原代码的接口一致)
void set_omni_motor_speeds(float m1_speed, float m2_speed, float m3_speed);
void stop_all_omni_motors();
void omni_move_forward(float speed);
void omni_move_backward(float speed);

#endif // OMNI_MOTOR_CONTROL_H_