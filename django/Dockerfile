FROM python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app/

RUN apt-get update && \
    apt-get install -y \
        default-libmysqlclient-dev \
        build-essential \
        cron vim logrotate \
        libpcre2-dev \
        default-mysql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Cleanup to reduce image size
RUN apt-get purge -y --auto-remove build-essential
