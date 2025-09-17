#!/bin/sh
set -e # Stop execution if any script line returns not `true`

# If a sqlite DB exists at /data/laterbot-tortoise.sqlite3, create a symlink to the
# location the bot expects relative to src/laterbot (../../data/laterbot-tortoise.sqlite3 from src/laterbot).

DB_HOST_PATH="/data/laterbot-tortoise.sqlite3"
TARGET_PATH="/home/appuser/app/data/laterbot-tortoise.sqlite3"

create_symlink() {
  # Ensure parent directory exists
  mkdir -p "$(dirname "$TARGET_PATH")"
  # Remove any existing target and create the symlink
  rm -f "$TARGET_PATH" || true
  ln -s "$DB_HOST_PATH" "$TARGET_PATH"
  echo "Created symlink $TARGET_PATH -> $DB_HOST_PATH"
}

if [ -f "$DB_HOST_PATH" ]; then
  echo "Found host DB at $DB_HOST_PATH"
  create_symlink
else
  echo "No host DB found at $DB_HOST_PATH. Creating one for the bot to set up..."
  echo "Creating empty file for db..."
  touch "$DB_HOST_PATH"
  echo "Creating symlink..."
  create_symlink
fi

# Run the requested command
exec "$@"
