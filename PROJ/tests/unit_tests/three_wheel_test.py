import RPi.GPIO as GPIO
import time
import signal
import sys

# --- 配置部分 ---
PWM_FREQUENCY_HZ = 100
TEST_SPEED_DC = 80.0  # 测试速度 80%
STOP_SPEED_DC = 0.0

# 三个电机引脚配置 (基于你的注释)
MOTOR_1_PINS = {'IN1': 17, 'IN2': 6, 'PWM': 26, 'name': 'Motor1'}   # 轮子1
MOTOR_2_PINS = {'IN1': 20, 'IN2': 12, 'PWM': 16, 'name': 'Motor2'}  # 轮子2
MOTOR_3_PINS = {'IN1': 22, 'IN2': 27, 'PWM': 23, 'name': 'Motor3'}  # 轮子3

# 全局 PWM 对象
pwm_1 = None
pwm_2 = None
pwm_3 = None

def cleanup_and_exit(signum=None, frame=None):
    """清理 GPIO 并安全退出"""
    print("\n停止所有电机并清理 GPIO...")
    if pwm_1: pwm_1.stop()
    if pwm_2: pwm_2.stop()
    if pwm_3: pwm_3.stop()
    GPIO.cleanup()
    print("测试结束。")
    sys.exit(0)

def setup_gpio():
    """初始化 GPIO 和 PWM"""
    global pwm_1, pwm_2, pwm_3
    GPIO.setmode(GPIO.BCM)

    # 设置三个电机
    motors = [MOTOR_1_PINS, MOTOR_2_PINS, MOTOR_3_PINS]
    pwms = [pwm_1, pwm_2, pwm_3]

    for i, motor in enumerate(motors):
        GPIO.setup([motor['IN1'], motor['IN2'], motor['PWM']], GPIO.OUT)
        GPIO.output([motor['IN1'], motor['IN2']], GPIO.LOW)

        pwm_instance = GPIO.PWM(motor['PWM'], PWM_FREQUENCY_HZ)
        pwm_instance.start(STOP_SPEED_DC)

        if i == 0:
            pwm_1 = pwm_instance
        elif i == 1:
            pwm_2 = pwm_instance
        else:
            pwm_3 = pwm_instance

    print("三轮 GPIO 初始化完成。准备开始电机测试...")

def set_motor(motor_pins, direction, speed_dc):
    """
    控制单个电机的基础函数
    direction: 'CW' (正转), 'CCW' (反转), 'STOP' (停止)
    """
    if motor_pins['name'] == 'Motor1':
        pwm_obj = pwm_1
    elif motor_pins['name'] == 'Motor2':
        pwm_obj = pwm_2
    else:
        pwm_obj = pwm_3

    if direction == 'CW':
        GPIO.output(motor_pins['IN1'], GPIO.HIGH)
        GPIO.output(motor_pins['IN2'], GPIO.LOW)
        print(f"-> {motor_pins['name']}: 正转 (CW) 速度:{speed_dc}%")
    elif direction == 'CCW':
        GPIO.output(motor_pins['IN1'], GPIO.LOW)
        GPIO.output(motor_pins['IN2'], GPIO.HIGH)
        print(f"-> {motor_pins['name']}: 反转 (CCW) 速度:{speed_dc}%")
    else: # STOP
        GPIO.output(motor_pins['IN1'], GPIO.LOW)
        GPIO.output(motor_pins['IN2'], GPIO.LOW)
        print(f"-> {motor_pins['name']}: 停止")

    pwm_obj.ChangeDutyCycle(speed_dc)

def move_forward(speed_dc):
    """
    麦克纳姆轮前进 - 三个轮子都需要以正确的方向旋转
    根据轮子的45度安装角度，需要调整每个电机的方向
    """
    print(f"-> 三轮直线前进，速度: {speed_dc}%")

    # 注意：这里的方向需要根据你的实际轮子安装方向调整
    # 假设轮子安装方向使得以下配置实现前进
    set_motor(MOTOR_1_PINS, 'CW', speed_dc)     # 轮子1 正转
    set_motor(MOTOR_2_PINS, 'CW', speed_dc)     # 轮子2 正转
    set_motor(MOTOR_3_PINS, 'CW', speed_dc)     # 轮子3 正转

def move_backward(speed_dc):
    """麦克纳姆轮后退"""
    print(f"-> 三轮直线后退，速度: {speed_dc}%")

    set_motor(MOTOR_1_PINS, 'CCW', speed_dc)    # 轮子1 反转
    set_motor(MOTOR_2_PINS, 'CCW', speed_dc)    # 轮子2 反转
    set_motor(MOTOR_3_PINS, 'CCW', speed_dc)    # 轮子3 反转

def stop_all():
    """停止所有电机"""
    print("-> 停止所有电机")
    set_motor(MOTOR_1_PINS, 'STOP', 0)
    set_motor(MOTOR_2_PINS, 'STOP', 0)
    set_motor(MOTOR_3_PINS, 'STOP', 0)

# --- 主程序 ---
if __name__ == '__main__':
    signal.signal(signal.SIGINT, cleanup_and_exit)

    try:
        setup_gpio()
        time.sleep(1)

        print("\n=== 三轮麦克纳姆轮直线行走测试 ===")

        # 1. 单独测试每个电机
        print("\n--- 单独测试每个电机 ---")
        motors = [MOTOR_1_PINS, MOTOR_2_PINS, MOTOR_3_PINS]

        for motor in motors:
            print(f"\n测试 {motor['name']}:")
            set_motor(motor, 'CW', TEST_SPEED_DC)
            time.sleep(2)
            set_motor(motor, 'STOP', 0)
            time.sleep(1)
            set_motor(motor, 'CCW', TEST_SPEED_DC)
            time.sleep(2)
            set_motor(motor, 'STOP', 0)
            time.sleep(1)

        # 2. 测试直线前进
        print("\n--- 测试直线前进 ---")
        move_forward(TEST_SPEED_DC)
        time.sleep(3)
        stop_all()
        time.sleep(2)

        # 3. 测试直线后退
        print("\n--- 测试直线后退 ---")
        move_backward(TEST_SPEED_DC)
        time.sleep(3)
        stop_all()
        time.sleep(2)

        # 4. 循环测试
        print("\n--- 循环测试 (5秒前进，2秒停止) ---")
        for i in range(3):
            print(f"\n第 {i+1} 次循环:")
            move_forward(TEST_SPEED_DC)
            time.sleep(5)
            stop_all()
            time.sleep(2)

        print("\n=== 测试完成 ===")

    except Exception as e:
        print(f"\n发生错误: {e}")
    finally:
        cleanup_and_exit()