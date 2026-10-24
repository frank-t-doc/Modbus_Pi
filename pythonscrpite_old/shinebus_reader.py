import serial
import struct

PORT = "/dev/ttyUSB0"
BAUD = 9600

def read_frame(ser):
    # Warten auf Startbytes AA 55
    while True:
        b1 = ser.read(1)
        if b1 == b'\xAA':
            b2 = ser.read(1)
            if b2 == b'\x55':
                break

    length = ser.read(1)[0]
    cmd = ser.read(1)[0]
    data = ser.read(length - 2)
    crc = ser.read(2)

    return cmd, data

def decode_sph(data):
    # Beispiel: Batterie-SOC, PV-Leistung, Grid-Power
    # ShineBus nutzt Little Endian 16-bit Werte
    pv_power = struct.unpack("<H", data[0:2])[0]
    battery_soc = data[2]
    grid_power = struct.unpack("<h", data[3:5])[0]

    return {
        "pv_power": pv_power,
        "battery_soc": battery_soc,
        "grid_power": grid_power
    }

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)

    print("ShineBus Reader gestartet...")

    while True:
        cmd, data = read_frame(ser)
        values = decode_sph(data)
        print(values)

if __name__ == "__main__":
    main()
