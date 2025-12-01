#!/bin/bash

# 视觉伺服系统测试脚本
# 这个脚本会启动YOLO手部检测和电机控制系统

echo "===================================="
echo "  视觉伺服手部跟踪系统"
echo "===================================="
echo ""
echo "功能说明："
echo "- 实时检测手部位置"
echo "- 自动跟踪手部移动"
echo "- 根据手部距离控制前进后退"
echo "- 根据手部位置控制左右转向"
echo ""
echo "安全提醒："
echo "- 确保小车有足够空间移动"
echo "- 可以随时按Ctrl+C停止"
echo "- 电机会在没有检测到手部时自动停止"
echo ""

read -p "按Enter键开始测试，或按Ctrl+C退出..."

echo ""
echo "启动视觉伺服系统..."
echo "需要root权限控制GPIO"
echo ""

# 使用sudo运行，因为需要控制GPIO
sudo ./mainFV2

echo ""
echo "系统已停止"