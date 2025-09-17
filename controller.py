# This is explicitly made to work with DOOM, so kindly change the keybindings to make it work in any game...!

import os
import evdev
from evdev import UInput, ecodes as e
import serial
import time
import string
from dotenv import load_dotenv

# --- Loading Environment Variables ---
load_dotenv()

# --- Variables & Configuration ---
PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
TIMEOUT = 5

PHONE_NUMBER = os.getenv("PHONE_NUMBER")
if not PHONE_NUMBER:
    print("ERROR: PHONE_NUMBER not found in .env file.")
    exit(1)

# To hide our true number in the terminal output we use this masked variable.
MASKED_NUMBER = "+ZZXXXXXXXXXX"

# --- Keycode Definitions ---
KEY_FORWARD = e.KEY_W
KEY_BACKWARD = e.KEY_S
KEY_RIGHT = e.KEY_D
KEY_LEFT = e.KEY_A
KEY_OPEN = e.KEY_SPACE
KEY_SHOOT = e.KEY_LEFTCTRL

# Define the capabilities of our virtual keyboard
caps = {
    e.EV_KEY: [KEY_FORWARD, KEY_BACKWARD, KEY_RIGHT, KEY_LEFT, KEY_OPEN, KEY_SHOOT]
}

def press_and_release(ui_device, key_code, press_duration=0.1):
    print(f"Simulating key press: {e.KEY.get(key_code, key_code)}")
    ui_device.write(e.EV_KEY, key_code, 1)  # Press
    ui_device.syn()
    time.sleep(press_duration)
    ui_device.write(e.EV_KEY, key_code, 0)  # Release
    ui_device.syn()

def send_command(cmd, delay=1):
    printable_cmd = cmd.replace(PHONE_NUMBER, MASKED_NUMBER)
    print(f">> {printable_cmd}")
    ser.write((cmd + '\r').encode())
    time.sleep(delay)

# --- Main Application ---
ser = None
ui = None
try:
    # Establishing serial connection
    ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)

    send_command('AT') # Should response with 'OK'
    send_command('AT+DDET=1')  # Enable DTMF detection

    # --- Make the Call ---
    send_command(f'ATD{PHONE_NUMBER};', delay=3)

    print("Waiting for call to be answered...")
    call_answered = False
    start_time = time.time()
    call_failed = False

    while time.time() - start_time < 45: # Keeping 45 second as max time before call is declared dead
        ser.write(b'AT+CLCC\r')
        time.sleep(1.5)

        while ser.in_waiting:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                printable_response = response.replace(PHONE_NUMBER, MASKED_NUMBER)
                print(f"<< {printable_response}")

                if response.startswith("+CLCC:"):
                    parts = response.split(',')
                    if len(parts) >= 3 and parts[2] == '0': # Status '0' is ACTIVE
                        print("Call is active! Starting game controller...")
                        call_answered = True
                        break
                elif "NO CARRIER" in response or "BUSY" in response or "NO ANSWER" in response:
                    print("Call failed or was not answered.")
                    call_failed = True
                    break
        if call_answered or call_failed:
            break

    # --- Start Game Loop (only if call was answered) ---
    if call_answered:
        # Create the virtual keyboard device
        ui = UInput(caps, name='doom-virtual-keyboard')
        print("Virtual keyboard created. Listening for DTMF tones...")

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line and "+DTMF:" in line:
                key = line.split(":")[1].strip()
                if key == '2':   # Up
                    press_and_release(ui, KEY_FORWARD, 0.5)
                elif key == '8': # Down
                    press_and_release(ui, KEY_BACKWARD, 0.5)
                elif key == '4': # Left
                    press_and_release(ui, KEY_LEFT, 0.5)
                elif key == '6': # Right
                    press_and_release(ui, KEY_RIGHT, 0.5)
                elif key == '5': # Open Door / Use
                    press_and_release(ui, KEY_OPEN, 0.2)
                elif key == '0': # Shoot
                    press_and_release(ui, KEY_SHOOT, 0.2)
    else:
        print("Could not establish an active call. Exiting.")

except KeyboardInterrupt:
    print("\nProgram interrupted by user.")
except Exception as e:
    print(f"\nAn error occurred: {e}")
    print("This might be a permissions issue. Did you run the script with 'sudo'?")
finally:
    print("Cleaning up and disconnecting...")
    if ser and ser.is_open:
        # Hang up the call if it was ever active
        send_command('ATH')
        ser.close()
        print("Serial port closed.")
    if ui:
        ui.close()
        print("Virtual keyboard destroyed.")
    print("Disconnected.")
