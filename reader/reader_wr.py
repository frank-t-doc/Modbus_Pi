# reader_wr.py
import serial
import time
from parser.frame_router import route_frame

def reader_wr(port="/dev/ttyUSB1", baud=9600):
    ser = serial.Serial(port, baudrate=baud, timeout=0.2)

    print(f"WR-Reader gestartet auf {port}")

    def modbus_crc(data):
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, byteorder="little")

    def read_registers(slave_id, start_reg, count):
        req = bytearray([
            slave_id,
            0x03,
            (start_reg >> 8) & 0xFF,
            start_reg & 0xFF,
            (count >> 8) & 0xFF,
            count & 0xFF
        ])
        req += modbus_crc(req)

        ser.write(req)
        time.sleep(0.05)

        resp = ser.read(200)
        if len(resp) > 0:
            frame_hex = resp.hex()
            decoded = route_frame(frame_hex)
            print(decoded)

    while True:
        # SPH PV‑Block: Register 0x000A, 18 Register
        read_registers(1, 0x000A, 18)
        read_registers(2, 0x000A, 18)

        time.sleep(0.5)
