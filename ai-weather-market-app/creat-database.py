import psycopg2

username = 'joeythe33rd'
password = 'wangu1199oJ*db'

# Define your database connection parameters
host = 'localhost'
database = 'weather_db'
username = 'joeythe33rd'
password = 'wangu1199oJ*db'

try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=username,
        password=password
    )

    # Create a cursor object to execute SQL commands
    cur = conn.cursor()

    # Create the database
    cur.execute('CREATE DATABASE weather_db')

    # Commit the changes
    conn.commit()

    print('Database created successfully!')

except psycopg2.Error as e:
    print(f'Error creating database: {e}')

finally:
    # Close the cursor and connection
    if cur:
        cur.close()
    if conn:
        conn.close()