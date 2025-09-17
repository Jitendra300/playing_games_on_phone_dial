# This has implementation of guessing game, the simplest game which I can think of to be build using the help of phone dial

import os
import random
import serial
import time
import string
from dotenv import load_dotenv

# -- Loading Environment Variables --
load_dotenv()

PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
TIMEOUT = 5

PHONE_NUMBER = os.getenv("PHONE_NUMBER")
if not PHONE_NUMBER:
    print("ERROR: PHONE_NUMBER not found in .env file.")
    exit(1)

# To hide our true number in the terminal output we use this masked variable.
MASKED_NUMBER = "+ZZXXXXXXXXXX"


# Establishing serial connection
ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)

def send_command(cmd, delay=1):
    masked_output = cmd.replace(PHONE_NUMBER, MASKED_NUMBER) # masking true number
    print(f">> {masked_output}")
        
    ser.write((cmd + '\r').encode())
    time.sleep(delay)

# Sometimes we get gibberish output for various reasons thus we use this function to get rid of them
def is_mostly_printable(s, threshold=0.9):
    if not s:
        return False
    printable = set(string.printable)
    return sum(c in printable for c in s) / len(s) > threshold

send_command('AT')        # Should return 'OK'
send_command('AT+DDET=1') # Enable DTMF

# --- Making the Call ---
send_command(f'ATD{PHONE_NUMBER};', delay=2)

# --- Waiting for the call to be answered using AT+CLCC ---
print("Waiting for call to be answered...")
call_answered = False
start_time = time.time()
call_failed = False

# Loop for up to 30 seconds to check call status
while time.time() - start_time < 30:
    ser.write(b'AT+CLCC\r')
    time.sleep(1)

    while ser.in_waiting:
        response = ser.readline().decode('utf-8', errors='ignore').strip()
        if response:
            masked_response = response.replace(PHONE_NUMBER, MASKED_NUMBER)
            print(f"<< {masked_response}")
            
            if response.startswith("+CLCC:"):
                parts = response.split(',')
                if len(parts) >= 3 and parts[2] == '0':
                    print("Call is active!")
                    call_answered = True
                    break
            elif "NO CARRIER" in response or "BUSY" in response or "NO ANSWER" in response:
                print("Call failed, was rejected, or not answered.")
                call_failed = True
                break
    
    if call_answered or call_failed:
        break

if not call_answered:
    print("Call was not answered. Hanging up...")
    send_command('ATH') # Hang up command
    ser.close()
    exit(0)

# --- Play Rules and Start Game (only if call was answered) ---
print("Call picked up. Playing rules audio...")
time.sleep(1) # Just keeping one second delay so that I can keep speaker and listen more clearly...[speaker recommened for deaf ppl like me ;) ]
send_command('AT+CREC=4,"C:\\2.amr",0,100') # Play the rules audio file

# Generate the random number the user has to guess
guess = str(random.randint(0, 9))
print(f"Secret number is: {guess}")

try:
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if is_mostly_printable(line):
            masked_line = line.replace(PHONE_NUMBER, MASKED_NUMBER)
            print(f"<< {masked_line}")
            
            if "+DTMF:" in line:
                digit = line.split(":")[1].strip()
                print(f"Player guessed: {digit}")
                
                if digit == guess:
                    print("Congratulations! You have won the game.")
                    send_command('AT+CREC=4,"C:\\1.amr",0,100') # Play "congrats" audio
                    time.sleep(3)
                    break
                else:
                    print("Wrong guess! Try again.")
                    send_command('AT+CREC=4,"C:\\3.amr",0,100') # Play "try again" audio

except KeyboardInterrupt:
    print("\nProgram interrupted by user.")
finally:
    print("Game over. Disconnecting.")
    send_command('ATH') # Hang up the call
    ser.close()
    print("Disconnected.")
