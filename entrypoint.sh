#!/bin/sh

python manage.py db init
python manage.py db migrate
python manage.py db upgrade

if [ "$FLASK_ENV" = "development" ]; then
    echo "starting gunicorn for development"
    gunicorn --bind 0.0.0.0:5090 --reload app:app
else
    echo "starting gunicorn"
    gunicorn --bind 0.0.0.0:5090 app:app
fi