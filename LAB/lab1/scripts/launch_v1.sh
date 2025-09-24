#!/bin/bash
#
# jfs9: 9/5/2024: script to launch multiple processes
#

echo "Running: python t0.py &"
python t0.py &

echo "Running (a second time): python t0.py &"
python t0.py &

