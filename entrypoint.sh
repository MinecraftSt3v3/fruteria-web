#!/bin/sh
python manage.py migrate --no-input
exec gunicorn fruteria_eli.wsgi:application --bind 0.0.0.0:8000
