from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = "http://192.168.10.223:8086"
INFLUX_TOKEN = "yZebaGFUz2Q9PvSLjXh1Fsy66vQx5j9D4QiQRIwl4-7mQZSRDgiJRk7bdN0_YtQMacJTK2JXLy5ns-IUI6q3rA=="
INFLUX_ORG = "TuttliesHomeBase"
INFLUX_BUCKET = "smartmeter"

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)

def write_smartmeter(values):
    """
    values = {
        "energy_Wh": ...,
        "power_L1_W": ...,
        "power_L2_W": ...,
        "power_L3_W": ...,
        "total_power_W": ...,
        "footer": "c71d"
    }
    """

    point = (
        Point("shine_dtsu666")
        .tag("device", "smartmeter")
        .time(datetime.utcnow())
        .field("energy_Wh", float(values["energy_Wh"]))
        .field("power_L1_W", float(values["power_L1_W"]))
        .field("power_L2_W", float(values["power_L2_W"]))
        .field("power_L3_W", float(values["power_L3_W"]))
        .field("total_power_W", float(values["total_power_W"]))
        .field("footer_hex", values["footer"])
    )

    write_api.write(bucket=INFLUX_BUCKET, record=point)
