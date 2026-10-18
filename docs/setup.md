# Environment Setup for AI-Powered Weather & Market Prediction App

This document provides step-by-step instructions to set up the development environment for the AI Weather Market App project.

---

## Prerequisites

Before starting, ensure you have the following installed on your system:

- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL (version 12 or higher recommended)
- Node.js and npm (for frontend setup)
- Git (for cloning the repository)

---

## Step 1: Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/joey-the-33rd/ai-weather-market-app.git
cd ai-weather-market-app
```

---

## Step 2: Install Backend Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

This will install packages including Flask, Flask-CORS, python-dotenv, h2o, pandas, requests, psycopg2, scikit-learn, numpy, joblib, pytz, and others.

---

## Step 3: Configure Environment Variables

Create a `.env` file in the root directory of the project with the following variables:

```
# Flask server port
PORT=4000

# PostgreSQL database connection
DB_NAME=weather_db
DB_USER=weather_db
DB_PASSWORD=weather_db_user_2025
DB_HOST=localhost
DB_PORT=5432

# Weather API key for data ingestion
WEATHERAPI_KEY=your_weatherapi_key_here
```

Replace `your_weatherapi_key_here` with your actual API key from [weatherapi.com](https://www.weatherapi.com/).

---

## Step 4: Setup PostgreSQL User

Run the provided shell script to create or update the PostgreSQL user for the app:

```bash
bash shell-scripts/create_or_alter_user.sh
```

This script will create the user `weather_db` with password `weather_db_user_2025` if it does not exist, or update the password if it does.

---

## Step 5: Create the Database

Log into PostgreSQL and create the database:

```sql
CREATE DATABASE weather_db;
```

You can do this via `psql` CLI or a GUI tool like pgAdmin.

---

## Step 6: Start and Troubleshoot PostgreSQL Database

### Starting PostgreSQL

- On macOS, if installed via Homebrew, start PostgreSQL with:

```bash
brew services start postgresql
```

- To stop PostgreSQL:

```bash
brew services stop postgresql
```

- To check PostgreSQL status:

```bash
brew services list
```

- Alternatively, use `pg_ctl` commands or your OS-specific service manager.

### Troubleshooting

- Ensure PostgreSQL server is running before connecting.
- Verify your PostgreSQL user and password are correct.
- Check that the database `weather_db` exists.
- If you encounter connection errors, verify the host and port in your `.env` file.
- Use the test connection script to verify connectivity:

```bash
python tests/test_db_connection.py
```

---

## Step 7: Initialize the Database Schema

Run the database setup script to create necessary tables and schema:

```bash
python setup_db.py
```

---

## Step 8: Start the Backend Server

Start the Flask API server:

```bash
bash shell-scripts/run_flask.sh
```

The server will start on the port specified in your `.env` file (default 4000).

---

## Step 9: Setup and Start the Frontend

Navigate to the frontend directory, install dependencies, and start the frontend app:

```bash
cd frontend
npm install
npm start
```

---

## Additional Notes

- To ingest weather data, run:

```bash
python ins-weather-data.py
```

- To train the AI model, run:

```bash
python train-rf_weather_model.py
```

- To read recent weather data records, run:

```bash
python read_weather_data.py
```

- If you encounter permission issues with the shell script, make it executable:

```bash
chmod +x create_or_alter_user.sh
```

---

## Resources

- [WeatherAPI](https://www.weatherapi.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Native Documentation](https://reactnative.dev/)

---

This completes the environment setup for the AI Weather Market App. You are now ready to develop and run the application locally.
