#!/bin/sh
set -e

# Validate SECRET_KEY length (must be at least 32 characters)
if [ -z "${SECRET_KEY}" ] || [ ${#SECRET_KEY} -lt 32 ]; then
    echo "ERROR: SECRET_KEY must be at least 32 characters long."
    echo "Current value length: ${#SECRET_KEY}"
    echo "Please set SECRET_KEY to a secure random string of 32+ characters."
    echo "You can generate one with: openssl rand -hex 32"
    exit 1
fi

echo "==> Running database migrations..."
alembic upgrade head

echo "==> Seeding initial data..."
python -m app.seed

echo "==> Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
