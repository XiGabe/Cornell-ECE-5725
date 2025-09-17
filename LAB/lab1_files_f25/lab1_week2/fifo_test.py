#!/usr/bin/env python3
"""
fifo_test.py - Test program for controlling mplayer through a FIFO
ECE 5725 Lab 1 Week 2
"""

import os
import sys

# FIFO file path
FIFO_PATH = '/home/pi/video_fifo'

def create_fifo():
    """Create FIFO if it doesn't exist"""
    if not os.path.exists(FIFO_PATH):
        os.mkfifo(FIFO_PATH)

def send_command(command):
    """Send command to FIFO"""
    with open(FIFO_PATH, 'w') as fifo:
        fifo.write(command + '\n')
        fifo.flush()

def print_help():
    """Print help information"""
    print("\nAvailable commands:")
    print("pause      - Pause/Resume playback")
    print("seek 10    - Forward 10 seconds")
    print("seek -10   - Rewind 10 seconds")
    print("quit      - Exit program")
    print("help      - Show this help message")
    print("")

def main():
    # Ensure FIFO exists
    create_fifo()
    
    print("mplayer FIFO Control Test Program")
    print("Enter 'help' to see available commands")
    
    while True:
        try:
            command = input("Enter command: ").strip()
            
            if command == "":
                continue
                
            if command == "help":
                print_help()
                continue
                
            if command == "quit":
                print("Exiting program...")
                send_command("quit")
                break
                
            # Send command to FIFO
            send_command(command)
            
        except KeyboardInterrupt:
            print("\nProgram interrupted by user")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()