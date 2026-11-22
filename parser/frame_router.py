from datetime import datetime
from .inverter_decoder import parse_inverter_frame
from .smartmeter_decoder import parse_smartmeter_frame
from .bms_can_decoder import parse_bms_can_frame
from .bms_rs485_decoder import parse_bms_rs485_frame
from .shinebus_decoder import is_shinebus_frame, parse_shinebus_frame
from .wr_modbus_decoder import is_wr_modbus_frame, parse_wr_modbus_frame
from .influx_writer import (
    write_shinebus_raw,
    write_shinebus_decoded,
    write_smartmeter_decoded,
    write_wr_modbus_decoded
)


def route_frame(frame_hex):
    frame_hex = frame_hex.strip().replace(" ", "").lower()

    # 1️⃣ CAN-Frame?
    if ":" in frame_hex:
        decoded = parse_bms_can_frame(frame_hex)

    elif frame_hex[:2] == "04":
        decoded = parse_smartmeter_frame(frame_hex)
        write_smartmeter_decoded(decoded)

    # 2️⃣ ShineBus-Frame?
    elif is_shinebus_frame(frame_hex):
        decoded = parse_shinebus_frame(frame_hex)
        write_shinebus_raw(decoded)
        write_shinebus_decoded(decoded)

    # 3️⃣ WR-Modbus-Frame?
    elif is_wr_modbus_frame(frame_hex):
        decoded = parse_wr_modbus_frame(frame_hex)
        write_wr_modbus_decoded(decoded)

    else:
        # 4️⃣ Modbus Slave-ID Routing
        slave_id = frame_hex[:2]

        # WR-Inverter (alter Decoder)
        if slave_id == "11":
            decoded = parse_inverter_frame(frame_hex)

        # Smartmeter
        elif slave_id == "01":
            decoded = parse_smartmeter_frame(frame_hex)
            write_smartmeter_decoded(decoded)

        # BMS RS485
        elif slave_id == "03":
            decoded = parse_bms_rs485_frame(frame_hex)

        else:
            decoded = {"device_id": "unknown", "raw": frame_hex}

    decoded["timestamp"] = datetime.now().isoformat()
    return decoded
