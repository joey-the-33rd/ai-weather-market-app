// backend/api/weather.ts
import express, { Request, Response } from "express";
import axios from "axios";
import dotenv from "dotenv";
import NodeCache from "node-cache";
import rateLimit from "express-rate-limit";
import morgan from "morgan";
dotenv.config();

const router = express.Router();
const cache = new NodeCache({ stdTTL: 600 }); // Cache for 10 minutes

// Logging middleware
router.use(morgan("combined"));

// Rate limiting middleware
const limiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 30, // limit each IP to 30 requests per minute
  message: "Too many requests from this IP, please try again later."
});

router.use("/weather", limiter);

router.get("/weather", async (req: Request, res: Response) => {
  const { location, mode = "hourly" } = req.query as { location?: string; mode?: string };

  if (!location) {
    return res.status(400).json({ error: "Location is required" });
  }

  const cacheKey = `${location}_${mode}`;
  const cachedData = cache.get(cacheKey);
  if (cachedData) {
    return res.json(cachedData);
  }

  try {
    const response = await axios.get("http://api.weatherapi.com/v1/forecast.json", {
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
      : forecast.forecastday.map((day: any) => ({ ...day.day, date: day.date }));

    const parsedData = forecastEntries.map((entry: any) => ({
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

    cache.set(cacheKey, parsedData);
    res.json(parsedData);
  } catch (error: any) {
    console.error("Error fetching weather data:", error);
    const status = error.response?.status || 500;
    const message = error.response?.data?.error?.message || "Failed to fetch weather data.";
    res.status(status).json({ error: message });
  }
});

export default router;
