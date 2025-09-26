#!/bin/sh
set -e

alembic upgrade head

exec fastapi dev src/main.py --host 0.0.0.0 --port 8000
