#!/bin/sh
set -e

DB_HOST="db"
DB_PORT="5432"

echo "Attempting to connect to database at $DB_HOST:$DB_PORT..."

# Wait until the port is open
while ! nc -z $DB_HOST $DB_PORT; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is up!"

echo "Running database migrations..."
alembic upgrade head

echo "Starting Uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
