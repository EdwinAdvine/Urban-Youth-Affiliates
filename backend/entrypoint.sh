#!/bin/sh

echo "==> Checking environment..."
echo "DATABASE_URL is set: $([ -n "$DATABASE_URL" ] && echo 'yes' || echo 'NO - MISSING!')"
echo "REDIS_URL is set: $([ -n "$REDIS_URL" ] && echo 'yes' || echo 'NO - MISSING!')"
echo "SECRET_KEY length: ${#SECRET_KEY}"

# Validate SECRET_KEY length (must be at least 32 characters)
if [ -z "${SECRET_KEY}" ] || [ ${#SECRET_KEY} -lt 32 ]; then
    echo "ERROR: SECRET_KEY must be at least 32 characters long."
    echo "Current value length: ${#SECRET_KEY}"
    echo "Please set SECRET_KEY to a secure random string of 32+ characters."
    echo "You can generate one with: openssl rand -hex 32"
    exit 1
fi

echo "==> Running database migrations..."
if ! alembic upgrade head; then
    echo "ERROR: Database migration failed!"
    echo "Check that DATABASE_URL is correct and the database is reachable."
    exit 1
fi

echo "==> Seeding initial data..."
if ! python -m app.seed; then
    echo "WARNING: Seeding failed (continuing anyway — may already be seeded)."
fi

echo "==> Starting server on 0.0.0.0:8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
