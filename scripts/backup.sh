#!/usr/bin/env bash
# LOGOSFORGE — local-disk backup helper.
#
# Detects whether the configured database is SQLite or PostgreSQL and
# writes a timestamped, gzipped dump under $BACKUP_DIR. Also bundles
# the attachment storage tree so restored databases line up with the
# files they reference.
#
# This is a placeholder pattern, not a managed-backup pipeline:
# wire in your own retention, off-site copy, and verification before
# relying on it.
set -euo pipefail

BACKUP_DIR=${BACKUP_DIR:-./backups}
SQLITE_PATH=${SQLITE_PATH:-./backend/logosforge.db}
STORAGE_PATH=${STORAGE_PATH:-./backend/storage}

mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)

backup_database() {
    if [ -n "${DATABASE_URL:-}" ] && [[ "$DATABASE_URL" =~ ^postgres ]]; then
        local out="$BACKUP_DIR/db-$TIMESTAMP.sql.gz"
        echo "[backup] dumping Postgres → $out"
        pg_dump --no-owner --no-privileges "$DATABASE_URL" | gzip > "$out"
        echo "[backup] postgres dump complete · $(stat -c%s "$out" 2>/dev/null || stat -f%z "$out") bytes"
    elif [ -f "$SQLITE_PATH" ]; then
        local out="$BACKUP_DIR/db-$TIMESTAMP.sqlite.gz"
        echo "[backup] copying SQLite → $out"
        gzip -c "$SQLITE_PATH" > "$out"
        echo "[backup] sqlite copy complete · $(stat -c%s "$out" 2>/dev/null || stat -f%z "$out") bytes"
    else
        echo "[backup] no database located (set DATABASE_URL or SQLITE_PATH)" >&2
        return 1
    fi
}

backup_storage() {
    if [ -d "$STORAGE_PATH" ] && [ -n "$(ls -A "$STORAGE_PATH" 2>/dev/null)" ]; then
        local out="$BACKUP_DIR/storage-$TIMESTAMP.tar.gz"
        echo "[backup] archiving storage tree → $out"
        tar -czf "$out" -C "$(dirname "$STORAGE_PATH")" "$(basename "$STORAGE_PATH")"
    else
        echo "[backup] storage tree empty or missing — skipping"
    fi
}

backup_database
backup_storage
echo "[backup] done · $TIMESTAMP"
