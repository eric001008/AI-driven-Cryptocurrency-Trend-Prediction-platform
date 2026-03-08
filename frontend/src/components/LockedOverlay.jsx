// src/components/LockedOverlay.jsx
import React from 'react';

export default function LockedOverlay({ children }) {
  return (
    <div style={{ position: 'relative' }}>
      {children}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backdropFilter: 'blur(6px)',
          WebkitBackdropFilter: 'blur(6px)',
          backgroundColor: 'rgba(0,0,0,0.3)',
          color: '#fff',
          fontSize: '1.2rem',
          fontWeight: 'bold',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          borderRadius: '8px',
          zIndex: 10,
          textAlign: 'center',
          padding: '0 10px',
        }}
      >
        Please register to access this content
      </div>
    </div>
  );
}
