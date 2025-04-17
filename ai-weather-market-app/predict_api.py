from flask import Flask, jsonify # type: ignore
import os
import psycopg2 # type: ignore
import pandas as pd # type: ignore
import numpy as np
from dotenv import load_dotenv # type: ignore
from tensorflow.keras.models import load_model # type: ignore
from sklearn.preprocessing import MinMaxScaler # type: ignore

app = Flask(__name__)
load_dotenv()

model = load_model(os.path.join(os.path.dirname(__file__), "models/lstm_weather_model.h5"))

def fetch_latest_weather():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    query = """
    SELECT recorded_at, temperature_c, humidity_percent, wind_speed_kmh, pressure_hpa, precipitation_mm
    FROM weather_data
    ORDER BY recorded_at DESC
    LIMIT 30;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.dropna().sort_values(by="recorded_at")

@app.route("/api/predict", methods=["GET"])
def predict_weather():
    try:
        df = fetch_latest_weather()
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(df[['temperature_c', 'humidity_percent', 'wind_speed_kmh', 'pressure_hpa', 'precipitation_mm']])
        X = np.expand_dims(scaled, axis=0)

        predicted_scaled = model.predict(X)[0][0]
        predicted_row = np.zeros((1, 5))
        predicted_row[0][0] = predicted_scaled

        predicted_temp = scaler.inverse_transform(predicted_row)[0][0]

        return jsonify({
            "predicted_temperature_c": round(predicted_temp, 2),
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)
