#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head

echo "Seeding users..."
python -m scripts.seed

echo "Starting service..."
exec "$@"