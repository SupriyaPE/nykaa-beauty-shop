#!/bin/sh
echo "🚀 Starting server..."

python manage.py migrate --noinput || echo "⚠️ migrate skipped"
python manage.py collectstatic --noinput || echo "⚠️ collectstatic skipped"

exec "$@"