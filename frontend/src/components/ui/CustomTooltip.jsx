import React from 'react';

export default function CustomTooltip({ active, payload, label, darkMode }) {
  if (active && payload && payload.length) {
    return (
      <div style={{
        backgroundColor: darkMode ? '#333' : '#fff',
        color: darkMode ? '#fff' : '#000',
        padding: '10px',
        borderRadius: '6px',
        boxShadow: '0 0 5px rgba(0,0,0,0.3)'
      }}>
        <p>{label}</p>
        {payload.map((entry, index) => (
          <p key={`item-${index}`} style={{ margin: 0 }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }

  return null;
}
