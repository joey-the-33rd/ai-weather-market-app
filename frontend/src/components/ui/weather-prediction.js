import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

/**
 * A React component that fetches an AI predicted temperature from the server and displays it.
 *
 * The component renders an ActivityIndicator until the data is loaded.
 *
 * @returns {React.ReactElement} The component to be rendered.
 */
export default function WeatherPrediction() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:5001/api/predict") // Replace with your deployed URL
      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          setPrediction(data.predicted_temperature_c);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <ActivityIndicator size="large" color="#00bfff" />;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🌤 AI Predicted Temperature</Text>
      <Text style={styles.temp}>{prediction}°C</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingTop: 60,
    alignItems: 'center',
  },
  title: {
    fontSize: 22,
    fontWeight: '600',
    marginBottom: 20,
  },
  temp: {
    fontSize: 40,
    color: '#ff8c00',
  },
});
