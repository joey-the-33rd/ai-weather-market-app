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
              <div style={{ marginTop: 20 }}>
                <p>Temperature: {weatherData[0].temperature_c} °C</p>
                <p>Humidity: {weatherData[0].humidity_percent} %</p>
                <p>Condition: {weatherData[0].weather_condition}</p>
              </div>
)}

        </CardContent>
      </Card>
    </div>
  );
}
