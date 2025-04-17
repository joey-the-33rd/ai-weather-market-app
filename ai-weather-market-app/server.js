const express = require("express");
const cors = require("cors");
const { Pool } = require("pg");
require("dotenv").config();

const app = express();
app.use(cors());

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

app.get("/api/weather", async (req, res) => {
  const { location } = req.query;
  if (!location) return res.status(400).json({ error: "Missing location" });

  try {
    const query = `
      SELECT 
        location,
        latitude,
        longitude,
        recorded_at,
        temperature_c,
        humidity_percent,
        wind_speed_kmh,
        pressure_hpa,
        precipitation_mm,
        city,
        weather_condition
      FROM weather_data
      WHERE LOWER(city) = LOWER($1)
      ORDER BY recorded_at DESC
      LIMIT 10;
    `;

    const { rows } = await pool.query(query, [location]);
    res.json(rows);
  } catch (err) {
    console.error("Error querying DB:", err);
    res.status(500).json({ error: "Database error" });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
