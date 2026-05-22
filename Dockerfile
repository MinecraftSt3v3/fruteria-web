FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN SECRET_KEY=temp-build-key python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "fruteria_eli.wsgi:application", "--bind", "0.0.0.0:8000"]
