#!/bin/sh
set -e

echo "=========================================================="
echo "Starting HealthLink Django Application"
echo "=========================================================="
echo ""

echo "Step 1: Running Database Migrations..."
echo "=========================================================="
python manage.py migrate --noinput
echo "=========================================================="
echo "Migrations completed successfully!"
echo ""

echo "Step 2: Starting Gunicorn Server..."
echo "=========================================================="
echo ""

exec gunicorn \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class sync \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  healthlink.wsgi:application
