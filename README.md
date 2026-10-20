# AI Weather Market App

A weather dashboard for hourly and daily forecasts. The web UI is in `frontend/`; the Flask API entry point used by the Procfile is `app.py`.

## Current capabilities

- Retrieves up to three days of hourly or daily forecast data from WeatherAPI.com.
- Displays temperature, humidity, wind, pressure, precipitation, UV and available air-quality fields.
- Returns a consistent JSON array from `GET /api/weather`.
- Trains a one-hour-ahead weather model on historical hourly observations from six Kenyan locations.
- Exposes a dedicated AI forecast endpoint with temperature and precipitation estimates plus chronological holdout metrics.

Market-price forecasting, credit scoring, blockchain contracts, and emergency-alert workflows are not implemented by the current API and should not be treated as production capabilities.

## Requirements

- Python 3.11+
- Node.js and npm
- A WeatherAPI.com API key
- Internet access during training to download historical hourly weather data from Open-Meteo

## Local setup

1. Install Python dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create a root `.env` file and do not commit it:

   ```dotenv
   WEATHERAPI_KEY=your_weatherapi_key
   PORT=5050
   FLASK_DEBUG=false
   ```

The old `/predict` endpoint now returns HTTP 410 so the unrelated medical model cannot be mistaken for weather predictions. The `/login` route does not issue tokens because this repository has no real user store or identity provider.

3. Train the weather model from the repository root (this downloads several years of hourly reanalysis data for six Kenyan locations):

   ```bash
   python train_weather_model.py
   ```

   This writes `weather_model.joblib`. Review printed test MAE against the persistence baseline before relying on predictions. Training needs internet access and may take several minutes.

4. Start the API from the repository root with `python app.py`.

5. In another terminal, run `cd frontend`, `npm install`, then `npm start`. The development server proxies `/api` requests to `http://localhost:5050`. For a separately hosted frontend, set `REACT_APP_API_BASE_URL` to the deployed backend origin and set backend `CORS_ORIGINS` to the exact frontend origin (comma-separated if there are multiple).

## API

### `GET /api/weather?location=Nairobi&mode=hourly`

- `location` is required.
- `mode` is `hourly` (default) or `daily`.
- Returns an array of records with fields such as `recorded_at`, `temperature_c`, `humidity_percent`, `wind_speed_kmh`, `weather_condition`, and `weather_icon`.
- Returns a useful HTTP error when the API key is missing, the provider times out, or the location cannot be resolved.

### `GET /api/ai-forecast?location=Nairobi&hours=24`

- Requires `weather_model.joblib` on the backend host; otherwise returns HTTP 503 with setup guidance.
- `hours` must be between 1 and 48.
- Returns one-hour-ahead temperature and precipitation estimates, model training dates, source information, and held-out MAE compared with a persistence baseline.
- Training uses Open-Meteo historical hourly reanalysis data from Nairobi, Mairo Inya, Eldoret, Kisumu, Mombasa, and Lodwar. The latest 20% of each location timeline is held out chronologically.
- These are experimental estimates, not official forecasts or guarantees.

### `POST /predict`

Retired with HTTP 410 because the previous endpoint used an unrelated medical model.

## Deployment notes

- Configure `WEATHERAPI_KEY` in the backend host's secret/environment settings; never put it in frontend code.
- Set frontend `REACT_APP_API_BASE_URL` to the backend origin and backend `CORS_ORIGINS` to the exact frontend origin when deployed separately.
- Install dependencies from `requirements.txt` and use the `Procfile` for a Gunicorn deployment.
- Test the deployed API and frontend together before calling the application production-ready.

## Security and limitations

- Never commit `.env`, API keys, JWT secrets, or user credentials.
- Weather lookup is public and should be rate-limited at the hosting layer before broad release.
- The AI forecast endpoint requires a trained `weather_model.joblib` artifact. For a separate backend host, run `python train_weather_model.py` during the build step, then start with `gunicorn app:app`. Set `WEATHER_MODEL_PATH` if the artifact is stored elsewhere.
- Check held-out metrics against the persistence baseline; a trained model is not automatically a useful model.
- Forecast and air-quality availability and provider quotas depend on the WeatherAPI.com plan and response.

## License

MIT. See [LICENSE](LICENSE).
