import React, { useState, useEffect } from "react";
import { Card, CardContent } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Button } from "./components/ui/button";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, BarChart, Bar } from "recharts";
import { RotateCcw } from "lucide-react";
import { motion } from "framer-motion";

export default function App() {
  const [location, setLocation] = useState("");
  const [mode, setMode] = useState("hourly");
  const [forecastData, setForecastData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchHistory, setSearchHistory] = useState(() => {
    return JSON.parse(localStorage.getItem("searchHistory")) || [];
  });
  const [darkMode, setDarkMode] = useState(false);
  const [chartType, setChartType] = useState("line");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!location) return;
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/weather?location=${encodeURIComponent(location)}&mode=${mode}`);
      if (!response.ok) {
        throw new Error("Failed to fetch weather data.");
      }
      const data = await response.json();
      setForecastData(data);

      const newHistory = [location, ...searchHistory.filter((loc) => loc !== location)].slice(0, 5);
      setSearchHistory(newHistory);
      localStorage.setItem("searchHistory", JSON.stringify(newHistory));
    } catch (error) {
      console.error("Error fetching weather data:", error);
      setError("Failed to load weather data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearchHistoryClick = async (loc) => {
    setLocation(loc);
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/weather?location=${encodeURIComponent(loc)}&mode=${mode}`);
      if (!response.ok) {
        throw new Error("Failed to fetch weather data.");
      }
      const data = await response.json();
      setForecastData(data);
    } catch (error) {
      console.error("Error fetching weather data:", error);
      setError("Failed to load weather data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const ChartComponent = chartType === "bar" ? BarChart : LineChart;
  const TempComponent = chartType === "bar" ? Bar : Line;

  const averageTemp = forecastData.length > 0 ? (forecastData.reduce((sum, item) => sum + item.temperature_c, 0) / forecastData.length).toFixed(1) : 0;
  const averageHumidity = forecastData.length > 0 ? (forecastData.reduce((sum, item) => sum + item.humidity_percent, 0) / forecastData.length).toFixed(1) : 0;

  return (
    <div className={`${darkMode ? "bg-gray-900 text-white" : "bg-gradient-to-b from-blue-100 to-blue-300 text-black"} min-h-screen p-4 transition-colors duration-500`}>
      <div className="max-w-4xl mx-auto">
        <motion.h1
          className="text-3xl font-bold mb-4 text-center"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Weather Forecast App
        </motion.h1>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-4">
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

        <div className="flex justify-between items-center mb-4">
          <div className="space-x-2">
            <Button onClick={() => setChartType(chartType === "line" ? "bar" : "line")}>Toggle Chart</Button>
            <Button onClick={() => setDarkMode(!darkMode)}>{darkMode ? "Light Mode" : "Dark Mode"}</Button>
          </div>
        </div>

        {searchHistory.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-semibold mb-1">Recent Searches:</p>
            <div className="flex flex-wrap gap-2">
              {searchHistory.map((loc, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSearchHistoryClick(loc)}
                  className="bg-white rounded px-3 py-1 shadow text-sm"
                >
                  {loc}
                </button>
              ))}
            </div>
          </div>
        )}

        {error && (
          <motion.div className="text-center text-red-600 font-medium mb-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            {error}
          </motion.div>
        )}

        {loading && (
          <div className="text-center mb-4">
            <motion.div
              className="inline-flex items-center gap-2 text-blue-700 font-medium"
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
            >
              <RotateCcw className="animate-spin" /> Loading weather data...
            </motion.div>
          </div>
        )}

        {!loading && forecastData.length > 0 && (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-white rounded-lg p-4 shadow text-center">
                <h3 className="text-sm font-medium">Average Temp (°C)</h3>
                <p className="text-2xl font-bold">{averageTemp}</p>
              </div>
              <div className="bg-white rounded-lg p-4 shadow text-center">
                <h3 className="text-sm font-medium">Average Humidity (%)</h3>
                <p className="text-2xl font-bold">{averageHumidity}</p>
              </div>
            </div>

            <Card className="mb-6">
              <CardContent>
                <h2 className="text-xl font-semibold mb-4">Temperature & Humidity Forecast</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <ChartComponent data={forecastData}>
                    <XAxis dataKey="recorded_at" tickFormatter={(str) => new Date(str).toLocaleDateString()} />
                    <YAxis yAxisId="left" unit="°C" />
                    <YAxis yAxisId="right" orientation="right" unit="%" />
                    <Tooltip labelFormatter={(label) => new Date(label).toLocaleString()} />
                    <Legend />
                    <TempComponent yAxisId="left" type="monotone" dataKey="temperature_c" stroke="#8884d8" fill="#8884d8" strokeWidth={2} name="Temperature (°C)" />
                    <TempComponent yAxisId="right" type="monotone" dataKey="humidity_percent" stroke="#82ca9d" fill="#82ca9d" strokeWidth={2} name="Humidity (%)" />
                  </ChartComponent>
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
