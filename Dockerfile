FROM python:3.10-slim

EXPOSE 8081
RUN apt-get update && apt-get upgrade -y && \
     apt-get install -y sqlite3
WORKDIR /app

COPY requirements.txt ./
COPY static ./static/
RUN pip install -r requirements.txt

COPY chatbot ./chatbot/
COPY db ./db/
COPY dynamic ./dynamic/

CMD (export PYTHONPATH=$(pwd) ; python chatbot/main.py)
