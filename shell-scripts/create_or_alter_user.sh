#!/bin/bash

# This script checks if the PostgreSQL user "weather_db" exists.
# If it does not exist, it creates the user with the specified password.
# If it exists, it alters the password.

# Set variables with defaults, can be overridden by environment variables
PGUSER="${PGUSER:-joeythe33rd}"  # Updated to use your superuser
PGDATABASE="${PGDATABASE:-postgres}"  # Change this if your default database is different
USERNAME="weather_db"
PASSWORD="weather_db_user_2025"

# Test connection to PostgreSQL
psql -U "$PGUSER" -d "$PGDATABASE" -c '\q' 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Error: Unable to connect to PostgreSQL with user '$PGUSER' and database '$PGDATABASE'."
  echo "Please check your PostgreSQL server, user, and database settings."
  exit 1
fi

# Check if user exists
USER_EXISTS=$(psql -U "$PGUSER" -d "$PGDATABASE" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$USERNAME'")

if [ "$USER_EXISTS" = "1" ]; then
  echo "User $USERNAME exists. Altering password..."
  psql -U "$PGUSER" -d "$PGDATABASE" -c "ALTER USER $USERNAME WITH PASSWORD '$PASSWORD';"
else
  echo "User $USERNAME does not exist. Creating user..."
  psql -U "$PGUSER" -d "$PGDATABASE" -c "CREATE USER $USERNAME WITH PASSWORD '$PASSWORD';"
fi

echo "Operation completed."
