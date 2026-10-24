import serial

PORT = "/dev/ttyUSB0"
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)

print("ShineBus Debug gestartet...")

while True:
    raw = ser.read(1)
    if raw:
        print(f"Byte: {raw.hex()}")
