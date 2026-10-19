# AI Weather Market App

A weather dashboard for hourly and daily forecasts. The web UI is in `frontend/`; the Flask API entry point used by the Procfile is `app.py`.

## Current capabilities

- Retrieves up to three days of hourly or daily forecast data from WeatherAPI.com.
- Displays temperature, humidity, wind, pressure, precipitation, UV and available air-quality fields.
- Returns a consistent JSON array from `GET /api/weather`.
- Keeps the optional H2O prediction endpoint separate from weather lookup.

Market-price forecasting, credit scoring, blockchain contracts, and emergency-alert workflows are not implemented by the current API and should not be treated as production capabilities.

## Requirements

- Python 3.11+
- Node.js and npm
- A WeatherAPI.com API key
- Optional: a compatible H2O model directory for `POST /predict`

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

Set a strong `JWT_SECRET` in the backend environment if you configure authenticated prediction requests. The `/login` route intentionally does not issue tokens because this repository does not yet contain a real user store or identity provider.

3. Start the API from the repository root with `python app.py`.

4. In another terminal, run `cd frontend`, `npm install`, then `npm start`. The development server proxies `/api` requests to `http://localhost:5050`. For a separately hosted frontend, set `REACT_APP_API_BASE_URL` to the deployed backend origin and set backend `CORS_ORIGINS` to the exact frontend origin (comma-separated if there are multiple).

## API

### `GET /api/weather?location=Nairobi&mode=hourly`

- `location` is required.
- `mode` is `hourly` (default) or `daily`.
- Returns an array of records with fields such as `recorded_at`, `temperature_c`, `humidity_percent`, `wind_speed_kmh`, `weather_condition`, and `weather_icon`.
- Returns a useful HTTP error when the API key is missing, the provider times out, or the location cannot be resolved.

### `POST /predict`

This endpoint requires a valid Bearer JWT and a compatible H2O model. Production authentication and model-schema validation are still required before exposing it to users.

## Deployment notes

- Configure `WEATHERAPI_KEY` in the backend host's secret/environment settings; never put it in frontend code.
- Set frontend `REACT_APP_API_BASE_URL` to the backend origin and backend `CORS_ORIGINS` to the exact frontend origin when deployed separately.
- Install dependencies from `requirements.txt` and use the `Procfile` for a Gunicorn deployment.
- Test the deployed API and frontend together before calling the application production-ready.

## Security and limitations

- Never commit `.env`, API keys, JWT secrets, or user credentials.
- Weather lookup is public and should be rate-limited at the hosting layer before broad release.
- The prediction endpoint depends on a compatible model and real authentication configuration.
- Forecast and air-quality availability and provider quotas depend on the WeatherAPI.com plan and response.

## License

MIT. See [LICENSE](LICENSE).
