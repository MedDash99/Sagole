#!/bin/sh
# wait-for-postgres.sh

set -e

# The 'db' here is the service name from docker-compose.yml
host="$1"
shift
cmd="$@"

# The default postgres port is 5432
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd