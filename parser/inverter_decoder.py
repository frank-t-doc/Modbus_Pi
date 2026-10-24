# modbus/inverter_decoder.py

from .base_modbus import parse_modbus_frame

def parse_inverter_frame(frame_hex):
    decoded = parse_modbus_frame(frame_hex, "growatt_inverter")

    regs = decoded.get("register_values", [])

    if len(regs) >= 10:
        decoded["pv1_voltage"] = regs[0] / 10.0
        decoded["pv1_current"] = regs[1] / 10.0
        decoded["pv2_voltage"] = regs[2] / 10.0
        decoded["pv2_current"] = regs[3] / 10.0

        decoded["ac_power"] = (regs[4] << 8) | regs[5]
        decoded["grid_freq"] = regs[6] / 100.0

    return decoded
