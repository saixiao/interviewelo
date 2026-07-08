#!/usr/bin/env bash
# Quick-start the full local stack: Postgres (docker), FastAPI backend, Vite frontend.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

cleanup() {
  echo "Stopping dev stack..."
  jobs -p | xargs -r kill 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "==> Starting Postgres..."
docker compose up -d postgres

echo "==> Waiting for Postgres to be healthy..."
until [ "$(docker inspect -f '{{.State.Health.Status}}' "$(docker compose ps -q postgres)" 2>/dev/null)" = "healthy" ]; do
  sleep 1
done

echo "==> Running Alembic migrations..."
(cd backend && .venv/bin/alembic upgrade head)

echo "==> Starting backend (http://localhost:8010)..."
(cd backend && .venv/bin/uvicorn app.main:app --reload --port 8010) &

echo "==> Starting frontend (http://localhost:5173)..."
(cd frontend && npm run dev) &

wait
