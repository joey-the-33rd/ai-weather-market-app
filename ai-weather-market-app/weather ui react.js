import React, { useState } from 'react';
import axios from 'axios';

export default function WeatherApp() {
  const [city, setCity] = useState('Nairobi');
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWeather = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`/weather?city=${encodeURIComponent(city)}`);
      const data = res?.data;

      if (
        data &&
        typeof data === 'object' &&
        'city' in data &&
        'temperature_c' in data &&
        typeof data.temperature_c === 'number'
      ) {
        setWeather(data);
      } else {
        throw new Error('Invalid data format received');
      }
    } catch (err) {
      setError('Unable to fetch weather data');
      console.error('Error fetching weather:', err?.response?.data || err.message || err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-200 to-green-100 p-4">
      <h1 className="text-3xl font-bold mb-6">Kenyan Weather Predictor</h1>
      <div className="bg-white shadow-xl rounded-2xl p-6 w-full max-w-md">
        <input
          type="text"
          placeholder="Enter city (e.g. Nairobi)"
          className="w-full p-2 mb-4 border rounded"
          value={city}
          onChange={(e) => setCity(e.target.value)}
        />
        <button
          onClick={fetchWeather}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
        >
          {loading ? 'Fetching...' : 'Get Weather'}
        </button>

        {error && <p className="text-red-500 mt-4">{error}</p>}

        {weather && (
          <div className="mt-6 text-gray-800">
            <h2 className="text-xl font-semibold mb-2">{weather.city}, {weather.country}</h2>
            <p><strong>Temperature:</strong> {weather.temperature_c} °C</p>
            <p><strong>Humidity:</strong> {weather.humidity}%</p>
            <p><strong>Condition:</strong> {weather.condition}</p>
          </div>
        )}
      </div>
    </div>
  );
}
