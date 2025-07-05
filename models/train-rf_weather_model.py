import os
import psycopg2
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Load environment variables
load_dotenv()

# Secure DB credentials
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Connect to the database
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    print("✅ Connected to PostgreSQL.")
except Exception as e:
    print("❌ Connection error:", e)
    exit()

# Query historical weather data
query = """
SELECT 
    temperature_c,
    humidity_percent,
    wind_speed_kmh,
    pressure_hpa,
    precipitation_mm
FROM weather_data
WHERE temperature_c IS NOT NULL
ORDER BY recorded_at;
"""

df = pd.read_sql(query, conn)
print(f"[INFO] Retrieved {len(df)} records from database")

# Handle missing values
df.dropna(inplace=True)
print(f"[INFO] After dropping nulls: {len(df)} records remain")

# Features and target
X = df.drop(columns=['temperature_c'])
y = df['temperature_c']

# Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define hyperparameter grid
param_grid = {
    "n_estimators": [50, 100, 200],
    "max_depth": [10, 20, 30],
    "min_samples_split": [2, 5, 10],
}

# Run Grid Search
model = RandomForestRegressor(random_state=42)
grid_search = GridSearchCV(model, param_grid, cv=3, scoring="neg_mean_squared_error", n_jobs=-1)
grid_search.fit(X_train, y_train)

# Best model
best_model = grid_search.best_estimator_
print("Best Parameters:", grid_search.best_params_)

# Evaluate on test set
y_pred = best_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"[RESULT] Test MSE: {mse:.4f}")

# Save the best model
import joblib
model_path = os.path.join(os.path.dirname(__file__), "rf_weather_model.joblib")
joblib.dump(best_model, model_path)
print(f"[INFO] Best Random Forest model saved to {model_path}")
