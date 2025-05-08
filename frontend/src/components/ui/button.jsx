import React from 'react';

export function Button(props) {
  return (
    <button
      {...props}
      style={{
        padding: '10px 15px',
        fontSize: '1rem',
        borderRadius: '6px',
        border: 'none',
        backgroundColor: '#007bff',
        color: '#fff',
        cursor: 'pointer',
        minWidth: '120px',
        marginBottom: '10px'
      }}
    />
  );
}
