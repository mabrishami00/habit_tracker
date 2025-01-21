set -e
set -x

if [ "$1" = "web" ]; then
    python3 manage.py migrate --noinput
    python3 manage.py collectstatic --noinput
fi
exec "$@"
