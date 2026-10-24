import serial
import time

PORT = "/dev/ttyUSB0"
BAUD = 9600

# ShineMaster Polling Frame
POLL = bytes.fromhex("AA55 04 01 00 00 00")

# ShineMaster ACK Frame
ACK  = bytes.fromhex("AA55 03 02 00 00")

def read_frame(ser):
    # Suche nach AA 55
    while True:
        b1 = ser.read(1)
        if not b1:
            return None
        if b1 == b'\xAA':
            b2 = ser.read(1)
            if b2 == b'\x55':
                break

    length = ser.read(1)
    if not length:
        return None
    length = length[0]

    cmd = ser.read(1)[0]
    data = ser.read(length - 2)
    crc = ser.read(2)

    return cmd, data, crc

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print("ShineMaster‑Emulator gestartet...")

    while True:
        # Poll senden
        ser.write(POLL)
        time.sleep(0.2)

        # Antwort lesen
        frame = read_frame(ser)
        if frame:
            cmd, data, crc = frame
            print(f"Antwort CMD={cmd}, DATA={data.hex()}")

            # ACK senden
            ser.write(ACK)

        time.sleep(1)

if __name__ == "__main__":
    main()
