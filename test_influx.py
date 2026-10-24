from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

client = InfluxDBClient(
    url="http://192.168.10.223:8086",
    token="yZebaGFUz2Q9PvSLjXh1Fsy66vQx5j9D4QiQRIwl4-7mQZSRDgiJRk7bdN0_YtQMacJTK2JXLy5ns-IUI6q3rA==",
    org="TuttliesHomeBase"
)

write_api = client.write_api(write_options=SYNCHRONOUS)

point = Point("shinebus_test").field("testvalue", 42)
write_api.write(bucket="growatt", record=point)

print("Test geschrieben!")
