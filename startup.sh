#!/bin/bash
# VintedScanner Web - Container Startup Script
#
# This script runs when the Docker container starts. It's like a checklist
# that ensures everything is ready before the application starts.
#
# What it does (in order):
# 1. Wait for database connection (if using PostgreSQL)
# 2. Run database migrations (create/update tables)
# 3. Seed popular brands into database (Nike, Adidas, etc.)
# 4. Start the FastAPI web server
#
# The 'set -e' below means "stop immediately if any command fails"
# This prevents the app from starting if setup steps fail.

set -e

echo "=================================="
echo "VintedScanner Web - Starting"
echo "=================================="

# Wait for database (if using PostgreSQL)
if [[ $DATABASE_URL == postgresql* ]]; then
    echo "Waiting for PostgreSQL..."
    until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_USER" -c '\q' 2>/dev/null; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    echo "PostgreSQL is up!"
fi

# Run database migrations
echo "Running database migrations..."
cd /app/backend
alembic upgrade head

# Seed popular brands (if enabled)
if [ "$SEED_POPULAR_BRANDS_ON_STARTUP" = "true" ]; then
    echo "Seeding popular brands..."
    python -c "
from backend.database import SessionLocal
from backend.seeds.popular_brands import seed_brands

# Seed for multiple countries
countries = ['fr', 'ie', 'de', 'uk', 'es', 'it']
db = SessionLocal()
try:
    for country in countries:
        try:
            count = seed_brands(db, country)
            print(f'Seeded {count} brands for {country}')
        except Exception as e:
            print(f'Failed to seed {country}: {e}')
finally:
    db.close()
" || echo "Brand seeding skipped (models may not exist yet)"
fi

# Start the application
echo "Starting FastAPI application..."
cd /app
exec uvicorn backend.main:app --host 0.0.0.0 --port 3000 --workers 2
