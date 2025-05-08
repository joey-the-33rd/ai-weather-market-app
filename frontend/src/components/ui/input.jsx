import React from 'react';

export function Input(props) {
  return (
    <input
      {...props}
      style={{
        padding: '10px',
        fontSize: '1rem',
        borderRadius: '6px',
        border: '1px solid #ccc',
        width: '100%',
        boxSizing: 'border-box',
        marginBottom: '10px'
      }}
    />
  );
}
