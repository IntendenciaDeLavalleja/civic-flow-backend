#!/bin/sh
# CivicFlow backend entrypoint

set -e

echo "Running database migrations..."
flask db upgrade

echo "Starting Gunicorn..."
exec gunicorn -c /app/gunicorn.conf.py "wsgi:app"
