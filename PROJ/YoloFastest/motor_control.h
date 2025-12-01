#ifndef MOTOR_CONTROL_H_
#define MOTOR_CONTROL_H_

// 与Python版本完全一致的引脚配置
struct MotorPins {
    int IN1;
    int IN2;
    int PWM;
    const char* name;
};

// 引脚配置 (直接使用BCM编号，与motor_test.py和test_motor_control_bcm一致)
extern MotorPins MOTOR_LEFT;   // {5, 6, 26, "Left"}   // BCM: 5, 6, 26
extern MotorPins MOTOR_RIGHT;  // {20, 12, 16, "Right"} // BCM: 20, 12, 16

// 控制参数
extern const int PWM_FREQUENCY_HZ;
extern const float MAX_SPEED_DC;

// 基础GPIO和PWM控制
int init_motors();
void cleanup_motors();

// 单个电机控制
void set_motor_direction(const MotorPins& motor, int direction);  // -1:CCW, 0:STOP, 1:CW
void set_motor_speed(const MotorPins& motor, float speed_dc);

// 双电机协调控制
void set_motor_speeds(float left_speed, float right_speed);
void stop_all_motors();

// 高级运动控制
void move_forward(float speed);
void move_backward(float speed);
void turn_left(float speed);
void turn_right(float speed);
void rotate_left(float speed);   // 原地左转
void rotate_right(float speed);  // 原地右转

// 调试信息
void print_motor_status();

#endif