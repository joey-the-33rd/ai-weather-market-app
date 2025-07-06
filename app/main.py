from app.weather_data import fetch_weather_data
from app.ai_model import predict_impact

def main():
    print("Fetching weather data...")
    data = fetch_weather_data()
    print("Predicting market impact...")
    prediction = predict_impact(data)
    print(f"Prediction: {prediction}")

if __name__ == "__main__":
    main()
