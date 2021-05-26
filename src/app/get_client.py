import requests
from datetime import datetime
import pytz

BASE = "http://127.0.0.1:5000/"

utc_str = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')).isoformat('T')

print(utc_str)
response = requests.get(BASE + "transactions")

print(response.json())
