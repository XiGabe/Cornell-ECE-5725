#!/bin/bash
# Launch mplayer and more_video_control_cb.py (interrupt version)

FIFO_PATH="video_fifo"
[ -p "$FIFO_PATH" ] || mkfifo "$FIFO_PATH"

echo "Starting more_video_control_cb.py..."
python3 more_video_control_cb.py &

sleep 1

echo "Starting mplayer..."
mplayer -slave -input file=video_fifo -vo fbdev:/dev/fb1 /home/pi/ECE-5725-Everything/LAB/lab1/lab1_week2/bigbuckbunny320p.mp4