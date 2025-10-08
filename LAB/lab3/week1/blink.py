# blink.py
# Description: Blinks an LED connected to a GPIO pin at a frequency read from the command line.
# Uses non-PWM RPi.GPIO calls.

import RPi.GPIO as GPIO
import time
import threading
import sys

# --- Configuration ---
LED_PIN = 26 
BLINK_FREQUENCY_HZ = 1.0  # Initial frequency: 1 Hz 
DUTY_CYCLE_PERCENT = 50.0 # Fixed duty cycle: 50% 
running = True

def led_blinker_thread():
    """Controls the LED blinking at the global BLINK_FREQUENCY_HZ."""
    global BLINK_FREQUENCY_HZ
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    
    print(f"Blinker thread started on GPIO {LED_PIN}.")

    while running:
        try:
            # Calculate the period and ON/OFF times based on the current frequency
            if BLINK_FREQUENCY_HZ > 0:
                period = 1.0 / BLINK_FREQUENCY_HZ
                # For a 50% duty cycle, ON time = OFF time = period / 2
                on_time = period * (DUTY_CYCLE_PERCENT / 100.0)
                off_time = period * (1.0 - (DUTY_CYCLE_PERCENT / 100.0))
                
                # Turn LED ON (HIGH)
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(on_time)
                
                # Turn LED OFF (LOW)
                GPIO.output(LED_PIN, GPIO.LOW)
                time.sleep(off_time)
            else:
                # Frequency = 0 is the special 'quit' entry 
                GPIO.output(LED_PIN, GPIO.LOW) # Ensure LED is off
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error in blinker thread: {e}")
            break

def command_line_input_thread():
    """Handles continuous reading of frequency input from the command line."""
    global BLINK_FREQUENCY_HZ
    global running

    print("\nEnter a blink frequency (Hz). Enter 0 to quit the program. \n")
    
    while running:
        try:
            # Read input from the command line 
            new_freq_str = input(f"Current Freq: {BLINK_FREQUENCY_HZ:.2f} Hz. Enter New Freq (int): ")
            new_freq = int(new_freq_str)
            
            if new_freq == 0:
                # Special entry to quit 
                running = False
                print("Quit command received. Exiting...")
                break
            elif new_freq > 0:
                BLINK_FREQUENCY_HZ = float(new_freq)
                print(f"Frequency updated to {BLINK_FREQUENCY_HZ} Hz.")
            else:
                print("Invalid frequency. Please enter a positive integer or 0 to quit.")
                
        except ValueError:
            print("Invalid input. Please enter an integer.")
        except EOFError:
            # Handles Ctrl+D/End of File which might occur in some terminal environments
            running = False
            print("\nEOF received. Exiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            running = False
            break

if __name__ == '__main__':
    try:
        # Start the LED control thread
        blinker = threading.Thread(target=led_blinker_thread)
        blinker.start()
        
        # Run the command line input reading in the main thread (or another thread)
        command_line_input_thread()

    except KeyboardInterrupt:
        print("\nProgram stopped by user (Ctrl+C).")
        running = False
        
    finally:
        # Cleanup GPIO after all threads have stopped
        running = False
        if 'blinker' in locals() and blinker.is_alive():
            blinker.join() # Wait for the blinker thread to finish
            
        GPIO.cleanup()
        print("GPIO cleanup complete. Program finished.")