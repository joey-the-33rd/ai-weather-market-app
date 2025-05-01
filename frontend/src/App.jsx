import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Card, CardContent } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Button as UIButton } from "./components/ui/button";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";
import CustomTooltip from './components/ui/CustomTooltip';
import { GoogleOAuthProvider, GoogleLogin, googleLogout } from '@react-oauth/google';

const clientId = "YOUR_GOOGLE_OAUTH_CLIENT_ID";

export default function App() {
  const [location, setLocation] = useState("");
  const [weatherData, setWeatherData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [darkMode, setDarkMode] = useState(() => {
    const stored = localStorage.getItem("darkMode");
    return stored ? JSON.parse(stored) : false;
  });
  const [forecastView, setForecastView] = useState('hourly');
  const [user, setUser] = useState(null);
  const [liveUpdate, setLiveUpdate] = useState(false);
  const intervalRef = useRef(null);

  useEffect(() => {
    localStorage.setItem("darkMode", JSON.stringify(darkMode));
  }, [darkMode]);

  useEffect(() => {
    if (liveUpdate) {
      fetchWeather();
      intervalRef.current = setInterval(() => {
        fetchWeather();
      }, 10000); // fetch every 10 seconds
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [liveUpdate, location, forecastView]);

  const fetchWeather = async () => {
    try {
      const response = await axios.get("/api/weather", {
        params: { location, mode: forecastView }
      });
      setWeatherData(response.data);

      // Fetch prediction from backend
      if (response.data && response.data.length > 0) {
        const latestData = response.data[0];
        const predictionResponse = await axios.post("/predict", latestData);
        setPrediction(predictionResponse.data.prediction);
      }
    } catch (error) {
      console.error("Error fetching weather data or prediction:", error);
    }
  };

  const getWeatherEmoji = (condition) => {
    if (condition.includes("Sunny")) return "☀️";
    if (condition.includes("Rain")) return "🌧️";
    if (condition.includes("Cloud")) return "☁️";
    if (condition.includes("Storm")) return "🌩️";
    return "🌡️";
  };

  const groupByDay = (data) => {
    const groups = {};
    data.forEach(item => {
      const date = new Date(item.recorded_at).toLocaleDateString();
      if (!groups[date]) groups[date] = [];
      groups[date].push(item);
    });
    return groups;
  };

  const computeDailyAverages = (groupedData) => {
    return Object.entries(groupedData).map(([date, entries]) => {
      const avgTemp = entries.reduce((sum, entry) => sum + entry.temperature_c, 0) / entries.length;
      const avgHumidity = entries.reduce((sum, entry) => sum + entry.humidity_percent, 0) / entries.length;
      const avgWind = entries.reduce((sum, entry) => sum + entry.wind_speed_kmh, 0) / entries.length;
      return {
        date,
        avgTemp: avgTemp.toFixed(1),
        avgHumidity: avgHumidity.toFixed(1),
        avgWind: avgWind.toFixed(1)
      };
    });
  };

  const handleLoginSuccess = (credentialResponse) => {
    setUser(credentialResponse);
  };

  const handleLoginError = () => {
    console.error("Login Failed");
  };

  const handleLogout = () => {
    googleLogout();
    setUser(null);
  };

  const containerStyle = {
    padding: 20,
    backgroundColor: darkMode ? '#121212' : '#f5f5f5',
    color: darkMode ? '#fff' : '#000',
    minHeight: '100vh',
    transition: 'background-color 0.3s ease, color 0.3s ease',
    maxWidth: '100%',
    boxSizing: 'border-box'
  };

  const responsiveTableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: 10,
    overflowX: 'auto',
    display: 'block'
  };

  const responsiveDivStyle = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px',
    justifyContent: 'space-around',
    fontSize: '1rem'
  };

  const buttonStyle = {
    marginTop: 10,
    padding: '10px 15px',
    fontSize: '1rem',
    minWidth: '120px'
  };

  return (
    <GoogleOAuthProvider clientId={clientId}>
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

              {user ? (
                <div style={{ marginBottom: 10 }}>
                  <p>Welcome, User!</p>
                  <UIButton onClick={handleLogout} style={buttonStyle}>Logout</UIButton>
                </div>
              ) : (
                <GoogleLogin
                  onSuccess={handleLoginSuccess}
                  onError={handleLoginError}
                />
              )}

              <Input
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Enter location"
              />
              <UIButton onClick={fetchWeather} style={buttonStyle}>Get Weather</UIButton>
              <UIButton onClick={() => setForecastView(forecastView === 'hourly' ? 'daily' : 'hourly')} style={buttonStyle}>
                Switch to {forecastView === 'hourly' ? 'Daily' : 'Hourly'} Forecast
              </UIButton>
              <UIButton onClick={() => setLiveUpdate(!liveUpdate)} style={buttonStyle}>
                {liveUpdate ? "Stop Live Updates" : "Start Live Updates"}
              </UIButton>
            </motion.div>

            {weatherData && weatherData.length > 0 && (
              <motion.div
                style={{ marginTop: 20, overflowX: 'auto' }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <h2 style={{ borderBottom: '1px solid #ccc', paddingBottom: '10px' }}>{weatherData[0].city}, {weatherData[0].country}</h2>
                <h3 style={{ marginTop: 20, marginBottom: 10 }}>
                  {forecastView === 'hourly' ? 'Hourly Forecast' : 'Daily Forecast'}
                </h3>

                <div style={{
                  ...responsiveDivStyle,
                  backgroundColor: darkMode ? '#1e1e1e' : '#e0f7fa',
                  padding: '15px',
                  borderRadius: '12px',
                  marginBottom: '20px',
                }}>
                  <div><strong>🌡️ Temperature:</strong> {weatherData[0].temperature_c}°C</div>
                  <div><strong>💧 Humidity:</strong> {weatherData[0].humidity_percent}%</div>
                  <div><strong>📍 Condition:</strong> {getWeatherEmoji(weatherData[0].weather_condition)} {weatherData[0].weather_condition}</div>
                  <div><strong>🌬️ Wind:</strong> {weatherData[0].wind_speed_kmh} km/h</div>
                  <div><strong>🌫️ Pressure:</strong> {weatherData[0].pressure_hpa} hPa</div>
                  <div><strong>🔆 UV Index:</strong> {weatherData[0].uv_index ?? 'N/A'}</div>
                  <div><strong>🏭 Air Quality:</strong> {weatherData[0].air_quality_index ?? 'N/A'}</div>
                </div>

                {prediction !== null && (
                  <div style={{
                    ...responsiveDivStyle,
                    backgroundColor: darkMode ? '#2e2e2e' : '#d0f0c0',
                    padding: '15px',
                    borderRadius: '12px',
                    marginBottom: '20px',
                    fontWeight: 'bold',
                    fontSize: '1.2rem'
                  }}>
                    AI Model Prediction: {prediction}
                  </div>
                )}

                <h3 style={{ marginTop: 30 }}>📈 Weekly Summary</h3>
                <table style={responsiveTableStyle}>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Avg Temp (°C)</th>
                      <th>Avg Humidity (%)</th>
                      <th>Avg Wind (km/h)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {computeDailyAverages(groupByDay(weatherData)).map((summary, index) => (
                      <tr key={index}>
                        <td>{summary.date}</td>
                        <td>{summary.avgTemp}</td>
                        <td>{summary.avgHumidity}</td>
                        <td>{summary.avgWind}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={weatherData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="recorded_at" tickFormatter={(time) => new Date(time).toLocaleTimeString()} />
                    <YAxis />
                    <Tooltip content={<CustomTooltip darkMode={darkMode} />} />
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
                      <th>UV Index</th>
                      <th>Air Quality</th>
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
                        <td>{getWeatherEmoji(w.weather_condition)} {w.weather_condition}</td>
                        <td>{w.uv_index ?? 'N/A'}</td>
                        <td>{w.air_quality_index ?? 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {forecastView === 'hourly' ? (
                  <>
                    <h3 style={{ marginTop: 30 }}>📆 3-Day Forecast (Hourly Breakdown)</h3>
                    {Object.entries(groupByDay(weatherData)).slice(0, 3).map(([day, data]) => (
                      <div key={day} style={{ marginTop: 20, padding: 10, border: '1px solid #ccc', borderRadius: 10 }}>
                        <h4>{day}</h4>
                        <ResponsiveContainer width="100%" height={200}>
                          <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="recorded_at" tickFormatter={(time) => new Date(time).toLocaleTimeString()} />
                            <YAxis />
                            <Tooltip content={<CustomTooltip darkMode={darkMode} />} />
                            <Legend />
                            <Line type="monotone" dataKey="temperature_c" stroke="#8884d8" name="Temp (°C)" />
                            <Line type="monotone" dataKey="humidity_percent" stroke="#82ca9d" name="Humidity (%)" />
                            <Line type="monotone" dataKey="wind_speed_kmh" stroke="#ffc658" name="Wind (km/h)" />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    ))}
                  </>
                ) : (
                  <>
                    <h3 style={{ marginTop: 30 }}>📆 3-Day Forecast (Daily Averages)</h3>
                    {computeDailyAverages(groupByDay(weatherData)).map((dayData) => (
                      <div key={dayData.date} style={{ marginTop: 20, padding: 10, border: '1px solid #ccc', borderRadius: 10 }}>
                        <h4>{dayData.date}</h4>
                        <p>Average Temperature: {dayData.avgTemp} °C</p>
                        <p>Average Humidity: {dayData.avgHumidity} %</p>
                        <p>Average Wind Speed: {dayData.avgWind} km/h</p>
                      </div>
                    ))}
                  </>
                )}
              </motion.div>
            )}
          </CardContent>
        </Card>
      </div>
    </GoogleOAuthProvider>
  );
}
