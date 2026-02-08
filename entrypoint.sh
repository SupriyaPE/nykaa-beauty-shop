#!/bin/sh

echo "⏳ Waiting for database..."

python << END
import time
import sys
import MySQLdb

host = "${DB_HOST}"
port = int("${DB_PORT}")

for i in range(30):
    try:
        db = MySQLdb.connect(host=host, port=port, user="${DB_USER}", passwd="${DB_PASSWORD}")
        db.close()
        print("✅ Database is ready")
        sys.exit(0)
    except Exception as e:
        print("DB not ready, retrying...")
        time.sleep(2)

print("❌ Could not connect to DB")
sys.exit(1)
END


echo "🚀 Running migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static..."
python manage.py collectstatic --noinput

echo "🎯 Starting server..."
exec "$@"