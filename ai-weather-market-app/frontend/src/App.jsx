import React, { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Button as UIButton } from "./components/ui/button";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";

export default function App() {
  const [location, setLocation] = useState("");
  const [weatherData, setWeatherData] = useState(null);
  const [darkMode, setDarkMode] = useState(() => {
    const stored = localStorage.getItem("darkMode");
    return stored ? JSON.parse(stored) : false;
  });

  useEffect(() => {
    localStorage.setItem("darkMode", JSON.stringify(darkMode));
  }, [darkMode]);

  const fetchWeather = async () => {
    try {
      const response = await axios.get("/api/weather", {
        params: { location }
      });
      setWeatherData(response.data);
    } catch (error) {
      console.error("Error fetching weather data:", error);
    }
  };

  const containerStyle = {
    padding: 20,
    backgroundColor: darkMode ? '#121212' : '#f5f5f5',
    color: darkMode ? '#fff' : '#000',
    minHeight: '100vh',
    transition: 'background-color 0.3s ease, color 0.3s ease'
  };

  return (
    <div style={containerStyle}>
      <Card>
        <CardContent>
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1>Weather App</h1>
            <UIButton onClick={() => setDarkMode(!darkMode)} style={{ marginBottom: 10 }}>
              Toggle {darkMode ? "Light" : "Dark"} Mode
            </UIButton>
            <Input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Enter location"
            />
            <UIButton onClick={fetchWeather} style={{ marginTop: 10 }}>Get Weather</UIButton>
          </motion.div>

          {weatherData && weatherData.length > 0 && (
            <motion.div
              style={{ marginTop: 20, overflowX: 'auto' }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <h2>{weatherData[0].city}, {weatherData[0].country}</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weatherData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="recorded_at" tickFormatter={(time) => new Date(time).toLocaleTimeString()} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="temperature_c" stroke="#8884d8" name="Temp (°C)" />
                  <Line type="monotone" dataKey="humidity_percent" stroke="#82ca9d" name="Humidity (%)" />
                  <Line type="monotone" dataKey="wind_speed_kmh" stroke="#ffc658" name="Wind (km/h)" />
                  <Line type="monotone" dataKey="precipitation_mm" stroke="#ff7300" name="Precipitation (mm)" />
                </LineChart>
              </ResponsiveContainer>

              <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 20 }}>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Temp (°C)</th>
                    <th>Humidity (%)</th>
                    <th>Wind (km/h)</th>
                    <th>Precipitation (mm)</th>
                    <th>Pressure (hPa)</th>
                    <th>Latitude</th>
                    <th>Longitude</th>
                    <th>Condition</th>
                  </tr>
                </thead>
                <tbody>
                  {weatherData.map((w, index) => (
                    <tr key={index}>
                      <td>{new Date(w.recorded_at).toLocaleString()}</td>
                      <td>{w.temperature_c}</td>
                      <td>{w.humidity_percent}</td>
                      <td>{w.wind_speed_kmh}</td>
                      <td>{w.precipitation_mm ?? 'N/A'}</td>
                      <td>{w.pressure_hpa}</td>
                      <td>{w.latitude}</td>
                      <td>{w.longitude}</td>
                      <td>{w.weather_condition}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
