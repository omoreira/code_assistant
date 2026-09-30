#!/usr/bin/env bash

# Create a new SQLite database at a user-selected path. Pass an optional
# generated .sql schema file to initialize its tables in the same step.
set -euo pipefail

usage() {
    echo "Usage: $0 <database-path> [schema.sql]" >&2
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
    usage
    exit 2
fi

database_path=$1
schema_path=${2:-}

if ! command -v sqlite3 >/dev/null 2>&1; then
    echo "Error: sqlite3 CLI is required. Install SQLite and try again." >&2
    exit 1
fi

if [[ -e "$database_path" ]]; then
    echo "Error: refusing to overwrite existing path: $database_path" >&2
    exit 1
fi

if [[ -n "$schema_path" && ! -f "$schema_path" ]]; then
    echo "Error: schema file not found: $schema_path" >&2
    exit 1
fi

parent_dir=$(dirname -- "$database_path")
mkdir -p -- "$parent_dir"

if [[ -n "$schema_path" ]]; then
    sqlite3 "$database_path" < "$schema_path"
else
    # Opening the path with SQLite creates a valid, empty SQLite database.
    sqlite3 "$database_path" 'PRAGMA user_version;'
fi

echo "Created SQLite database: $database_path"
