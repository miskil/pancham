#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL is not set"
  echo "Set DATABASE_URL and run again."
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "WARNING: This will drop all tables and data in DATABASE_URL"
echo "Target DB: ${DATABASE_URL}"
read -r -p "Type RESET to continue: " CONFIRM
if [[ "$CONFIRM" != "RESET" ]]; then
  echo "Cancelled."
  exit 0
fi

SYNC_DB_URL="${DATABASE_URL/postgresql+asyncpg:\/\//postgresql://}"

psql "$SYNC_DB_URL" -v ON_ERROR_STOP=1 <<'SQL'
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;
SQL

echo "Schema reset complete. Running migrations..."
source backend/venv/bin/activate
alembic -c backend/alembic.ini upgrade head

echo "Done. All tables recreated from migrations."
