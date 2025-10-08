# blink_pwm.py
# Description: Blinks an LED using RPi.GPIO's hardware/software PWM at a command line specified frequency.

import RPi.GPIO as GPIO
import time
import threading
import sys

# --- Configuration ---
LED_PIN = 26 
INITIAL_FREQUENCY_HZ = 1.0  # Initial frequency: 1 Hz 
DUTY_CYCLE = 50.0 # Fixed duty cycle: 50% 
running = True

# Global PWM object reference
pwm_instance = None

def led_pwm_thread():
    """Initializes and runs the PWM instance."""
    global pwm_instance
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    
    # Create a PWM instance
    pwm_instance = GPIO.PWM(LED_PIN, INITIAL_FREQUENCY_HZ)
    
    # Start PWM: p.start(dc) 
    pwm_instance.start(DUTY_CYCLE) 
    
    print(f"PWM Blinker thread started on GPIO {LED_PIN} at {INITIAL_FREQUENCY_HZ} Hz / {DUTY_CYCLE}% DC.")

    while running:
        time.sleep(0.1) # Keep the thread alive while waiting for the main thread to update PWM

def update_frequency(new_freq):
    """Changes the frequency of the running PWM instance."""
    global pwm_instance
    if pwm_instance:
        try:
            # To change the frequency
            pwm_instance.ChangeFrequency(new_freq)
            return True
        except Exception as e:
            print(f"Failed to change frequency: {e}")
            return False
    return False

def command_line_input_thread():
    """Handles continuous reading of frequency input from the command line."""
    global running
    current_freq = INITIAL_FREQUENCY_HZ

    print("\nEnter a blink frequency (Hz). Enter 0 to quit the program. \n")
    
    while running:
        try:
            new_freq_str = input(f"Current Freq: {current_freq:.2f} Hz. Enter New Freq (int): ")
            new_freq = int(new_freq_str)
            
            if new_freq == 0:
                # Special entry to quit 
                running = False
                print("Quit command received. Exiting...")
                break
            elif new_freq > 0:
                if update_frequency(new_freq):
                    current_freq = float(new_freq)
                    print(f"Frequency updated to {current_freq} Hz.")
            else:
                print("Invalid frequency. Please enter a positive integer or 0 to quit.")
                
        except ValueError:
            print("Invalid input. Please enter an integer.")
        except EOFError:
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
        blinker = threading.Thread(target=led_pwm_thread)
        blinker.start()
        
        # Give time for PWM object to be initialized
        time.sleep(0.5) 
        
        # Run the command line input reading in the main thread
        command_line_input_thread()

    except KeyboardInterrupt:
        print("\nProgram stopped by user (Ctrl+C).")
        running = False
        
    finally:
        # To stop PWM: p.stop() 
        if pwm_instance:
            pwm_instance.stop()
        
        # Cleanup GPIO after all threads have stopped
        running = False
        if 'blinker' in locals() and blinker.is_alive():
            blinker.join() 
            
        GPIO.cleanup()
        print("GPIO cleanup complete. Program finished.")