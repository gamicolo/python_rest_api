#!/usr/bin/python3

import requests
import time

BASE = "http://127.0.0.1:5000/"

start_time = time.time()
response = requests.get(BASE + "transactions")

print(len(response.json()))
print("%s seconds" % (time.time() - start_time))
