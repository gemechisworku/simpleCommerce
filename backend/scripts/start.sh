#!/bin/sh
set -e
cd /app
# Run migrations (uses DATABASE_URL from env)
alembic upgrade head
# Optional: run seed at startup (set RUN_SEED_ON_STARTUP=1 in Railway Variables, then deploy once)
if [ -n "$RUN_SEED_ON_STARTUP" ] && [ "$RUN_SEED_ON_STARTUP" != "0" ]; then
  python -m scripts.seed_mock_data || true
fi
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
