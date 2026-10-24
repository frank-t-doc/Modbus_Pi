import serial
import time
import binascii
from parser import parse_modbus_frame
import paho.mqtt.publish as publish

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600

FRAME_TIMEOUT = 0.015  # 15 ms Pause = Frame-Ende


def try_parse_frame(buf):

    """Try to parse a Modbus RTU frame."""
    if len(buf) < 5:
        return None

    slave = buf[0]
    func = buf[1]

    # Request frames (always 8 bytes for function 03)
    if func == 0x03 and len(buf) == 8:
        return {"type": "request", "slave": slave}

    # Response frames
    if func == 0x03:
        byte_count = buf[2]
        expected_len = 3 + byte_count + 2

        if len(buf) == expected_len:
            hex_frame = binascii.hexlify(buf).decode()
            parsed = parse_modbus_frame(hex_frame)
            return parsed

    return None


def main():
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.01)

    buffer = bytearray()
    last_byte_time = time.time()

    print("Live-Sniffer + Parser läuft...")

    while True:
        chunk = ser.read(200)
        now = time.time()

        if chunk:
            buffer.extend(chunk)
            last_byte_time = now

        # Frame-Ende durch Pause
        if (now - last_byte_time) > FRAME_TIMEOUT and len(buffer) > 0:

            parsed = try_parse_frame(buffer)

    if parsed:
        print("\n=== Neuer Frame ===")
        print("RAW:", binascii.hexlify(buffer).decode())
        print("Parsed:", parsed)

    # MQTT Publish
    try:
        publish.multiple([
            ("energy/growatt/system/timestamp", parsed.get("timestamp", "")),
            ("energy/growatt/system/frame_counter", parsed.get("frame_counter", 0)),
            ("energy/growatt/pv/power", parsed.get("pv_power", 0)),
            ("energy/growatt/pv/energy_today", parsed.get("energy_today", 0)),
            ("energy/growatt/pv/energy_total", parsed.get("energy_total", 0)),
            ("energy/growatt/pv/string_energy", parsed.get("energy_string", 0)),
            ("energy/growatt/grid/power", parsed.get("grid_power", 0)),
            ("energy/growatt/grid/voltage", parsed.get("grid_voltage", 0)),
            ("energy/growatt/grid/frequency", parsed.get("grid_frequency", 0)),
        ], hostname="DEIN_MQTT_BROKER")
    except Exception as e:
        print("MQTT-Fehler:", e)

        buffer = bytearray()

        time.sleep(0.001)


if __name__ == "__main__":
    main()
