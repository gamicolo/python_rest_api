# python_rest_api
prerequisite

- docker and docker-compose installed

to run the container

1. docker-compose up (only the first time)
2. docker-compose build
3. docker-compose run --service-ports real-time-statistics

the container is listening in all IP's in the port 5000

to load testing

1. docker-compose run --service-ports real-time-statistics
2. locust -f [post_load_client.py|get_load_client.py] --host=http://0.0.0.0:5000
3. on a web browser go to the URL http://localhost:8089/
4. set up the number of total users and spawn rate (users spawned/second)
