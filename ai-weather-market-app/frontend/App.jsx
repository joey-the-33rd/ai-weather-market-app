import React, { useState } from "react";
import { View, Text, TextInput, Button, StyleSheet } from "react-native";
import axios from "axios";
import { Card, CardContent } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Button as UIButton } from "./components/ui/button";

// Your existing App component code here, updated with correct import paths

export default function App() {
  const [location, setLocation] = useState("");
  const [weatherData, setWeatherData] = useState(null);

  const fetchWeather = async () => {
    try {
      const response = await axios.get(`/api/weather?location=${location}`);
      setWeatherData(response.data);
    } catch (error) {
      console.error("Error fetching weather data:", error);
    }
  };

  return (
    <View style={styles.container}>
      <Card>
        <CardContent>
          <Text style={styles.title}>Weather App</Text>
          <Input
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter location"
          />
          <UIButton onClick={fetchWeather}>Get Weather</UIButton>
          {weatherData && (
            <View style={styles.results}>
              <Text>Temperature: {weatherData.temperature_c} °C</Text>
              <Text>Humidity: {weatherData.humidity_percent} %</Text>
              <Text>Condition: {weatherData.weather_condition}</Text>
            </View>
          )}
        </CardContent>
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    marginBottom: 10,
  },
  results: {
    marginTop: 20,
  },
});
