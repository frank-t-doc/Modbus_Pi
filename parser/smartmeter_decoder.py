# modbus/parser/smartmeter_decoder.py

import struct
from datetime import datetime


def decode_float(b):
    return struct.unpack(">f", b)[0]


def parse_dtsu666_power(frame, decoded):
    """
    DTSU666:
    2012H Pt Gesamte Wirkleistung
    2014H Pa Phase A
    2016H Pb Phase B
    2018H Pc Phase C
    """

    bytecount = frame[2]

    if bytecount != 16:
        decoded["type"] = "dtsu666_unknown_fc03"
        return decoded

    data = frame[3:19]

    pt = decode_float(data[0:4]) * 0.1
    pa = decode_float(data[4:8]) * 0.1
    pb = decode_float(data[8:12]) * 0.1
    pc = decode_float(data[12:16]) * 0.1

    decoded.update({
        "type": "dtsu666_power",
        "power_total_w": round(pt, 1),
        "power_l1_w": round(pa, 1),
        "power_l2_w": round(pb, 1),
        "power_l3_w": round(pc, 1),
        "phase_sum_w": round(pa + pb + pc, 1)
    })

    return decoded


def parse_smartmeter_frame(frame_hex):

    frame_hex = frame_hex.replace(" ", "").lower()

    frame = bytes.fromhex(frame_hex)

    decoded = {
        "timestamp": datetime.now().isoformat(),
        "device_id": "growatt_smartmeter",
        "raw": frame_hex
    }

    if len(frame) < 3:
        decoded["type"] = "invalid"
        return decoded

    slave = frame[0]
    func = frame[1]

    decoded["slave"] = slave
    decoded["function"] = func

    # ---------------------------------------------------------
    # FC=06 Write Register
    # ---------------------------------------------------------

    if func == 6:

        decoded["type"] = "smartmeter_write"
        return decoded

    # ---------------------------------------------------------
    # FC=03 DTSU666 Holding Register
    # ---------------------------------------------------------

    if func == 3:

        return parse_dtsu666_power(
            frame,
            decoded
        )

    # ---------------------------------------------------------
    # FC=04 Input Register
    # ---------------------------------------------------------

    if func == 4:

        bytecount = frame[2]

        data = frame[3:3 + bytecount]

        registers = []

        for i in range(0, len(data), 2):

            if len(data[i:i + 2]) < 2:
                break

            reg = struct.unpack(
                ">H",
                data[i:i + 2]
            )[0]

            registers.append(reg)

        decoded["registers"] = registers

        if len(registers) >= 38:

            decoded.update({

                "voltage_l1_v":
                    registers[0] / 10.0,

                "voltage_l2_v":
                    registers[1] / 10.0,

                "voltage_l3_v":
                    registers[2] / 10.0,

                "current_l1_a":
                    registers[3] / 100.0,

                "current_l2_a":
                    registers[4] / 100.0,

                "current_l3_a":
                    registers[5] / 100.0,

                "power_total_w":
                    registers[26],

                "import_energy_kwh":
                    registers[36] / 100.0,

                "export_energy_kwh":
                    registers[37] / 100.0
            })

        decoded["type"] = "smartmeter_read"

        return decoded

    decoded["type"] = "smartmeter_unknown"

    return decoded


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

def test_dtsu666():

    frame = (
        "04031045d9f80044550000456f4000450f70008f6f"
    )

    result = parse_smartmeter_frame(frame)

    print("\n=== DTSU666 TEST ===")
    print(result)

    assert abs(result["power_total_w"] - 697.5) < 0.5
    assert abs(result["power_l1_w"] - 85.2) < 0.5
    assert abs(result["power_l2_w"] - 382.8) < 0.5
    assert abs(result["power_l3_w"] - 229.9) < 0.5

    print("TEST OK")


if __name__ == "__main__":
    test_dtsu666()