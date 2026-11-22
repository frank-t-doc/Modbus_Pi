# modbus/parser/influx_writer.py

from datetime import datetime

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


# ---------------------------------------------------------
# InfluxDB Einstellungen
# ---------------------------------------------------------

INFLUX_URL = "http://192.168.10.223:8086"
INFLUX_TOKEN = ""
INFLUX_ORG = "TuttliesHomeBase"
INFLUX_BUCKET = "growatt"


client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)


# ---------------------------------------------------------
# RAW ShineBus Frames (alle raw_reg_xx)
# ---------------------------------------------------------

def write_shinebus_raw(decoded):

    point = (
        Point("shinebus_raw")
        .tag("device_id", decoded.get("device_id", "unknown"))
        .tag("header", str(decoded.get("header", 0)))
        .tag("function", str(decoded.get("function", 0)))
        .time(datetime.utcnow())
    )

    for key, value in decoded.items():
        if key.startswith("raw_reg_"):
            point = point.field(key, float(value))

    write_api.write(
        bucket=INFLUX_BUCKET,
        record=point
    )


# ---------------------------------------------------------
# DECODED ShineBus Frames
# ---------------------------------------------------------

def write_shinebus_decoded(decoded):

    point = (
        Point("shinebus_decoded")
        .tag("device_id", decoded.get("device_id", "unknown"))
        .tag("header", str(decoded.get("header", 0)))
        .time(datetime.utcnow())
    )

    for key in [
        "pv_temperature_c",
        "pv_temperature2_c",
        "pv_ipm_temperature_c",

        "pv1_voltage_v",
        "pv2_voltage_v",

        "pv_power_w",
        "grid_power_w",
        "battery_power_w",

        "pv1_current_a",
        "pv2_current_a",

        "status_bits",
        "status_byte",
        "mode_code",

        "pv_power_raw",
        "grid_power_raw",
        "battery_power_raw"
    ]:

        if key in decoded:
            point = point.field(
                key,
                float(decoded[key])
            )

    write_api.write(
        bucket=INFLUX_BUCKET,
        record=point
    )


# ---------------------------------------------------------
# SMARTMETER Frames (DTSU666)
# ---------------------------------------------------------

def write_smartmeter_decoded(decoded):
    """
    Schreibt Smartmeter-Daten in InfluxDB.
    Measurement: smartmeter_decoded
    """

    point = (
        Point("smartmeter_decoded")
        .tag(
            "device_id",
            decoded.get("device_id", "growatt_smartmeter")
        )
        .tag(
            "type",
            decoded.get("type", "unknown")
        )
        .tag(
            "request_name",
            decoded.get("request_name", "unknown")
        )
        .tag(
            "request_register",
            decoded.get("request_register", "unknown")
        )
        .tag(
            "crc",
            decoded.get("crc", "")
        )
        .time(datetime.utcnow())
    )

    for key, value in decoded.items():

        # Metadaten überspringen
        if key in [
            "device_id",
            "type",
            "request_name",
            "request_register",
            "crc",
            "raw",
            "registers",
            "timestamp"
        ]:
            continue

        # Nur numerische Werte schreiben
        if isinstance(value, (int, float)):
            point = point.field(key, value)

    try:

        write_api.write(
            bucket=INFLUX_BUCKET,
            record=point
        )

        print(
            "Influx OK:",
            decoded.get("power_total_w", "n/a")
        )

    except Exception as e:

        print(
            "Influx ERROR:",
            e
        )


# ---------------------------------------------------------
# WR-Modbus Frames (WR1 / WR2 getrennt)
# ---------------------------------------------------------

def write_wr_modbus_decoded(decoded):
    """
    Schreibt WR-Modbus-Daten getrennt nach WR-ID.
    Measurement: wr_decoded
    """

    wr_id = decoded.get("wr_id")

    if wr_id is None:
        return

    point = (
        Point("wr_decoded")
        .tag("wr_id", str(wr_id))
        .time(datetime.utcnow())
    )

    for key in [
        "pv_power_w",
        "grid_power_w",
        "battery_power_w",

        "pv1_voltage_v",
        "pv2_voltage_v",

        "pv1_current_a",
        "pv2_current_a",

        "temperature_internal_c",
        "temperature_ipm_c",

        "status_bits",
        "status_byte",
        "mode_code"
    ]:

        if key in decoded:
            try:
                point = point.field(
                    key,
                    float(decoded[key])
                )
            except Exception:
                pass

    write_api.write(
        bucket=INFLUX_BUCKET,
        record=point
    )