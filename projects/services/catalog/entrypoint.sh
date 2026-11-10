#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head

echo "Seeding database..."
python -m scripts.seed

echo "Starting service..."
exec "$@"