FROM python:3

WORKDIR /home/guille/development/python_rest_ap/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements

COPY . .

CMD ["python", "./main.py"]
