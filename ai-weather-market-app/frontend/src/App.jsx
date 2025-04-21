import React, { useState } from "react";
import axios from "axios";
import { Card, CardContent } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Button as UIButton } from "./components/ui/button";

export default function App() {
  const [location, setLocation] = useState("");
  const [weatherData, setWeatherData] = useState(null);

  const fetchWeather = async () => {
    try {
      const response = await axios.get("/api/weather", 
        {
        params: { location }
      });
      setWeatherData(response.data);
    } catch (error) {
      console.error("Error fetching weather data:", error);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <Card>
        <CardContent>
          <h1>Weather App</h1>
          <Input
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter location"
          />
          <UIButton onClick={fetchWeather}>Get Weather</UIButton>
          {weatherData && weatherData.length > 0 && (
            <div style={{ marginTop: 20, overflowX: 'auto' }}>
              <h2>{weatherData[0].city}, {weatherData[0].country}</h2>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>Time</th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>Temp (°C)</th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>Humidity (%)</th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>Wind (km/h)</th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>Precipitation (mm)</th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>Pressure (hPa)</th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>Latitude</th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>Longitude</th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>Condition</th>
                  </tr>
                </thead>
                <tbody>
                  {weatherData.map((w, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #ccc' }}>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{new Date(w.recorded_at).toLocaleString()}</td>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{w.temperature_c}</td>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{w.humidity_percent}</td>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{w.wind_speed_kmh}</td>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{w.precipitation_mm ?? 'N/A'}</td>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{w.pressure_hpa}</td>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{w.latitude}</td>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{w.longitude}</td>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{w.weather_condition}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

        </CardContent>
      </Card>
    </div>
  );
}
