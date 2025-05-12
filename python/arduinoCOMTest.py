import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)  # Replace with correct COM port and baud rate
time.sleep(2)  # Wait for Arduino to reset

ser.write(b'Hello\n')
response = ser.readline().decode('utf-8')
print("Response:", response)

ser.close()
