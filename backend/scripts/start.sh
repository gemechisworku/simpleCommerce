#!/bin/sh
set -e
cd /app
# Run migrations (uses DATABASE_URL from env)
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
