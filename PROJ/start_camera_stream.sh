#!/bin/bash
# start_camera_stream.sh
# Script to start mjpg-streamer with USB camera and system monitoring

echo "🚀 Starting USB camera stream with system monitoring..."

# Settings
WIDTH=640
HEIGHT=480
FPS=30
PORT=8080
DEVICE="/dev/video0"

# Get the IP address
IP=$(hostname -I | awk '{print $1}')

# Start system info API server (port 5001)
echo "🖥️ Starting system info API server (port 5001)..."

# 检查端口是否被占用
if sudo netstat -tlnp | grep -q ":5001"; then
    echo "⚠️  Port 5001 is in use, killing existing process..."
    sudo pkill -f "system_info_server.py" 2>/dev/null || true
    sleep 1
fi

# 启动系统信息服务器
nohup python3 mjpg-streamer/system_info_server.py > /tmp/system_info.log 2>&1 &
SYSINFO_PID=$!

# 等待服务器启动
sleep 3

# 检查服务器是否启动成功
if kill -0 $SYSINFO_PID 2>/dev/null; then
    echo "✅ System info API server started (PID: $SYSINFO_PID)"

    # 验证API是否工作
    if curl -s http://localhost:5001/system_info.json > /dev/null; then
        echo "✅ API endpoint is responding"
    else
        echo "⚠️  API server started but endpoint not responding yet"
    fi
else
    echo "❌ System info server failed to start"
    echo "📋 Check log: tail -f /tmp/system_info.log"
    SYSINFO_PID=""
fi

# Start mjpg-streamer with USB camera
echo "📹 Starting USB camera stream (port $PORT)..."
echo "📱 Access URLs:"
echo "   🎯 System Monitor: http://$IP:$PORT/system_monitor.html"
echo "   📹 Camera Stream: http://$IP:$PORT/?action=stream"
echo "   📸 Snapshot: http://$IP:$PORT/?action=snapshot"
echo ""
echo "🛑 Stop with: Ctrl+C"
echo ""

# Export path for mjpg-streamer plugins
export LD_LIBRARY_PATH="$(pwd)/mjpg-streamer/mjpg-streamer-experimental/_build"

# Start the stream directly with USB camera
./mjpg-streamer/mjpg-streamer-experimental/_build/mjpg_streamer \
    -i "./mjpg-streamer/mjpg-streamer-experimental/_build/plugins/input_uvc/input_uvc.so --device $DEVICE --resolution ${WIDTH}x${HEIGHT} --fps $FPS" \
    -o "./mjpg-streamer/mjpg-streamer-experimental/_build/plugins/output_http/output_http.so --port $PORT --www ./mjpg-streamer/mjpg-streamer-experimental/www" &

STREAM_PID=$!

echo "✅ Services started:"
echo "   Camera Stream PID: $STREAM_PID"
echo "   System Info PID: $SYSINFO_PID"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $STREAM_PID 2>/dev/null
    kill $SYSINFO_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait for both processes
wait