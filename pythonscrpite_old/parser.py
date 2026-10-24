frame_counter = 0
from datetime import datetime
import struct

def parse_modbus_frame(frame_hex):
    global frame_counter

    decoded = {}  # <-- WICHTIG: decoded MUSS zuerst existieren

    frame_counter += 1
    decoded["frame_counter"] = frame_counter
    decoded["timestamp"] = datetime.now().isoformat()

    """
    Parse a Growatt Modbus RTU frame (hex string).
    Returns dict with decoded values.
    """

    # Remove whitespace
    frame_hex = frame_hex.replace(" ", "").lower()

    # Convert to bytes
    try:
        frame = bytes.fromhex(frame_hex)
    except ValueError:
        return None

    # Minimum length check
    if len(frame) < 5:
        return None

    slave_id = frame[0]
    function = frame[1]

    # Only parse Read Holding Register responses (0x03)
    if function != 0x03:
        return {
            "slave": slave_id,
            "function": function,
            "raw": frame_hex
        }

    byte_count = frame[2]
    data = frame[3:3+byte_count]

    # Ignore extremely long frames (device info frames)
    if byte_count > 200:
        return {
            "slave": slave_id,
            "function": function,
            "type": "device_info_frame",
            "raw": frame_hex
        }

    # Ignore frames with odd data length
    if len(data) % 2 != 0:
        return {
            "slave": slave_id,
            "function": function,
            "type": "invalid_or_device_info_frame",
            "raw": frame_hex
        }

    # Growatt uses 16‑bit registers, often combined into 32‑bit values
    registers = []
    for i in range(0, len(data), 2):
        reg = struct.unpack(">H", data[i:i+2])[0]
        registers.append(reg)

    # Now decode known Growatt registers
    decoded = {
        "slave": slave_id,
        "function": function,
        "raw": frame_hex,
        "registers": registers,
    }

    # Growatt register map (offsets relative to 0x2710)
    try:
        decoded.update({
            "pv_power": (registers[1] << 16 | registers[2]),      # 10000
            "grid_power": (registers[3] << 16 | registers[4]),    # 10002
            "energy_today": registers[23],                         # 10010
            "energy_total": registers[20],                         # 10012
            "energy_string": registers[13],
            "grid_voltage": registers[16] / 10.0,                 # 10020
            "grid_frequency": registers[17] / 100.0,              # 10022
        })
    except Exception:
        pass

    return decoded


if __name__ == "__main__":
    # Example frame from your sniffer
    test = "0103300001000186a00000b0fc03e800010000000000000000000000000000000100620002000000000000bb68000186a000008a5b"
    print(parse_modbus_frame(test))
