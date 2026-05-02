#!/bin/sh

/app/.venv/bin/python manage.py collectstatic --noinput
/app/.venv/bin/python manage.py migrate
/app/.venv/bin/daphne -b 0.0.0.0 -p 8000 core.asgi:application