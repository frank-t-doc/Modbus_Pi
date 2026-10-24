# reader_smartmeter.py
import serial
from parser.frame_router import route_frame

def reader_smartmeter(port="/dev/ttyUSB1", baud=9600):
    ser = serial.Serial(port, baudrate=baud, timeout=0.01)

    print(f"Smartmeter-Reader gestartet auf {port}")

    buffer = bytearray()
    last_byte_time = 0
    FRAME_TIMEOUT = 0.015

    import time

    while True:
        chunk = ser.read(200)
        now = time.time()

        if chunk:
            buffer.extend(chunk)
            last_byte_time = now

        if (now - last_byte_time) > FRAME_TIMEOUT and len(buffer) > 0:

            frame_hex = buffer.hex()
            decoded = route_frame(frame_hex)
            print(decoded)

            buffer = bytearray()

        time.sleep(0.001)
