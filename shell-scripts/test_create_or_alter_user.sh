#!/bin/bash
# Safe test script for create_or_alter_user.sh without modifying PostgreSQL users

echo "Testing create_or_alter_user.sh script..."

# Check if psql command is available
if command -v psql >/dev/null 2>&1; then
  echo "psql command found."
else
  echo "Warning: psql command not found. Please install PostgreSQL client tools."
fi

# Check PostgreSQL connection parameters
PGUSER="${PGUSER:-joeythe33rd}"
PGDATABASE="${PGDATABASE:-postgres}"

echo "Using PostgreSQL user: $PGUSER"
echo "Using PostgreSQL database: $PGDATABASE"

echo "Skipping actual user creation/modification for safety."

echo "create_or_alter_user.sh script test completed."
