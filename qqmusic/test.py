#!/usr/bin/python3
from instead_lib import wait_next
import time

start = "2022-11-12 20:14:40"
last_record_timearray = time.strptime(start, "%Y-%m-%d %H:%M:%S")
print(last_record_timearray)
start_timestamp = int(time.mktime(last_record_timearray))

while True:    
    print(start_timestamp)
    wait_next(start_timestamp, 58)
    start_timestamp += 58