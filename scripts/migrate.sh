#!/bin/bash
# Database migration script

set -e

echo "🔄 Running database migrations..."

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
pip install -q -r requirements.txt

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

echo "✓ Migrations complete!"

