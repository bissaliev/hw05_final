#!/usr/bin/env bash

# Ожидаем доступности базы данных
/app/wait-for-it.sh db:5432 --timeout=30 --strict -- echo "Postgres is up - executing command"

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py loaddata fixtures/users
python manage.py loaddata fixtures/groups
python manage.py loaddata fixtures/posts
exec gunicorn --bind 0:8000 yatube.wsgi