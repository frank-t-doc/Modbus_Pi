import serial
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# -----------------------------
# InfluxDB Konfiguration
# -----------------------------
INFLUX_URL = "http://192.168.10.223:8086"
INFLUX_TOKEN = "yZebaGFUz2Q9PvSLjXh1Fsy66vQx5j9D4QiQRIwl4-7mQZSRDgiJRk7bdN0_YtQMacJTK2JXLy5ns-IUI6q3rA=="
INFLUX_ORG = "TuttliesHomeBase"
INFLUX_BUCKET = "smartmeter"

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)

def write_smartmeter(values):
    point = (
        Point("shine_dtsu666")
        .tag("device", "smartmeter")
        .time(datetime.utcnow())
        .field("energy_Wh", float(values["energy_Wh"]))
        .field("power_L1_W", float(values["power_L1_W"]))
        .field("power_L2_W", float(values["power_L2_W"]))
        .field("power_L3_W", float(values["power_L3_W"]))
        .field("total_power_W", float(values["total_power_W"]))
        .field("footer_hex", values["footer"])
    )

    write_api.write(bucket=INFLUX_BUCKET, record=point)

# -----------------------------
# ShineMaster Frame Parser
# -----------------------------

FRAME_START = bytes([0x04, 0x03, 0x20, 0x12, 0x00, 0x08, 0xef, 0x9c])
FRAME_LEN = 25  # 8 Header + 15 Payload + 2 Footer

def decode_24bit(b1, b2, b3):
    raw = (b1 << 16) | (b2 << 8) | b3
    if raw & 0x800000:
        raw -= 0x1000000
    return raw

def parse_frame(frame):
    payload = frame[8:23]  # 15 bytes = 5 values
    values = []

    for i in range(0, 15, 3):
        b1, b2, b3 = payload[i:i+3]
        values.append(decode_24bit(b1, b2, b3))

    # KORREKTE DTSU666 Interpretation
    energy_Wh      = values[0] / 100
    power_L1       = values[1] / 1000
    power_L2       = values[2] / 1000
    power_L3       = values[3] / 1000
    total_power    = values[4] / 1000

    return {
        "energy_Wh": energy_Wh,
        "power_L1_W": power_L1,
        "power_L2_W": power_L2,
        "power_L3_W": power_L3,
        "total_power_W": total_power,
        "footer": frame[23:25].hex()
    }

def run_sniffer():
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.2)
    buffer = bytearray()

    print("ShineMaster DTSU666 Parser läuft...")

    while True:
        chunk = ser.read(256)
        if chunk:
            buffer.extend(chunk)

            while True:
                idx = buffer.find(FRAME_START)
                if idx == -1:
                    break

                if len(buffer) < idx + FRAME_LEN:
                    break

                frame = buffer[idx:idx + FRAME_LEN]
                del buffer[:idx + FRAME_LEN]

                parsed = parse_frame(frame)
                write_smartmeter(parsed)
                print(parsed)

if __name__ == "__main__":
    run_sniffer()
