# modbus/parser/bms_rs485_decoder.py

from datetime import datetime

def parse_bms_rs485_frame(frame_hex):
    """
    Minimaler RS485-BMS-Frame-Parser.
    Du kannst später echte Register hinzufügen.
    """

    frame_hex = frame_hex.replace(" ", "").lower()

    decoded = {
        "timestamp": datetime.now().isoformat(),
        "device_id": "growatt_bms_rs485",
        "raw": frame_hex,
        "length_bytes": len(frame_hex) // 2
    }

    # Beispiel: RS485 BMS liefert 03 xx xx xx xx
    # Hier kannst du später echte Register dekodieren

    return decoded
