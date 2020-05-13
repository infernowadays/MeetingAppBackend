FROM python:3.8.1-slim

WORKDIR /app

RUN apt update && \
    apt install -y --no-install-recommends \
        libpq-dev \
        build-essential

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt remove -y   \
        build-essential \
        libpq-dev && \
    apt-get autoremove -y

COPY . .

CMD gunicorn MeetingApp.wsgi:application
