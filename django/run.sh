#!/bin/bash

sleep 15
#python manage.py make_config
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py process_tasks &
gunicorn labellabor.wsgi:application -b 0.0.0.0:8000 --reload
