#!/bin/sh
set -e

# Trava contra banco vazio por engano: se o arquivo do banco não existe
# (volume montado errado, esqueceu de mover o db.sqlite3 para data/), o
# migrate criaria um banco novo e o sistema subiria sem nenhum dado.
# Banco novo de propósito: ALLOW_NEW_DB=1.
DB_PATH="${DJANGO_DB_NAME:-/app/db.sqlite3}"
if [ ! -f "$DB_PATH" ] && [ "${ALLOW_NEW_DB:-0}" != "1" ]; then
    echo "ERRO: banco não encontrado em $DB_PATH." >&2
    echo "Mova o db.sqlite3 para lá ou suba com ALLOW_NEW_DB=1 para criar um banco vazio." >&2
    exit 1
fi

python manage.py collectstatic --noinput
python manage.py migrate
exec daphne -b 0.0.0.0 -p 8000 core.asgi:application
