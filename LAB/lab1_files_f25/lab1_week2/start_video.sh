#!/bin/bash
# start_video.sh - Launch video playback and control program
# ECE 5725 Lab 1 Week 2

# Ensure FIFO exists
FIFO_PATH="/home/pi/video_fifo"
[ -p "$FIFO_PATH" ] || mkfifo "$FIFO_PATH"

# Start video control program (run in background)
echo "Starting video control program..."
python3 /home/pi/lab1_files_f25/lab1_week2/video_control.py &

# Wait a moment to ensure control program is started
sleep 1

# Start mplayer to play video
# Note: Replace video.mp4 with actual video file path
echo "Starting video playback..."
mplayer -fs -vo fbdev2:/dev/fb1 -input file="$FIFO_PATH" video.mp4