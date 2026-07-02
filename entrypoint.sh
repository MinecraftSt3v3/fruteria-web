#!/bin/sh
mkdir -p /home
python manage.py migrate --no-input

python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
import os
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
if password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username!r} created.')
else:
    print(f'Superuser {username!r} already exists or no password set, skipping.')
"

exec gunicorn fruteria_eli.wsgi:application --bind 0.0.0.0:8000
