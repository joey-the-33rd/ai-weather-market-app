# -*- coding: utf-8 -*-
import os
import psycopg2 # type: ignore
import pandas as pd # type: ignore
import numpy as np
from dotenv import load_dotenv # type: ignore
from sklearn.preprocessing import MinMaxScaler # type: ignore
from sklearn.model_selection import train_test_split # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense, Dropout # type: ignore
from tensorflow.keras.callbacks import EarlyStopping # type: ignore

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

# Query historical weather data with all relevant columns
query = """
SELECT 
    recorded_at,
    temperature_c,
    humidity_percent,
    wind_speed_kmh,
    pressure_hpa,
    precipitation_mm,
    wind_direction_deg,
    uv_index,
    air_quality_index,
    weather_condition,
    cloud_cover_percent,
    visibility_km,
    dew_point_c,
    solar_radiation_w_m2,
    sunrise_time,
    sunset_time
FROM weather_data
WHERE temperature_c IS NOT NULL
ORDER BY recorded_at;
"""

df = pd.read_sql(query, conn)
print("[INFO] Retrieved {} records from database".format(len(df)))

# Handle missing values
df.dropna(inplace=True)
print("[INFO] After dropping nulls: {} records remain".format(len(df)))
print("Sample data:")
print(df.head())

# Convert categorical weather_condition to numeric using one-hot encoding
df = pd.get_dummies(df, columns=['weather_condition'])

# Normalize features (excluding recorded_at)
feature_cols = df.columns.difference(['recorded_at', 'temperature_c'])
scaler = MinMaxScaler()
scaled_features = scaler.fit_transform(df[feature_cols])

# Combine scaled features with temperature_c target
scaled_df = pd.DataFrame(scaled_features, columns=feature_cols, index=df.index)
scaled_df['temperature_c'] = df['temperature_c'].values

# Create sequences for LSTM
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(seq_length, len(data)):
        X.append(data.iloc[i-seq_length:i].values)
        y.append(data.iloc[i]['temperature_c'])
    return np.array(X), np.array(y)

SEQ_LENGTH = 10
X, y = create_sequences(scaled_df, SEQ_LENGTH)

# Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build LSTM model
model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(SEQ_LENGTH, X.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(32))
model.add(Dropout(0.2))
model.add(Dense(1))  # Output: predicted temperature

model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()

# Train model
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
history = model.fit(X_train, y_train, epochs=50, batch_size=32,
                    validation_data=(X_test, y_test),
                    callbacks=[early_stop])

# Evaluate
loss = model.evaluate(X_test, y_test)
print("[RESULT] Final Test Loss (MSE): {:.4f}".format(loss))

# Save model and scaler
print("[INFO] Current working directory:", os.getcwd())
model.save("ai-weather-market-app/models/lstm_weather_model.h5")
import joblib # type: ignore
joblib.dump(scaler, "ai-weather-market-app/models/scaler.save")
print("[INFO] Model and scaler saved.")
