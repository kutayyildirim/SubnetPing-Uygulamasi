#!/bin/sh

echo "Veritabanı bekleniyor..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Veritabanı hazır!"

python manage.py migrate --noinput

if [ "$RUN_MODE" = "web" ]; then
    echo "Django başlatılıyor..."
    python manage.py runserver 0.0.0.0:8000
elif [ "$RUN_MODE" = "celery" ]; then
    echo "Celery başlatılıyor..."
    celery -A pingmonitor worker -l info
else
    echo "Bilinmeyen RUN_MODE: $RUN_MODE"
    exec "$@"
fi
