FROM python:3.12

WORKDIR /app

COPY requirements.txt ./

RUN python3 -m pip install -r requirements.txt

COPY ./app ./

CMD ["python3", "server.py", "0.0.0.0", "1337"]