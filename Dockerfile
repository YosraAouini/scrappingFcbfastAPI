# syntax=docker/dockerfile:1

From python:3.9.2
WORKDIR /fastapi-app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./app ./app


CMD ["python","./app/debug_server.py"]