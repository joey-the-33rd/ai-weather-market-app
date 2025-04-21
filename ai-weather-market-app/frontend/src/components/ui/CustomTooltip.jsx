// src/components/CustomTooltip.jsx
import React from 'react';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div style={{
        backgroundColor: '#fff',
        padding: '10px',
        border: '1px solid #ccc',
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
