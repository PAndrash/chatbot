FROM python:3.10-slim

EXPOSE 8081
RUN apt-get update && apt-get upgrade -y && \
     apt-get install -y sqlite3 cron procps
WORKDIR /app

COPY requirements.txt ./
COPY static ./static/
RUN pip install -r requirements.txt

COPY chatbot ./chatbot/
COPY db ./db/
COPY dynamic ./dynamic/

COPY restart_script.sh ./
COPY cron /etc/cron.d/hello-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/hello-cron && \
    crontab /etc/cron.d/hello-cron && \
    touch /var/log/cron.log && \
    chmod +x restart_script.sh

# Run the command on container startup
CMD echo "TOKEN=${TOKEN}" > .env && echo "ADMIN_CHAT_ID=${ADMIN_CHAT_ID}" >> .env && export PYTHONPATH=$(pwd) && python chatbot/main.py >> /var/log/cron.log 2>&1 & cron && tail -f /var/log/cron.log
