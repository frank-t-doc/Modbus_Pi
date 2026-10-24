import serial
import struct
import time

PORT = "/dev/ttyUSB0"
BAUD = 9600

def crc16(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def build_request():
    # ID = 01, Function = 03, Start = 0000, Length = 0010
    req = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x10])
    crc = crc16(req)
    req.append(crc & 0xFF)
    req.append((crc >> 8) & 0xFF)
    return bytes(req)

def decode_response(resp):
    # resp = ID, FUNC, LEN, DATA..., CRC
    if len(resp) < 5:
        return None

    length = resp[2]
    data = resp[3:3+length]

    # Beispiel-Dekodierung (Growatt Meter Mapping)
    voltage_L1 = struct.unpack(">H", data[0:2])[0] / 10.0
    current_L1 = struct.unpack(">H", data[2:4])[0] / 100.0
    power_L1   = struct.unpack(">H", data[4:6])[0]

    return {
        "voltage_L1": voltage_L1,
        "current_L1": current_L1,
        "power_L1": power_L1
    }

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    request = build_request()

    print("Growatt Meter‑Master gestartet (ID 01)...")

    while True:
        ser.write(request)
        time.sleep(0.2)

        resp = ser.read(64)
        if resp:
            print("Antwort:", resp.hex())
            decoded = decode_response(resp)
            if decoded:
                print(decoded)

        time.sleep(1)

if __name__ == "__main__":
    main()
