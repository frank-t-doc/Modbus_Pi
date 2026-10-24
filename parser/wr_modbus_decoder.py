from datetime import datetime

def is_wr_modbus_frame(frame_hex: str) -> bool:
    frame_hex = frame_hex.replace(" ", "").lower()
    try:
        slave_id = int(frame_hex[0:2], 16)
        function = int(frame_hex[2:4], 16)
        return slave_id in range(1, 10) and function == 3
    except:
        return False


def parse_wr_modbus_frame(frame_hex: str) -> dict:
    frame_hex = frame_hex.replace(" ", "").lower()

    slave_id = int(frame_hex[0:2], 16)
    function = int(frame_hex[2:4], 16)
    start_reg = int(frame_hex[4:8], 16)
    reg_count = int(frame_hex[8:12], 16)

    payload_hex = frame_hex[12:]

    regs = []
    for i in range(0, reg_count * 4, 4):
        regs.append(int(payload_hex[i:i+4], 16))

    decoded = {
        "timestamp": datetime.now().isoformat(),
        "device_id": f"growatt_wr_{slave_id}",
        "wr_id": slave_id,
        "type": "wr_modbus_frame",
        "raw": frame_hex,
        "function": function,
        "start_register": start_reg,
        "register_count": reg_count,
    }

    decoded["payload"] = payload_hex

    return decoded

    for idx, val in enumerate(regs):
        decoded[f"raw_reg_{idx:02d}"] = val

    # --- SPH TL3 BH Mapping ---
    decoded["pv_power_w"] = regs[0]
    decoded["grid_power_w"] = regs[1]
    decoded["battery_power_w"] = regs[2]

    decoded["pv1_voltage_v"] = regs[2] / 10.0
    decoded["pv2_voltage_v"] = regs[3] / 10.0

    decoded["pv1_current_a"] = regs[4] / 10.0
    decoded["pv2_current_a"] = regs[5] / 10.0

    decoded["temperature_internal_c"] = regs[6] / 10.0
    decoded["temperature_ipm_c"] = regs[7] / 10.0

    decoded["status_bits"] = regs[8]
    decoded["status_byte"] = regs[9]
    decoded["mode_code"] = regs[10]

    return decoded
