#!/bin/sh
set -e

echo "[servario] Starte Datenbankmigrationen …"
alembic upgrade head

echo "[servario] Starte Anwendungsserver …"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
