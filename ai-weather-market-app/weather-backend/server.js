const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

app.get("/api/weather", async (req, res) => {
    const { location, mode = "hourly" } = req.query;
  
    // ...same WeatherAPI request...
  
    let forecastData;
    if (mode === "daily") {
      forecastData = forecast.forecastday.map((day) => ({
        city: loc.name,
        latitude: loc.lat,
        longitude: loc.lon,
        recorded_at: day.date,
        temperature_c: day.day.avgtemp_c,
        humidity_percent: day.day.avghumidity,
        wind_speed_kmh: day.day.maxwind_kph,
        pressure_hpa: day.day.avgvis_km, // WeatherAPI doesn't give daily pressure directly
        precipitation_mm: day.day.totalprecip_mm,
        weather_condition: day.day.condition.text,
        location: location,
      }));
    } else {
      forecastData = forecast.forecastday.flatMap((day) =>
        day.hour.map((hour) => ({
          city: loc.name,
          latitude: loc.lat,
          longitude: loc.lon,
          recorded_at: hour.time,
          temperature_c: hour.temp_c,
          humidity_percent: hour.humidity,
          wind_speed_kmh: hour.wind_kph,
          pressure_hpa: hour.pressure_mb,
          precipitation_mm: hour.precip_mm,
          weather_condition: hour.condition.text,
          location: location,
        }))
      );
    }
  
    res.json(forecastData);
  });

app.listen(port, () => {
  console.log(`Weather backend server running on port ${port}`);
});
