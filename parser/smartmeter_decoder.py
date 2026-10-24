# modbus/parser/smartmeter_decoder.py

import struct
from datetime import datetime

def parse_smartmeter_frame(frame_hex):
    frame_hex = frame_hex.replace(" ", "").lower()
    frame = bytes.fromhex(frame_hex)

    decoded = {
        "timestamp": datetime.now().isoformat(),
        "device_id": "growatt_smartmeter",
        "raw": frame_hex
    }

    # Modbus RTU: [slave][func][...]
    slave = frame[0]
    func = frame[1]

    # ---------------------------------------------------------
    # FC=06 → Write Single Register → KEINE Messdaten
    # ---------------------------------------------------------
    if func == 6:
        decoded["type"] = "smartmeter_write"
        return decoded

    # ---------------------------------------------------------
    # FC=04 → Read Input Registers → Messdaten
    # ---------------------------------------------------------
    if func == 4:
        bytecount = frame[2]
        data = frame[3:3+bytecount]

        registers = []
        for i in range(0, len(data), 2):
            # Schutz: nur dekodieren, wenn 2 Bytes vorhanden
            if len(data[i:i+2]) < 2:
                break
            reg = struct.unpack(">H", data[i:i+2])[0]
            registers.append(reg)

        decoded["registers"] = registers

        # Schutz: nur dekodieren, wenn genug Register vorhanden
        if len(registers) >= 38:
            decoded.update({
                "voltage_l1_v": registers[0] / 10.0,
                "voltage_l2_v": registers[1] / 10.0,
                "voltage_l3_v": registers[2] / 10.0,

                "current_l1_a": registers[3] / 100.0,
                "current_l2_a": registers[4] / 100.0,
                "current_l3_a": registers[5] / 100.0,

                "power_total_w": registers[26],
                "import_energy_kwh": registers[36] / 100.0,
                "export_energy_kwh": registers[37] / 100.0
            })

        decoded["type"] = "smartmeter_read"
        return decoded

    # ---------------------------------------------------------
    # Unbekannte Funktion
    # ---------------------------------------------------------
    decoded["type"] = "smartmeter_unknown"
    return decoded
