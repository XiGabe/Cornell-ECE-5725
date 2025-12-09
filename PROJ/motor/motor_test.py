import RPi.GPIO as GPIO
import time
import signal
import sys

# --- 配置部分 (保持与原代码一致的引脚) ---
PWM_FREQUENCY_HZ = 100
TEST_SPEED_DC = 95.0  # 测试速度设为 80%，防止太快
STOP_SPEED_DC = 0.0

# 左电机引脚
MOTOR_L_PINS = {'IN1': 17, 'IN2': 6, 'PWM': 26, 'name': 'Left'}
# 右电机引脚
MOTOR_R_PINS = {'IN1': 22, 'IN2': 27, 'PWM': 23, 'name': 'Right'}
#17 6 26
#20 12 16
#22 27 23
# 全局 PWM 对象
pwm_L = None
pwm_R = None

def cleanup_and_exit(signum=None, frame=None):
    """清理 GPIO 并安全退出"""
    print("\n停止电机并清理 GPIO...")
    if pwm_L: pwm_L.stop()
    if pwm_R: pwm_R.stop()
    GPIO.cleanup()
    print("测试结束。")
    sys.exit(0)

def setup_gpio():
    """初始化 GPIO 和 PWM"""
    global pwm_L, pwm_R
    GPIO.setmode(GPIO.BCM)
    
    # 设置左右电机
    for motor in [MOTOR_L_PINS, MOTOR_R_PINS]:
        GPIO.setup([motor['IN1'], motor['IN2'], motor['PWM']], GPIO.OUT)
        GPIO.output([motor['IN1'], motor['IN2']], GPIO.LOW) # 初始状态 IN1=0, IN2=0
        
        pwm_instance = GPIO.PWM(motor['PWM'], PWM_FREQUENCY_HZ)
        pwm_instance.start(STOP_SPEED_DC)
        
        if motor['name'] == 'Left':
            pwm_L = pwm_instance
        else:
            pwm_R = pwm_instance
            
    print("GPIO 初始化完成。准备开始电机测试...")

def set_motor(motor_pins, direction, speed_dc):
    """
    控制单个电机的基础函数
    direction: 'CW' (正转), 'CCW' (反转), 'STOP' (停止)
    """
    pwm_obj = pwm_L if motor_pins['name'] == 'Left' else pwm_R
    
    if direction == 'CW':
        GPIO.output(motor_pins['IN1'], GPIO.HIGH)
        GPIO.output(motor_pins['IN2'], GPIO.LOW)
        print(f"-> {motor_pins['name']} Motor: 正转 (CW)")
    elif direction == 'CCW':
        GPIO.output(motor_pins['IN1'], GPIO.LOW)
        GPIO.output(motor_pins['IN2'], GPIO.HIGH)
        print(f"-> {motor_pins['name']} Motor: 反转 (CCW)")
    else: # STOP
        GPIO.output(motor_pins['IN1'], GPIO.LOW)
        GPIO.output(motor_pins['IN2'], GPIO.LOW)
        print(f"-> {motor_pins['name']} Motor: 停止")
        
    pwm_obj.ChangeDutyCycle(speed_dc)

# --- 主程序 ---
if __name__ == '__main__':
    # 捕获 Ctrl+C 信号以便安全退出
    signal.signal(signal.SIGINT, cleanup_and_exit)
    
    try:
        setup_gpio()
        time.sleep(1)

        while True:
            print("\n--- 开始新一轮测试循环 ---")
            
            # 1. 测试左电机
            set_motor(MOTOR_L_PINS, 'CW', TEST_SPEED_DC)
            time.sleep(1)
            set_motor(MOTOR_L_PINS, 'STOP', 0)
            time.sleep(1)
            set_motor(MOTOR_L_PINS, 'CCW', TEST_SPEED_DC)
            time.sleep(1)
            set_motor(MOTOR_L_PINS, 'STOP', 0)
            time.sleep(1)

            # 2. 测试右电机
            set_motor(MOTOR_R_PINS, 'CW', TEST_SPEED_DC)
            time.sleep(1)
            set_motor(MOTOR_R_PINS, 'STOP', 0)
            time.sleep(1)
            set_motor(MOTOR_R_PINS, 'CCW', TEST_SPEED_DC)
            time.sleep(1)
            set_motor(MOTOR_R_PINS, 'STOP', 0)
            time.sleep(1)

            # 3. 双电机同时测试
            print("-> 双电机全速前进")
            set_motor(MOTOR_L_PINS, 'CW', TEST_SPEED_DC)
            set_motor(MOTOR_R_PINS, 'CW', TEST_SPEED_DC)
            time.sleep(2)
            
            print("-> 全部停止")
            set_motor(MOTOR_L_PINS, 'STOP', 0)
            set_motor(MOTOR_R_PINS, 'STOP', 0)
            time.sleep(2)

    except Exception as e:
        print(f"\n发生错误: {e}")
    finally:
        cleanup_and_exit()