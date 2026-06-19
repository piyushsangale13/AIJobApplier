#!/bin/sh
set -eu

echo "Waiting for postgres to accept connections..."
until pg_isready -h postgres -U postgres -d ai_job_applier; do
  sleep 2
done

echo "Creating default tables..."
psql -h postgres -U postgres -d ai_job_applier -f /db-init/create_default_tables.sql

echo "Inserting default data..."
psql -h postgres -U postgres -d ai_job_applier -f /db-init/insert_default_data.sql

echo "Database initialization complete."
