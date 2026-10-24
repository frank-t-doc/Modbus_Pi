# shinebus_decoder.py
from datetime import datetime

def is_shinebus_frame(frame_hex: str) -> bool:
    frame_hex = frame_hex.strip()
    # ShineBus: 40 Byte, beginnt mit 01 oder 02, Function 03
    try:
        # Erstes Byte = header, zweites = function
        header = int(frame_hex[0:2], 16)
        function = int(frame_hex[2:4], 16)
        return header in (1, 2) and function == 3 and len(frame_hex) == 80
    except Exception:
        return False


def parse_shinebus_frame(frame_hex: str) -> dict:
    frame_hex = frame_hex.strip()

    # 40 Byte → 80 Hex‑Zeichen
    # Wir zerlegen in 17 Register à 2 Byte (4 Hex‑Zeichen) nach dem Header/Function‑Teil
    header = int(frame_hex[0:2], 16)
    function = int(frame_hex[2:4], 16)

    # Rest als 16‑Bit‑Register
    regs = []
    # ab Position 4 (nach header+function)
    for i in range(4, 4 + 17 * 4, 4):
        regs.append(int(frame_hex[i:i+4], 16))

    decoded = {
        "device_id": "growatt_shinebus",
        "type": "shinebus_frame",
        "raw": frame_hex,
        "length_bytes": 40,
        "header": header,
        "function": function,
        "payload_length": 10000,   # Platzhalter
        "register_count": len(regs),
    }

    # Rohregister mitgeben
    for idx, val in enumerate(regs):
        decoded[f"raw_reg_{idx:02d}"] = val

    # ---- Mapping: header = 1 (BMS / PV‑Spannungen / Temperaturen) ----
    if header == 1:
        decoded["pv_temperature_c"] = regs[5] / 10.0
        decoded["pv_ipm_temperature_c"] = regs[8] / 100.0

        # echte Skalierung:
        decoded["pv1_voltage_v"] = (regs[3] / 68.0) * 127.4
        decoded["pv2_voltage_v"] = (regs[9] / 96.0) * 0.767

    # ---- Mapping: header = 2 (Inverter‑Broadcast) ----
    if header == 2:
        decoded["pv_temperature_c"] = regs[5] / 6.0
        decoded["pv_temperature2_c"] = regs[12] / 4.0

        # echte Skalierung:
        decoded["pv1_voltage_v"] = (regs[8] / 16.0) * 127.4
        decoded["pv2_voltage_v"] = (regs[9] / 5.4) * 0.767

        decoded["status_bits"] = regs[6]
        decoded["status_byte"] = regs[7]
        decoded["mode_code"] = regs[16]

        # Power korrekt skalieren:
        decoded["pv_power_w"] = regs[0] * 0.97157
        decoded["grid_power_w"] = regs[1] * 0.97157
        decoded["battery_power_w"] = regs[2] * 0.97157
        
        # PV-Strom berechnen (A)
        if decoded["pv1_voltage_v"] > 1:
            decoded["pv1_current_a"] = decoded["pv_power_w"] / decoded["pv1_voltage_v"]
        else:
            decoded["pv1_current_a"] = 0

        if decoded["pv2_voltage_v"] > 1:
            decoded["pv2_current_a"] = decoded["pv_power_w"] / decoded["pv2_voltage_v"]
        else:
            decoded["pv2_current_a"] = 0


    decoded["timestamp"] = datetime.now().isoformat()
    return decoded
