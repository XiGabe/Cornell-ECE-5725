# 逐帧追捕，动态拦截：智能垃圾桶项目蓝图

## 1. 项目愿景：重新定义"扔垃圾"的最后一步

在日常生活中，"扔垃圾"这个动作的终点，是我们的手和垃圾桶之间的一段抛物线。我们都曾有过投掷失败、纸团落在桶外的经历。受到网络上创意视频的启发，我们不禁思考：为什么垃圾桶必须是一个被动的接收者？

### 核心目标
创造一个"主动式"的智能垃圾桶。它不再是静止等待的容器，而是一个基于实时AI视觉和高速运动控制的移动机器人。它的核心使命只有一个：在你将垃圾扔出的瞬间，实时预判并高速移动到落点，主动"接住"垃圾。

### 项目范围界定
为确保项目可行性，我们进行了严格的范围界定：
- **100%专注于**：实现"垃圾追踪与拦截"这一核心功能
- **计算核心**：树莓派（超频）作为计算平台
- **视觉系统**：高速摄像头
- **AI算法**：YoloFastestV2-ncnn（专为嵌入式平台优化的目标检测算法库）
- **不涉及**：后续的自动倒垃圾或自动充电功能
- **专注解决**：最有趣、最具挑战性的"动态拦截"问题

## 2. 原型开发路线：从"跟手"到"追垃圾"

成功的复杂项目源于清晰的迭代。我们坚信"分而治之"的工程哲学，将这个看似魔术般的功能拆解为四个逻辑严密、逐级递进的原型。

### 原型1：两轮"跟手"小车 —— 验证"大脑"
**目标**：验证"检测-追踪"的核心算法闭环

**硬件配置**：
- 基础两轮差速驱动小车
- 树莓派 + 摄像头
- L298N电机驱动模块
- 简单的底盘结构

**核心任务**：
- 训练一个"手部"检测模型
- 实现基础的"视觉伺服"算法
- 根据手在画面中的位置（偏左、偏右、过远、过近）实时调整两个轮子的转速
- 实现对"手"的稳定跟随

**进化价值**：
这是项目的"0到1"突破。它将证明我们的AI检测、PID控制和电机驱动能跑通一个完整的闭环，让机器"活"起来。

### 原型2：全向轮"跟手"底盘 —— 升级"机动性"
**目标**：解决两轮底盘的致命缺陷——无法平移

**硬件升级**：
- 激光切割的圆盘基座
- 三个全向轮（Mecanum轮或全向轮）
- JGA25（或同级）带编码器的电机
- 改进的驱动电路

**核心任务**：
- 沿用原型1的"跟手"算法
- 将控制输出从"前进/转向"升级为"前进/平移"
- 实现真正的全向移动能力

**进化价值**：
垃圾从空中落下时，我们最需要的是"瞬时平移"能力（即"横着走"）。全向轮底盘是实现"拦截"动作的物理基础。此阶段，我们的底盘硬件将进化到最终形态。

### 原型3：全向轮"追垃圾" —— 锁定"目标"
**目标**：将追踪对象从"手"切换到"垃圾"

**硬件配置**：
- 100%沿用原型2的全向轮底盘
- 相同的计算平台和摄像头系统

**核心任务**：
- 在PC上训练专门检测常见垃圾（纸团、瓶子、易拉罐）的Yolo模型
- 将训练好的模型部署到树莓派上
- 替换检测目标，从"手部"切换到"垃圾物体"
- 优化视觉伺服算法以适应垃圾的运动特性

**进化价值**：
这是我们首次实现项目的最终核心功能。此时，原型机已经能做到"扔出纸团、底盘瞬移拦截"。项目的AI能力进化到最终形态。

### 原型4：一体化集成 —— 进化"形态"
**目标**：从"实验室原型"进化为"可演示成品"

**核心任务**：
- 将原型3的整个底盘系统集成到垃圾桶外壳内部
- 解决内部供电方案（电池管理、电源分配）
- 结构固定和重心稳定优化
- 美化和用户体验提升

**进化价值**：
解决最后的工程化问题，这是项目从"能用"到"好用"的最后一步，实现真正的智能垃圾桶产品原型。

## 3. 核心算法：高速"视觉伺服"

我们的核心算法放弃了"弹道预测"这条复杂的路线。该路线需要双目相机或雷达来解算3D坐标，并用卡尔曼滤波去拟合抛物线，在树莓派上极难实时实现。

我们选择了一个更直接、更鲁棒的方案："视觉伺服"（Visual Servoing）。

### 算法理念
这个算法的理念很纯粹：我不需要知道垃圾的物理轨迹，我只需要保证垃圾在我的视野（摄像头画面）中永远处于"准星"位置。

### 算法工作流程（每秒执行20-30次）

#### 3.1 感知（Sense）
```cpp
// 1. 图像捕获
cv::Mat frame = captureFrame();  // OpenCV捕捉一帧图像

// 2. 目标检测
std::vector<TargetBox> detections;
yoloDetector.detection(frame, detections, threshold);  // YoloFastestV2-ncnn处理

// 3. 获取目标2D坐标
if (!detections.empty()) {
    Point2f target_pos(detections[0].x1 + detections[0].x2 / 2,
                      detections[0].y1 + detections[0].y2 / 2);
}
```
- OpenCV捕捉一帧图像
- YoloFastestV2-ncnn立即处理，以极低延迟（例如30ms）返回目标（垃圾）在画面中的2D坐标(x, y)

#### 3.2 决策（Decide）
```cpp
// 1. 定义"准星"
Point2f setpoint(frame.cols / 2, frame.rows * 0.8);  // 目标点

// 2. 计算误差
float error_x = target_pos.x - setpoint.x;  // 水平误差
float error_y = setpoint.y - target_pos.y;  // 垂直/距离误差

// 3. PID控制计算
float translation_speed = pid_x.calculate(error_x);  // 平移速度
float forward_speed = pid_y.calculate(error_y);     // 前进速度
```

**定义"准星"**：
- 程序中定义一个"目标点(Setpoint)"
- X_target = 画面宽度 / 2（水平居中）
- Y_target = 画面高度 * 0.8（垂直位置在画面下方）
- **精妙设计**：Y轴目标点在画面下方，迫使垃圾桶始终试图"钻"到垃圾的正下方

**误差计算**：
- Error_X = x - X_target（水平误差）
- Error_Y = Y_target - y（垂直/距离误差）

**PID控制**：
- 使用两个独立的高层PID控制器
- **平移PID**：Error_X作为输入 → PID_X控制器 → 输出左右平移速度Vy
- **前进PID**：Error_Y作为输入 → PID_Y控制器 → 输出前后前进速度Vx

#### 3.3 执行（Act）
```cpp
// 1. 运动学解算
Vector3f wheel_speeds = kinematics.inverse(forward_speed, translation_speed, 0);

// 2. 底层电机控制
motor1.setSpeed(wheel_speeds.x);
motor2.setSpeed(wheel_speeds.y);
motor3.setSpeed(wheel_speeds.z);

// 3. 编码器反馈和底层PID
motor1.updatePID();
motor2.updatePID();
motor3.updatePID();
```

**运动学解算**：
- 运动学模型（为全向轮底盘编写）接收目标速度(Vx, Vy, Wz=0)
- 瞬间计算出三个电机各自需要达到的目标转速(w1, w2, w3)

**底层PID执行**：
- 电机的编码器实时反馈当前转速
- 底层的速度PID（在pigpio库支持下）确保电机以极高精度和极快响应，立刻达到目标转速

## 4. 技术架构设计

### 4.1 硬件架构
```
+---------------------------+
|   树莓派4B (超频)        |
|  - YoloFastestV2推理      |
|  - 视觉伺服算法           |
|  - 运动学解算             |
+---------------------------+
        |         |
        v         v
+-----------+  +-----------+
|  高速摄像头|  |  电机驱动  |
+-----------+  +-----------+
        |         |
        v         v
+---------------------------+
|     全向轮底盘系统        |
|  - 3个JGA25编码器电机     |
|  - 激光切割圆盘基座       |
+---------------------------+
```

### 4.2 软件架构
```cpp
class VisualServoController {
private:
    YoloFastestV2 detector;
    PIDController pid_x, pid_y;
    OmniKinematics kinematics;
    MotorController motors[3];

    Point2f setpoint;
    float loop_frequency;

public:
    void initialize();
    void updateLoop();
    void processFrame(cv::Mat& frame);
    void calculateControl(Point2f target);
    void executeMotion(Vector3f velocities);
};

class OmniKinematics {
public:
    // 运动学正解算：轮速 -> 机器人速度
    Vector3f forwardKinematics(float w1, float w2, float w3);

    // 运动学逆解算：机器人速度 -> 轮速
    Vector3f inverseKinematics(float vx, float vy, float wz);

    // 全向轮排列参数
    float wheel_radius;
    float robot_radius;
    float wheel_angles[3];
};
```

### 4.3 实时性能保证
- **帧率目标**：20-30 FPS（33-50ms周期）
- **检测延迟**：< 30ms（YoloFastestV2优化）
- **控制周期**：1ms（pigpio硬件PWM）
- **总体延迟**：< 100ms（从看到到动作）

## 5. 关键技术挑战与解决方案

### 5.1 实时性挑战
**挑战**：树莓派上的实时AI推理和运动控制
**解决方案**：
- 使用NCNN框架的模型优化
- 树莓派超频提升算力
- 多线程并行处理（视觉线程 + 控制线程）
- 算法优化：ROI区域检测，减少计算量

### 5.2 精度挑战
**挑战**：高速运动中的精确定位和拦截
**解决方案**：
- 高精度编码器反馈
- 双层PID控制（高层视觉PID + 底层速度PID）
- 运动学精确建模
- 系统延迟补偿算法

### 5.3 鲁棒性挑战
**挑战**：复杂环境下的稳定运行
**解决方案**：
- 多目标跟踪算法
- 目标丢失后的预测和搜索策略
- 传感器数据融合（视觉+编码器）
- 异常状态检测和恢复机制

## 6. 当前实现状态

### 6.1 已完成部分
- ✅ YoloFastestV2环境配置和基础检测
- ✅ 三分类检测模型（Paper, bottle, can）
- ✅ 基础的图像处理和显示功能
- ✅ 实时摄像头捕获和FPS统计

### 6.2 下一步开发重点
1. **原型1阶段**：实现PID控制器和底层电机驱动
2. **视觉伺服**：连接检测结果到PID控制输入
3. **两轮底盘**：基础运动控制和闭环验证
4. **全向轮升级**：运动学建模和三电机协调控制

### 6.3 PID控制系统设计
基于已实现的手部检测，下一步需要实现连接检测输出到电机控制的完整链路：

#### 3层控制架构
```cpp
// 高层视觉PID控制器（20-30Hz）
class VisualPIDController {
    Point2f setpoint;           // 目标点(画面中心)
    PID pid_x, pid_y;           // 分别控制水平/垂直误差
    Point2f last_target;        // 上次目标位置

    // 核心算法：将画面误差转换为机器人运动指令
    MotionCommand calculate(Point2f current_target);
};

// 中层运动学解算（实时）
class DifferentialKinematics {
    // 将(vx, vy)转换为左右轮速度
    WheelSpeeds inverse(float vx, float vy, float wz);
    // 将轮速转换为机器人速度（用于状态估计）
    RobotVelocity forward(float wl, float wr);
};

// 底层电机PID控制器（1kHz）
class MotorController {
    PID speed_pid;              // 速度环PID
    Encoder encoder;            // 编码器反馈
    PWMGenerator pwm;           // PWM输出

    // 核心功能：精确速度控制
    void setSpeed(float target_speed);
    float getCurrentSpeed();    // 从编码器获取实际速度
};
```

## 7. 项目里程碑

### 近期目标（1-2周）
- [x] 完成手部检测模型训练
- [ ] 实现基础PID控制器
- [ ] 搭建两轮差速底盘
- [ ] 完成"跟手"功能验证

### 中期目标（3-4周）
- [ ] 升级为全向轮底盘
- [ ] 实现全向运动学控制
- [ ] 完成垃圾检测模型训练
- [ ] 实现"追垃圾"核心功能

### 长期目标（5-6周）
- [ ] 一体化垃圾桶外壳设计
- [ ] 系统集成和优化
- [ ] 性能调优和可靠性测试
- [ ] 最终演示和展示

---

**项目特色**：基于视觉伺服的实时动态拦截，避免了复杂的3D轨迹预测，专注于嵌入式平台的可行性实现
**核心技术**：YoloFastestV2 + 全向轮运动学 + 双层PID控制
**开发理念**：渐进式原型迭代，从简单到复杂，确保每步都可验证
**最后更新**：2025-11-07