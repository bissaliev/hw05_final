#!/bin/bash

# Ожидаем доступности базы данных
/app/wait-for-it.sh db:5432 --timeout=30 --strict -- echo "Postgres is up - executing command"

python manage.py migrate
sleep 2
python manage.py collectstatic --no-input
sleep 2
python manage.py loaddata fixtures/users
sleep 2
python manage.py loaddata fixtures/groups
sleep 2
python manage.py loaddata fixtures/posts
# sleep 2
exec gunicorn --bind 0:8000 yatube.wsgi