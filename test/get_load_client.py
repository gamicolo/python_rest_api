#!/usr/bin/python3

from locust import HttpUser, between, task

BASE = "http://127.0.0.1:5000/"

class MyWebSiteUser(HttpUser):

    wait_time = between(5, 15)

    @task
    def load_main(self):

        self.client.get(BASE + "transactions")
