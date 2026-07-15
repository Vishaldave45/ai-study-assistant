import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const AuthLayout: React.FC = () => {
  const { authenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex-center" style={{ minHeight: '100vh', flexDirection: 'column', gap: '1rem' }}>
        <div className="spinner" style={{ width: '2.5rem', height: '2.5rem', borderWidth: '3px', color: 'var(--color-primary)' }}></div>
        <p style={{ color: 'var(--color-text-secondary)', fontFamily: 'var(--font-display)', fontSize: '1.1rem' }}>
          Checking Session...
        </p>
      </div>
    );
  }

  if (authenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div
      className="flex-center"
      style={{
        minHeight: '100vh',
        width: '100vw',
        padding: '2rem 1.5rem',
        flexDirection: 'column',
      }}
    >
      <Outlet />
    </div>
  );
};

export default AuthLayout;
