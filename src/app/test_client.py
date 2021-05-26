import requests
from datetime import datetime
import pytz

BASE = "http://127.0.0.1:5000/"

utc_str = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')).isoformat('T')

print(utc_str)
#response = requests.post(BASE + "transactions", {'amount': '1', 'timestamp': '2018-07-17T09:59:51.312Z'})
response = requests.post(BASE + "transactions", {'amount': '1', 'timestamp': utc_str})
#response = requests.post(BASE + "transactions", {'amount': '1'})
#response = requests.post(BASE + "transactions", {'timestamp': '2018-07-17T09:59:51.312Z'})
