// src/App.jsx
import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function App() {
  const [location, setLocation] = useState("");
  const [mode, setMode] = useState("hourly");
  const [forecastData, setForecastData] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!location) return;

    try {
      const response = await fetch(`/api/weather?location=${encodeURIComponent(location)}&mode=${mode}`);
      const data = await response.json();
      setForecastData(data);
    } catch (error) {
      console.error("Error fetching weather data:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-300 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4 text-center">Weather Forecast App</h1>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-6">
          <Input
            type="text"
            placeholder="Enter location (e.g., Nairobi)"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="border rounded px-2 py-1"
          >
            <option value="hourly">Hourly</option>
            <option value="daily">Daily</option>
          </select>
          <Button type="submit">Get Forecast</Button>
        </form>

        {forecastData.length > 0 && (
          <>
            <Card className="mb-6">
              <CardContent>
                <h2 className="text-xl font-semibold mb-4">Temperature Forecast</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={forecastData}>
                    <XAxis dataKey="recorded_at" tickFormatter={(str) => new Date(str).toLocaleDateString()} />
                    <YAxis unit="°C" />
                    <Tooltip labelFormatter={(label) => new Date(label).toLocaleString()} />
                    <Line type="monotone" dataKey="temperature_c" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <h2 className="text-xl font-semibold mb-4">Forecast Details</h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm text-left">
                    <thead>
                      <tr>
                        <th className="px-2 py-1">Date</th>
                        <th className="px-2 py-1">City</th>
                        <th className="px-2 py-1">Lat</th>
                        <th className="px-2 py-1">Lon</th>
                        <th className="px-2 py-1">Temp (°C)</th>
                        <th className="px-2 py-1">Humidity (%)</th>
                        <th className="px-2 py-1">Wind (km/h)</th>
                        <th className="px-2 py-1">Pressure (hPa)</th>
                        <th className="px-2 py-1">Precip (mm)</th>
                        <th className="px-2 py-1">Condition</th>
                      </tr>
                    </thead>
                    <tbody>
                      {forecastData.map((entry, index) => (
                        <tr key={index} className="odd:bg-white even:bg-gray-100">
                          <td className="px-2 py-1">{new Date(entry.recorded_at).toLocaleString()}</td>
                          <td className="px-2 py-1">{entry.city}</td>
                          <td className="px-2 py-1">{entry.latitude}</td>
                          <td className="px-2 py-1">{entry.longitude}</td>
                          <td className="px-2 py-1">{entry.temperature_c}</td>
                          <td className="px-2 py-1">{entry.humidity_percent}</td>
                          <td className="px-2 py-1">{entry.wind_speed_kmh}</td>
                          <td className="px-2 py-1">{entry.pressure_hpa ?? "N/A"}</td>
                          <td className="px-2 py-1">{entry.precipitation_mm}</td>
                          <td className="px-2 py-1 flex items-center gap-2">
                            <img src={`https:${entry.weather_icon}`} alt="icon" className="w-6 h-6" />
                            {entry.weather_condition}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}
