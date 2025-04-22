import os


model = load_model(os.path.join(os.path.dirname(__file__), "models/lstm_weather_model.h5")) # type: ignore
