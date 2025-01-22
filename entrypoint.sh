#!/bin/bash

set -e
set -x


if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$1" = "web" ]; then
    python3 manage.py migrate --noinput
    python3 manage.py collectstatic --noinput
fi
exec "$@"
