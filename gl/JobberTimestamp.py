
import datetime

timestamp_ns = 1741004694984801569
timestamp_s = timestamp_ns / 1e9  # Convert nanoseconds to seconds

dt_object = datetime.datetime.fromtimestamp(timestamp_s)

print(dt_object)

