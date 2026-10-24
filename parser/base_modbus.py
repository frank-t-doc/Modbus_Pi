# modbus/parser/base_modbus.py

def parse_modbus_frame(frame_hex, device_id="modbus_device"):
    """
    Minimaler generischer Modbus-Frame-Parser.
    device_id ist optional und wird von den Decodern gesetzt.
    """

    frame_hex = frame_hex.replace(" ", "").lower()

    return {
        "device_id": device_id,
        "raw": frame_hex,
        "length_bytes": len(frame_hex) // 2,
        "type": "modbus_frame"
    }
