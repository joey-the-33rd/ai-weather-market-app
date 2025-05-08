import React from 'react';

export function Card({ children }) {
  return (
    <div style={{
      backgroundColor: '#fff',
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      padding: '20px',
      marginBottom: '20px',
      boxSizing: 'border-box'
    }}>
      {children}
    </div>
  );
}

export function CardContent({ children }) {
  return (
    <div style={{ padding: '10px' }}>
      {children}
    </div>
  );
}
