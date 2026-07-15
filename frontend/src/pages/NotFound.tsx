import React from 'react';
import { Link } from 'react-router-dom';

export const NotFound: React.FC = () => {
  return (
    <div
      className="flex-center"
      style={{
        minHeight: '80vh',
        flexDirection: 'column',
        gap: '1.5rem',
        textAlign: 'center',
        padding: '2rem',
      }}
    >
      <h1
        style={{
          fontSize: '8rem',
          fontWeight: 800,
          background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          lineHeight: 1,
        }}
      >
        404
      </h1>
      <h2 style={{ fontSize: '2rem', fontWeight: 600 }}>Page Not Found</h2>
      <p style={{ color: 'var(--color-text-secondary)', maxWidth: '460px', fontSize: '1rem', lineHeight: '1.6' }}>
        The page you are looking for does not exist or has been moved. Let's get you back on track.
      </p>
      <Link to="/" className="btn btn-primary" style={{ marginTop: '1rem' }}>
        Return Home
      </Link>
    </div>
  );
};
export default NotFound;
