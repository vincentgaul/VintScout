#!/bin/bash
set -e

echo "========================================="
echo "VintScout Startup"
echo "========================================="

# Paths
DB_PATH="/app/backend/data/vinted.db"
TEMPLATE_PATH="/app/backend/data/vinted.db.template"

# Initialize database from template if it doesn't exist
if [ ! -f "$DB_PATH" ]; then
    echo "First run detected - initializing database from template..."

    if [ ! -f "$TEMPLATE_PATH" ]; then
        echo "ERROR: Template database not found at $TEMPLATE_PATH"
        exit 1
    fi

    cp "$TEMPLATE_PATH" "$DB_PATH"
    echo "✓ Database initialized from template"
else
    echo "✓ Using existing database"
fi

# Run database migrations
echo ""
echo "Running database migrations..."
cd /app/backend
alembic upgrade head
echo "✓ Migrations complete"

# Create default admin user if no users exist
echo ""
echo "Checking for users..."
python3 << 'PYEOF'
import sys
import os
import uuid

# Add parent directory to path
sys.path.insert(0, '/app')

from backend.database import SessionLocal
from backend.models import User
from backend.api.routes.auth import hash_password

db = SessionLocal()

try:
    user_count = db.query(User).count()

    if user_count == 0:
        print('No users found - creating default admin user...')

        # Get credentials from environment or use defaults
        admin_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin')

        # Create admin user
        admin = User(
            email=admin_email,
            hashed_password=hash_password(admin_password)
        )
        db.add(admin)
        db.commit()

        print('')
        print('✓ Created default admin user')
        print(f'  Email:    {admin_email}')
        print(f'  Password: {admin_password}')
        print('')
        print('⚠️  SECURITY WARNING: Please change this password immediately!')
        print('   You can customize credentials via environment variables:')
        print('   - DEFAULT_ADMIN_EMAIL')
        print('   - DEFAULT_ADMIN_PASSWORD')
        print('')
    else:
        print(f'✓ Found {user_count} existing user(s)')

except Exception as e:
    print(f'ERROR creating default user: {e}')
    db.rollback()
    sys.exit(1)
finally:
    db.close()
PYEOF

# Start the application
echo ""
echo "========================================="
echo "Starting FastAPI application..."
echo "========================================="
cd /app
exec uvicorn backend.main:app --host 0.0.0.0 --port 3000
