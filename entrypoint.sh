#!/bin/bash

set -e
set -x



echo "Waiting for postgres..."

until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT; do
    sleep 2
done

echo "PostgreSQL started"

if [ "$1" = "primary" ]; then
    python3 manage.py migrate --noinput
    python3 manage.py collectstatic --noinput
fi
shift
exec "$@"
