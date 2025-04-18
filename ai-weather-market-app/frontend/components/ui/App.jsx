import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import axios from 'axios';

export default function App() {
  const [city, setCity] = useState('');
  const [weather, setWeather] = useState(null);

  const fetchWeather = async () => {
    try {
      const response = await axios.get(`http://your-backend-url/weather?city=${city}`);
      setWeather(response.data);
    } catch (error) {
      console.error("Error fetching weather:", error);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Weather Prediction</Text>
      <TextInput style={styles.input} placeholder="Enter city" onChangeText={setCity} />
      <Button title="Get Weather" onPress={fetchWeather} />
      {weather && (
        <View style={styles.result}>
          <Text>Temperature: {weather.temperature}°C</Text>
          <Text>Humidity: {weather.humidity}%</Text>
          <Text>Condition: {weather.weather}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center' },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 10 },
  input: { height: 40, borderColor: 'gray', borderWidth: 1, marginBottom: 10, padding: 8 },
  result: { marginTop: 20, padding: 10, backgroundColor: '#f0f0f0' }
});
