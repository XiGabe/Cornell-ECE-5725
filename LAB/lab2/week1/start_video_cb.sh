#!/bin/bash
# Launch mplayer and more_video_control_cb.py (interrupt version)

FIFO_PATH="/home/pi/ECE-5725-Everything/LAB/lab1_files_f25/lab1_week2/video_fifo"
[ -p "$FIFO_PATH" ] || mkfifo "$FIFO_PATH"

echo "Starting more_video_control_cb.py..."
python3 /home/pi/ECE-5725-Everything/LAB/lab2/more_video_control_cb.py &

sleep 1

echo "Starting mplayer..."
mplayer -slave -input file=$FIFO_PATH -vo fbdev:/dev/fb1 /home/pi/ECE-5725-Everything/LAB/lab1/lab1_week2/bigbuckbunny320p.mp4