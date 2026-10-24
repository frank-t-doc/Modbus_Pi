from datetime import datetime
from .inverter_decoder import parse_inverter_frame
from .smartmeter_decoder import parse_smartmeter_frame
from .bms_can_decoder import parse_bms_can_frame
from .bms_rs485_decoder import parse_bms_rs485_frame
from .shinebus_decoder import is_shinebus_frame, parse_shinebus_frame
from .influx_writer import write_shinebus_raw, write_shinebus_decoded

#
def route_frame(frame_hex):
    frame_hex = frame_hex.strip()

    # CAN-Frame?
    if ":" in frame_hex:
        decoded = parse_bms_can_frame(frame_hex)

    # ShineBus-Frame?
    elif is_shinebus_frame(frame_hex):
        decoded = parse_shinebus_frame(frame_hex)

        # ⭐ Jetzt in InfluxDB schreiben
        write_shinebus_raw(decoded)
        write_shinebus_decoded(decoded)

    # Modbus-Frame → anhand der Slave-ID
    else:
        slave_id = frame_hex.split()[0]

        if slave_id == "11":
            decoded = parse_inverter_frame(frame_hex)
        elif slave_id == "01":
            decoded = parse_smartmeter_frame(frame_hex)
        elif slave_id == "03":
            decoded = parse_bms_rs485_frame(frame_hex)
        else:
            decoded = {"device_id": "unknown", "raw": frame_hex}

    decoded["timestamp"] = datetime.now().isoformat()
    return decoded
