


import serial
import struct

FRAME_START = bytes([
    0x04, 0x03, 0x20, 0x12,
    0x00, 0x08, 0xEF, 0x9C
])

FRAME_LEN = 29

def decode_float(data):
    return struct.unpack(">f", data)[0]

def parse_frame(frame):

    response = frame[8:]

    slave = response[0]
    function = response[1]
    byte_count = response[2]

    if byte_count != 16:
        return None

    data = response[3:19]

    pt = decode_float(data[0:4]) * 0.1
    pa = decode_float(data[4:8]) * 0.1
    pb = decode_float(data[8:12]) * 0.1
    pc = decode_float(data[12:16]) * 0.1

    return {
        "pt_w": round(pt, 1),
        "pa_w": round(pa, 1),
        "pb_w": round(pb, 1),
        "pc_w": round(pc, 1),

        "phase_sum_w": round(
            pa + pb + pc,
            1
        ),

        "crc": response[-2:].hex()
    }


def run_sniffer():

    ser = serial.Serial(
        "/dev/ttyUSB0",
        9600,
        timeout=0.2
    )

    buffer = bytearray()

    print("ShineMaster DTSU666 Parser läuft...")

    while True:

        chunk = ser.read(256)

        if not chunk:
            continue

        buffer.extend(chunk)

        while True:

            idx = buffer.find(FRAME_START)

            if idx < 0:
                break

            if len(buffer) < idx + FRAME_LEN:
                break

            frame = buffer[idx: idx + FRAME_LEN]

            del buffer[: idx + FRAME_LEN]

            parsed = parse_frame(frame)

            if parsed:
                print(parsed)

                # write_smartmeter(parsed)