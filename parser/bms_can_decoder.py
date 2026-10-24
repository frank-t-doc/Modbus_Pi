import struct
from datetime import datetime

def parse_bms_can_frame(frame_hex):
    can_id_hex, data_hex = frame_hex.split(":")
    can_id = int(can_id_hex, 16)
    frame = bytes.fromhex(data_hex)

    decoded = {
        "timestamp": datetime.now().isoformat(),
        "device_id": "growatt_bms",
        "can_id": can_id
    }

    # Zellspannungen
    if can_id in [0x355, 0x356, 0x357, 0x358]:
        decoded["type"] = "cell_voltage"
        decoded["cells"] = []

        for i in range(0, len(frame), 2):
            raw = struct.unpack(">H", frame[i:i+2])[0]
            decoded["cells"].append(raw / 1000.0)

    # Temperaturen
    if can_id == 0x35A:
        decoded["type"] = "cell_temperature"
        decoded["temps"] = list(frame)

    return decoded
