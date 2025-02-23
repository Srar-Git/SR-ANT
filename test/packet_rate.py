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
    value = random.uniform(0, 2)
    point = (
        Point("measurement_packet")
        .tag("tagname1", "tagvalue1")
        .field("field1", value)
    )
    write_api.write(bucket=bucket, org="srv6-ant", record=point)
    time.sleep(1)  # separate points by 1 second
query_api = write_client.query_api()

query = """from(bucket: "srv6-ant")
 |> range(start: -10m)
 |> filter(fn: (r) => r._measurement == "measurement1")"""
tables = query_api.query(query, org="srv6-ant")

for table in tables:
  for record in table.records:
    print(record)