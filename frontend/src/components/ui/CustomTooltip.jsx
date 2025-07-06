// src/components/CustomTooltip.jsx
import React from 'react';

const CustomTooltip = ({ active, payload, label, darkMode }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div style={{
        backgroundColor: darkMode ? '#333' : '#fff',
        color: darkMode ? '#fff' : '#000',
        padding: '10px',
        border: '1px solid',
        borderColor: darkMode ? '#555' : '#ccc',
        borderRadius: '5px'
      }}>
        <p><strong>{new Date(label).toLocaleString()}</strong></p>
        <p>🌡️ Temp: {data.temperature_c}°C</p>
        <p>💧 Humidity: {data.humidity_percent}%</p>
        <p>🌬️ Wind: {data.wind_speed_kmh} km/h</p>
        <p>🌫️ Pressure: {data.pressure_hpa} hPa</p>
        <p>🔆 UV Index: {data.uv_index ?? 'N/A'}</p>
        <p>🏭 Air Quality: {data.air_quality_index ?? 'N/A'}</p>
      </div>
    );
  }
  return null;
};

export default CustomTooltip;
