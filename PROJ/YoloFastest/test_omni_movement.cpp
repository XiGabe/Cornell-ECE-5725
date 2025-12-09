#include "omni_motor_control.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <signal.h>
#include <sstream>
#include <string>

// 全局标志用于优雅退出
static bool keep_running = true;

// 信号处理函数
void signal_handler(int signum) {
    std::cout << "\nReceived signal " << signum << std::endl;
    keep_running = false;
}

// 测试基本移动模式
void test_basic_movements() {
    std::cout << "\n=== Testing Basic Movements ===" << std::endl;

    float test_speed = 85.0f; // 85% 速度 (提高速度)
    int move_duration = 3000; // 3秒 (延长测试时间)
    int stop_duration = 1000; // 1秒

    // 前进
    std::cout << "\n1. Moving forward..." << std::endl;
    omni_controller.move_forward(test_speed);
    std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
    omni_controller.stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));

    // 后退
    std::cout << "\n2. Moving backward..." << std::endl;
    omni_controller.move_backward(test_speed);
    std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
    omni_controller.stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));

    // 左平移
    std::cout << "\n3. Strafing left..." << std::endl;
    omni_controller.strafe_left(test_speed);
    std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
    omni_controller.stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));

    // 右平移
    std::cout << "\n4. Strafing right..." << std::endl;
    omni_controller.strafe_right(test_speed);
    std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
    omni_controller.stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));

    // 左转
    std::cout << "\n5. Rotating left..." << std::endl;
    omni_controller.rotate_left(test_speed * 0.7f);
    std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
    omni_controller.stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));

    // 右转
    std::cout << "\n6. Rotating right..." << std::endl;
    omni_controller.rotate_right(test_speed * 0.7f);
    std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
    omni_controller.stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));
}

// 测试斜向移动
void test_diagonal_movements() {
    std::cout << "\n=== Testing Diagonal Movements ===" << std::endl;

    float test_speed = 75.0f; // 提高到75%
    int move_duration = 2500;  // 延长到2.5秒
    int stop_duration = 1000;

    // 左前斜向
    std::cout << "\n1. Moving diagonal front-left..." << std::endl;
    omni_controller.move_diagonal_fl(test_speed);
    std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
    omni_controller.stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));

    // 右前斜向
    std::cout << "\n2. Moving diagonal front-right..." << std::endl;
    omni_controller.move_diagonal_fr(test_speed);
    std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
    omni_controller.stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));

    // 左后斜向
    std::cout << "\n3. Moving diagonal back-left..." << std::endl;
    omni_controller.move_diagonal_bl(test_speed);
    std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
    omni_controller.stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));

    // 右后斜向
    std::cout << "\n4. Moving diagonal back-right..." << std::endl;
    omni_controller.move_diagonal_br(test_speed);
    std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
    omni_controller.stop_all_motors();
    std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));
}

// 测试自定义方向移动
void test_direction_movements() {
    std::cout << "\n=== Testing Direction Movements ===" << std::endl;

    float test_speed = 70.0f; // 提高到70%
    int move_duration = 2000;  // 延长到2秒
    int stop_duration = 500;

    // 测试8个主要方向
    float directions[] = {0, 45, 90, 135, 180, 225, 270, 315}; // 度数
    std::string direction_names[] = {"East", "Northeast", "North", "Northwest",
                                   "West", "Southwest", "South", "Southeast"};

    for (int i = 0; i < 8 && keep_running; i++) {
        std::cout << "\n" << (i+1) << ". Moving " << direction_names[i]
                  << " (" << directions[i] << "°)..." << std::endl;

        omni_controller.move_direction(directions[i], test_speed);
        std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
        omni_controller.stop_all_motors();
        std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));
    }
}

// 测试运动学向量控制
void test_vector_control() {
    std::cout << "\n=== Testing Vector Control ===" << std::endl;

    int move_duration = 2500;  // 延长到2.5秒
    int stop_duration = 1000;

    // 测试不同的速度向量
    OmniKinematics::VelocityVector vectors[] = {
        {0.3f, 0.0f, 0.0f},        // 向右
        {-0.3f, 0.0f, 0.0f},       // 向左
        {0.0f, 0.3f, 0.0f},        // 向前
        {0.0f, -0.3f, 0.0f},       // 向后
        {0.2f, 0.2f, 0.0f},        // 右前
        {-0.2f, 0.2f, 0.0f},       // 左前
        {0.0f, 0.0f, 0.5f},        // 原地旋转
    };

    std::string vector_names[] = {
        "Right (vx=0.3)", "Left (vx=-0.3)", "Forward (vy=0.3)", "Backward (vy=-0.3)",
        "Front-Right (vx=0.2, vy=0.2)", "Front-Left (vx=-0.2, vy=0.2)",
        "Rotate (omega=0.5)"
    };

    for (int i = 0; i < 7 && keep_running; i++) {
        std::cout << "\n" << (i+1) << ". Moving with vector: " << vector_names[i] << std::endl;

        omni_controller.move_vector(vectors[i]);
        std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
        omni_controller.stop_all_motors();
        std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));
    }
}

// 测试单个电机
void test_individual_motors() {
    std::cout << "\n=== Testing Individual Motors ===" << std::endl;

    float test_speed = 40.0f;
    int move_duration = 1000;
    int stop_duration = 500;

    // 测试每个电机独立运行
    for (int motor = 1; motor <= 3; motor++) {
        std::cout << "\n" << motor << ". Testing Motor " << motor << " forward..." << std::endl;

        switch (motor) {
            case 1:
                omni_controller.set_motor_speeds(test_speed, 0, 0);
                break;
            case 2:
                omni_controller.set_motor_speeds(0, test_speed, 0);
                break;
            case 3:
                omni_controller.set_motor_speeds(0, 0, test_speed);
                break;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
        omni_controller.stop_all_motors();
        std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));

        // 测试反向
        std::cout << "Testing Motor " << motor << " backward..." << std::endl;

        switch (motor) {
            case 1:
                omni_controller.set_motor_speeds(-test_speed, 0, 0);
                break;
            case 2:
                omni_controller.set_motor_speeds(0, -test_speed, 0);
                break;
            case 3:
                omni_controller.set_motor_speeds(0, 0, -test_speed);
                break;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(move_duration));
        omni_controller.stop_all_motors();
        std::this_thread::sleep_for(std::chrono::milliseconds(stop_duration));
    }
}

// 交互式测试模式
void interactive_test() {
    std::cout << "\n=== Interactive Test Mode ===" << std::endl;
    std::cout << "Commands:" << std::endl;
    std::cout << "  f [speed]  - Move forward (default: 50%)" << std::endl;
    std::cout << "  b [speed]  - Move backward" << std::endl;
    std::cout << "  l [speed]  - Strafe left" << std::endl;
    std::cout << "  r [speed]  - Strafe right" << std::endl;
    std::cout << "  rl [speed] - Rotate left" << std::endl;
    std::cout << "  rr [speed] - Rotate right" << std::endl;
    std::cout << "  d [angle] [speed] - Move in direction" << std::endl;
    std::cout << "  s          - Stop all motors" << std::endl;
    std::cout << "  status     - Show status" << std::endl;
    std::cout << "  q          - Quit" << std::endl;

    std::string command;
    while (keep_running) {
        std::cout << "\n> ";
        std::getline(std::cin, command);

        if (command == "q" || command == "quit") {
            break;
        } else if (command == "s" || command == "stop") {
            omni_controller.stop_all_motors();
        } else if (command == "status") {
            omni_controller.print_status();
        } else if (command.substr(0, 1) == "f") {
            float speed = (command.length() > 2) ? std::stof(command.substr(2)) : 50.0f;
            omni_controller.move_forward(speed);
        } else if (command.substr(0, 1) == "b") {
            float speed = (command.length() > 2) ? std::stof(command.substr(2)) : 50.0f;
            omni_controller.move_backward(speed);
        } else if (command.substr(0, 1) == "l") {
            float speed = (command.length() > 2) ? std::stof(command.substr(2)) : 50.0f;
            omni_controller.strafe_left(speed);
        } else if (command.substr(0, 1) == "r") {
            if (command.substr(0, 2) == "rl") {
                float speed = (command.length() > 3) ? std::stof(command.substr(3)) : 50.0f;
                omni_controller.rotate_left(speed);
            } else if (command.substr(0, 2) == "rr") {
                float speed = (command.length() > 3) ? std::stof(command.substr(3)) : 50.0f;
                omni_controller.rotate_right(speed);
            } else {
                float speed = (command.length() > 2) ? std::stof(command.substr(2)) : 50.0f;
                omni_controller.strafe_right(speed);
            }
        } else if (command.substr(0, 1) == "d") {
            std::istringstream iss(command);
            std::string dir_cmd, angle_str, speed_str;
            iss >> dir_cmd >> angle_str >> speed_str;
            float angle = std::stof(angle_str);
            float speed = speed_str.empty() ? 50.0f : std::stof(speed_str);
            omni_controller.move_direction(angle, speed);
        } else if (command.empty()) {
            // 忽略空输入
            continue;
        } else {
            std::cout << "Unknown command: " << command << std::endl;
        }
    }
}

int main(int argc, char** argv) {
    // 注册信号处理函数
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    std::cout << "=== OmniWheel Movement Test Program ===" << std::endl;

    // 初始化全向电机控制器
    if (omni_controller.initialize() != 0) {
        std::cerr << "Failed to initialize omni motor controller!" << std::endl;
        return -1;
    }

    std::cout << "\nInitialization complete! Starting tests..." << std::endl;

    try {
        if (argc > 1 && std::string(argv[1]) == "interactive") {
            // 交互式测试模式
            interactive_test();
        } else {
            // 自动测试模式

            // 1. 测试单个电机
            test_individual_motors();
            if (!keep_running) return 0;

            // 2. 测试基本移动
            test_basic_movements();
            if (!keep_running) return 0;

            // 3. 测试斜向移动
            test_diagonal_movements();
            if (!keep_running) return 0;

            // 4. 测试方向移动
            test_direction_movements();
            if (!keep_running) return 0;

            // 5. 测试向量控制
            test_vector_control();

            std::cout << "\n=== All tests completed successfully! ===" << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "Test failed with exception: " << e.what() << std::endl;
    }

    // 停止所有电机
    omni_controller.stop_all_motors();
    omni_controller.cleanup();

    std::cout << "Test program ended gracefully." << std::endl;
    return 0;
}