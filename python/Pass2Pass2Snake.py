import serial
import time

# Connect to Arduino
ser = serial.Serial('COM3', 115200, timeout=1)  # Change port as needed
time.sleep(2)

# Send shoot command
ser.write(b"pass2pass2snake\n")
print("Pass to pass to snake shot triggered")

# Listen for Arduino response
while True:
    response = ser.readline().decode().strip()
    if response:
        print("Arduino:", response)
    if "Pass to pass to snake shot done" in response:
        break

ser.close()
