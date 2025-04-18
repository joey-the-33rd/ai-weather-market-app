// backend/api/weather.js
import express from "express";
import axios from "axios";
import dotenv from "dotenv";
dotenv.config();

const router = express.Router();

router.get("/weather", async (req, res) => {
  const { location, mode = "hourly" } = req.query;

  if (!location) {
    return res.status(400).json({ error: "Location is required" });
  }

  try {
    const response = await axios.get(`http://api.weatherapi.com/v1/forecast.json`, {
      params: {
        key: process.env.WEATHER_API_KEY,
        q: location,
        days: mode === "daily" ? 7 : 1,
        aqi: "no",
        alerts: "no"
      }
    });

    const { location: loc, forecast } = response.data;
    const forecastEntries = mode === "hourly"
      ? forecast.forecastday[0].hour
      : forecast.forecastday.map(day => ({ ...day.day, date: day.date }));

    const parsedData = forecastEntries.map(entry => ({
      recorded_at: new Date(entry.time || entry.date).toISOString(),
      temperature_c: entry.temp_c || entry.avgtemp_c,
      humidity_percent: entry.humidity || entry.avghumidity,
      wind_speed_kmh: entry.wind_kph || entry.maxwind_kph,
      pressure_hpa: entry.pressure_mb || null,
      precipitation_mm: entry.precip_mm || entry.totalprecip_mm,
      city: loc.name,
      latitude: loc.lat,
      longitude: loc.lon,
      weather_condition: entry.condition?.text || "",
      weather_icon: entry.condition?.icon || ""
    }));

    res.json(parsedData);
  } catch (error) {
    console.error("Error fetching weather data:", error.message);
    res.status(500).json({ error: "Failed to fetch weather data." });
  }
});

export default router;
