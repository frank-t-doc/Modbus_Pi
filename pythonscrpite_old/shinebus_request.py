import serial
import time

PORT = "/dev/ttyUSB0"
BAUD = 9600

# Beispiel-Request: ShineBus CMD 0x01 (Status)
# Format: AA 55 LEN CMD DATA CRC
# Minimaler Request ohne Daten
request = bytes.fromhex("AA55 04 01 00 00 00")

ser = serial.Serial(PORT, BAUD, timeout=1)

print("Sende ShineBus-Request...")

while True:
    ser.write(request)
    time.sleep(0.2)

    response = ser.read(64)
    if response:
        print("Antwort:", response.hex())

