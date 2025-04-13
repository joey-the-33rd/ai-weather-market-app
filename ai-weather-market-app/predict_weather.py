import os
import psycopg2 # type: ignore
import pandas as pd # type: ignore
import numpy as np
from dotenv import load_dotenv # type: ignore
from tensorflow.keras.models import load_model # type: ignore
from sklearn.preprocessing import MinMaxScaler # type: ignore

# Load environment variables
load_dotenv()

# Load the trained LSTM model
model = load_model(os.path.join(os.path.dirname(__file__), "models/lstm_weather_model.h5"))
# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

# Fetch the last 30 records
query = """
SELECT recorded_at, temperature_c, humidity_percent, wind_speed_kmh, pressure_hpa, precipitation_mm
FROM weather.weather_data
ORDER BY recorded_at DESC
LIMIT 30;
"""
df = pd.read_sql(query, conn)
conn.close()

# Preprocess in chronological order
df = df.dropna().sort_values(by="recorded_at")

# Normalize features
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df[['temperature_c', 'humidity_percent', 'wind_speed_kmh', 'pressure_hpa', 'precipitation_mm']])

# Prepare input for prediction
X_input = np.expand_dims(scaled_data, axis=0)  # Shape: (1, 30, features)

# Predict all features
predicted_scaled = model.predict(X_input)[0]  # Get all predicted features
predicted_data = np.zeros((1, 5))
predicted_data[0] = predicted_scaled  # Store all predictions

# Inverse transform all features
original_values = scaler.inverse_transform(predicted_data)[0]

print("🌤️ Weather Prediction for Next Time Step:")
print(f"•🌡 Temperature: {original_values[0]:.2f}°C")
print(f"• Humidity: {original_values[1]:.2f}%")
print(f"• 💨 Wind Speed: {original_values[2]:.2f} km/h")
print(f"• Pressure: {original_values[3]:.2f} hPa")
print(f"• 🌧 Precipitation: {original_values[4]:.2f} mm")
