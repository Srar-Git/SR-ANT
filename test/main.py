import random

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get("INFLUXDB_TOKEN")
org = "srv6-ant"
url = "http://localhost:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket = "srv6-ant"

write_api = write_client.write_api(write_options=SYNCHRONOUS)

while True:
    value = random.randint(5, 10)
    value_cpu = random.randint(10, 15)
    value_ram = random.randint(10000, 11000)
    value2 = random.uniform(0, 1) #packet
    valueq = random.randint(65, 200) #queue depth kb
    point = (
        Point("measurement1")
        .tag("tagname1", "tagvalue1")
        .field("field1", value)
    )
    point2 = (
        Point("measurement_packet")
        .tag("tagname1", "tagvalue1")
        .field("field1", value2)
    )
    point3 = (
        Point("measurement_cpu")
        .tag("tagname1", "tagvalue1")
        .field("field1", value_cpu)
    )
    point4 = (
        Point("measurement_ram")
        .tag("tagname1", "tagvalue1")
        .field("field1", value_ram)
    )
    point5 = (
        Point("measurement_q")
        .tag("tagname1", "tagvalue1")
        .field("field1", valueq)
    )
    write_api.write(bucket=bucket, org="srv6-ant", record=point)
    write_api.write(bucket=bucket, org="srv6-ant", record=point2)
    write_api.write(bucket=bucket, org="srv6-ant", record=point3)
    write_api.write(bucket=bucket, org="srv6-ant", record=point4)
    write_api.write(bucket=bucket, org="srv6-ant", record=point5)
    time.sleep(1)  # separate points by 1 second
# query_api = write_client.query_api()
#
# query = """from(bucket: "srv6-ant")
#  |> range(start: -10m)
#  |> filter(fn: (r) => r._measurement == "measurement1")"""
# tables = query_api.query(query, org="srv6-ant")
#
# for table in tables:
#   for record in table.records:
#     print(record)