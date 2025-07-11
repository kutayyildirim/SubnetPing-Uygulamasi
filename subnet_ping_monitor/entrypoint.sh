#!/bin/sh

echo "Veritabanı bekleniyor..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Veritabanı hazır!"

python manage.py migrate

python manage.py runserver 0.0.0.0:8000
