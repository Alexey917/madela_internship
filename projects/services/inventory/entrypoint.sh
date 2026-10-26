#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head

echo "Seeding inventory..."
python -m scripts.seed

echo "Starting service..."
exec "$@"