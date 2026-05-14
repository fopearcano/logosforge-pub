#!/usr/bin/env bash
# LOGOSFORGE — local-disk restore helper.
#
# Usage: ./scripts/restore.sh <backup-file>
#
#   *.sql.gz     → restored into $DATABASE_URL via psql
#   *.sqlite.gz  → unzipped to $SQLITE_PATH (default backend/logosforge.db)
#   *.tar.gz     → extracted into $(dirname "$STORAGE_PATH")
#
# This is a placeholder pattern. Verify destinations before running.
set -euo pipefail

[ $# -eq 1 ] || {
    echo "Usage: $0 <backup-file>" >&2
    exit 2
}

SRC=$1
SQLITE_PATH=${SQLITE_PATH:-./backend/logosforge.db}
STORAGE_PATH=${STORAGE_PATH:-./backend/storage}

if [ ! -f "$SRC" ]; then
    echo "[restore] backup not found: $SRC" >&2
    exit 1
fi

case "$SRC" in
    *.sql.gz)
        if [ -z "${DATABASE_URL:-}" ]; then
            echo "[restore] DATABASE_URL must be set to restore Postgres dumps" >&2
            exit 1
        fi
        echo "[restore] applying Postgres dump → $DATABASE_URL"
        gunzip -c "$SRC" | psql "$DATABASE_URL"
        ;;
    *.sqlite.gz)
        echo "[restore] unzipping SQLite → $SQLITE_PATH"
        mkdir -p "$(dirname "$SQLITE_PATH")"
        gunzip -c "$SRC" > "$SQLITE_PATH"
        ;;
    *.tar.gz)
        echo "[restore] extracting storage tree → $(dirname "$STORAGE_PATH")"
        mkdir -p "$(dirname "$STORAGE_PATH")"
        tar -xzf "$SRC" -C "$(dirname "$STORAGE_PATH")"
        ;;
    *)
        echo "[restore] unrecognised backup format: $SRC" >&2
        exit 1
        ;;
esac

echo "[restore] done"
