import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Legend
} from 'recharts';

export default function WeatherApp() {
  const [city, setCity] = useState('Nairobi');
  const [weather, setWeather] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(() => {
    const storedMode = localStorage.getItem('darkMode');
    return storedMode ? JSON.parse(storedMode) : false;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const fetchWeather = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`/api/weather?location=${encodeURIComponent(city)}`);
      const data = res?.data;
      console.log("Fetched weather data:", data);

      if (
        Array.isArray(data) &&
        data.length > 0 &&
        data[0].city &&
        typeof data[0].temperature_c === 'number'
      ) {
        setWeather(data);
      } else {
        throw new Error('Invalid data format received');
      }
    } catch (err) {
      setError('Unable to fetch weather data');
      console.error('Error fetching weather:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`/predict?city=${encodeURIComponent(city)}`);
      const data = res?.data;

      if (Array.isArray(data)) {
        setForecast(data);
      } else {
        throw new Error('Invalid forecast data received');
      }
    } catch (err) {
      setError('Unable to fetch forecast data');
      console.error('Error fetching forecast:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center p-4 transition-colors duration-500 ${darkMode ? 'bg-gray-900 text-white' : 'bg-gradient-to-br from-blue-200 to-green-100 text-gray-800'}`}>
      <motion.h1 className="text-3xl font-bold mb-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1 }}>
        Kenyan Weather Predictor
      </motion.h1>
      <motion.div 
        className={`shadow-xl rounded-2xl p-6 w-full max-w-md transition-colors duration-500 ${darkMode ? 'bg-gray-800 text-white' : 'bg-white'}`}
        initial={{ y: 30, opacity: 0 }} 
        animate={{ y: 0, opacity: 1 }} 
        transition={{ duration: 0.5 }}
      >
        <div className="flex justify-between items-center mb-4">
          <input
            type="text"
            placeholder="Enter city (e.g. Nairobi)"
            className={`w-full p-2 mr-2 border rounded ${darkMode ? 'bg-gray-700 border-gray-600 text-white' : ''}`}
            value={city}
            onChange={(e) => setCity(e.target.value)}
          />
          <motion.button
            onClick={() => setDarkMode(!darkMode)}
            whileTap={{ rotate: 360 }}
            transition={{ type: 'spring', stiffness: 200 }}
            className={`px-3 py-1 rounded font-semibold ${darkMode ? 'bg-yellow-400 text-black' : 'bg-gray-800 text-white'}`}
          >
            {darkMode ? '☀️' : '🌙'}
          </motion.button>
        </div>

        <div className="flex gap-2">
          <button
            onClick={fetchWeather}
            className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
          >
            {loading ? 'Fetching...' : 'Get Weather'}
          </button>
          <button
            onClick={fetchForecast}
            className="flex-1 bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded"
          >
            {loading ? 'Predicting...' : 'Get Forecast'}
          </button>
        </div>

        {error && <p className="text-red-500 mt-4">{error}</p>}

          {weather.length > 0 && (
          <>
            {console.log("Current weather state:", weather)}
            <motion.div className="mt-6 p-4 border-2 border-blue-500 rounded-lg bg-blue-50 dark:bg-gray-700" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
              <h2 className="text-2xl font-bold mb-4 text-blue-700 dark:text-blue-300">{weather[0].city}, {weather[0].country}</h2>
              <div className="overflow-auto max-h-96">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr>
                      <th className="border-b border-blue-500 px-2 py-1">Time</th>
                      <th className="border-b border-blue-500 px-2 py-1">Temp (°C)</th>
                      <th className="border-b border-blue-500 px-2 py-1">Humidity (%)</th>
                      <th className="border-b border-blue-500 px-2 py-1">Wind (km/h)</th>
                      <th className="border-b border-blue-500 px-2 py-1">Precipitation (mm)</th>
                      <th className="border-b border-blue-500 px-2 py-1">Pressure (hPa)</th>
                      <th className="border-b border-blue-500 px-2 py-1">Latitude</th>
                      <th className="border-b border-blue-500 px-2 py-1">Longitude</th>
                      <th className="border-b border-blue-500 px-2 py-1">Condition</th>
                    </tr>
                  </thead>
                  <tbody>
                    {weather.map((w, index) => (
                      <tr key={index} className="border-b border-blue-300">
                        <td className="px-2 py-1">{new Date(w.recorded_at).toLocaleString()}</td>
                        <td className="px-2 py-1">{w.temperature_c}</td>
                        <td className="px-2 py-1">{w.humidity_percent}</td>
                        <td className="px-2 py-1">{w.wind_speed_kmh}</td>
                        <td className="px-2 py-1">{w.precipitation_mm ?? 'N/A'}</td>
                        <td className="px-2 py-1">{w.pressure_hpa}</td>
                        <td className="px-2 py-1">{w.latitude}</td>
                        <td className="px-2 py-1">{w.longitude}</td>
                        <td className="px-2 py-1">{w.weather_condition}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </>
        )}

        {forecast && (
          <motion.div className="mt-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
            <h3 className="text-lg font-bold mb-2">7-Day Forecast</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={forecast} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="5 5" />
                <XAxis dataKey="date" stroke={darkMode ? '#fff' : '#000'} />
                <YAxis stroke={darkMode ? '#fff' : '#000'} />
                <Tooltip contentStyle={{ backgroundColor: darkMode ? '#333' : '#fff', color: darkMode ? '#fff' : '#000' }} />
                <Legend />
                <Line type="monotone" dataKey="temperature_c" stroke="#8884d8" strokeWidth={2} name="Temp (°C)" />
                <Line type="monotone" dataKey="humidity_percent" stroke="#82ca9d" strokeWidth={2} name="Humidity (%)" />
                <Line type="monotone" dataKey="wind_speed_kmh" stroke="#ffc658" strokeWidth={2} name="Wind (km/h)" />
                <Line type="monotone" dataKey="precipitation_mm" stroke="#ff7300" strokeWidth={2} name="Precipitation (mm)" />
              </LineChart>
            </ResponsiveContainer>
            <ul className="space-y-2 mt-4">
              {forecast.map((day, index) => (
                <li key={index} className={`p-2 rounded text-sm ${darkMode ? 'bg-gray-700' : 'bg-blue-100'}`}>
                  <strong>{day.date}:</strong> {day.temperature_c.toFixed(1)} °C, {day.weather_condition}
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
