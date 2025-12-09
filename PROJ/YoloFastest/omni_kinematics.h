#ifndef OMNI_KINEMATICS_H_
#define OMNI_KINEMATICS_H_

#include <vector>
#include <string>

// 三轮麦克纳姆轮运动学解算库
class OmniKinematics {
public:
    // 运动向量结构
    struct VelocityVector {
        float vx;           // X方向速度 (m/s)
        float vy;           // Y方向速度 (m/s)
        float omega;        // 角速度 (rad/s)

        VelocityVector(float vx_ = 0, float vy_ = 0, float omega_ = 0)
            : vx(vx_), vy(vy_), omega(omega_) {}
    };

    // 电机速度结构
    struct MotorSpeeds {
        float motor1;       // 轮子1速度 (-1.0 到 1.0)
        float motor2;       // 轮子2速度
        float motor3;       // 轮子3速度

        MotorSpeeds(float m1 = 0, float m2 = 0, float m3 = 0)
            : motor1(m1), motor2(m2), motor3(m3) {}
    };

    // 移动模式枚举
    enum MoveMode {
        STOP,               // 停止
        FORWARD,            // 前进
        BACKWARD,           // 后退
        STRAFE_LEFT,        // 左平移
        STRAFE_RIGHT,       // 右平移
        ROTATE_LEFT,        // 左转
        ROTATE_RIGHT,       // 右转
        DIAGONAL_FL,        // 左前斜向
        DIAGONAL_FR,        // 右前斜向
        DIAGONAL_BL,        // 左后斜向
        DIAGONAL_BR,        // 右后斜向
        CUSTOM_VECTOR       // 自定义向量
    };

private:
    // 机器人参数
    float wheel_radius;     // 轮子半径 (m)
    float robot_radius;     // 机器人中心到轮子距离 (m)
    float wheel_angle;      // 轮子安装角度 (弧度，45度 = π/4)

    // 速度限制
    float max_linear_speed; // 最大线速度 (m/s)
    float max_angular_speed;// 最大角速度 (rad/s)

    // 当前运动状态
    MoveMode current_mode;
    VelocityVector current_velocity;
    MotorSpeeds current_motor_speeds;

public:
    OmniKinematics();
    ~OmniKinematics() = default;

    // 初始化运动学参数
    void initialize(float wheel_r = 0.05f, float robot_r = 0.15f);

    // 设置速度限制
    void set_speed_limits(float max_linear, float max_angular);

    // 基本移动模式
    MotorSpeeds calculate_motor_speeds(MoveMode mode, float speed = 1.0f);

    // 自定义向量移动
    MotorSpeeds calculate_vector_speeds(const VelocityVector& vel);

    // 从方向和速度计算 (角度为度数)
    MotorSpeeds calculate_direction_speeds(float direction_deg, float speed);

    // 运动学正解算 (从电机速度计算机器人速度)
    VelocityVector calculate_robot_velocity(const MotorSpeeds& motor_speeds);

    // 获取当前状态
    MoveMode get_current_mode() const { return current_mode; }
    VelocityVector get_current_velocity() const { return current_velocity; }
    MotorSpeeds get_current_motor_speeds() const { return current_motor_speeds; }

    // 状态管理
    void stop() { current_mode = STOP; current_velocity = VelocityVector(); }
    bool is_stopped() const { return current_mode == STOP; }

    // 调试信息
    void print_status() const;
    std::string get_mode_name(MoveMode mode) const;

    // 速度限制和归一化
    MotorSpeeds normalize_motor_speeds(const MotorSpeeds& speeds);
    VelocityVector normalize_velocity(const VelocityVector& vel);
};

#endif // OMNI_KINEMATICS_H_