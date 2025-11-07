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

# Start integrated snapshot/system info server (port 5001)
echo "🖥️ Starting integrated server (port 5001)..."
python3 mjpg-streamer/mjpg-streamer-experimental/www/snapshot_server.py &
SYSINFO_PID=$!

# Wait a moment for system info server to start
sleep 2

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