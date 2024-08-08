FROM python:3.10-slim

EXPOSE 8081
RUN apt-get update && apt-get upgrade -y
WORKDIR /app

COPY requirements.txt texts.json ./
RUN pip install -r requirements.txt

COPY chatbot ./chatbot/

CMD (export PYTHONPATH=$(pwd) ; python chatbot/main.py)
