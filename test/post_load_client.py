#!/usr/bin/python3

from locust import HttpUser, between, task
import requests
from datetime import datetime
import pytz
import random

import time

BASE = "http://127.0.0.1:5000/"
class MyWebSiteUser(HttpUser):

    wait_time = between(5, 15)

    @task
    def load_main(self):

        utc_str = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')).isoformat('T')
        self.client.post(BASE + "transactions", {'amount': str(int(500*random.random())), 'timestamp': utc_str})

