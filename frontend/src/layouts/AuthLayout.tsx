import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const AuthLayout: React.FC = () => {
  const { authenticated, loading } = useAuth();

  // If already authenticated and not loading, bypass login/register and go straight to dashboard
  if (!loading && authenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div
      className="flex-center"
      style={{
        minHeight: '100vh',
        width: '100vw',
        position: 'relative',
        overflow: 'hidden',
        padding: '2rem 1.5rem',
      }}
    >
      {/* Decorative Blur Orbs */}
      <div
        style={{
          position: 'absolute',
          top: '25%',
          left: '20%',
          width: '300px',
          height: '300px',
          background: 'rgba(99, 102, 241, 0.15)',
          borderRadius: '50%',
          filter: 'blur(80px)',
          zIndex: 0,
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '25%',
          right: '20%',
          width: '350px',
          height: '350px',
          background: 'rgba(168, 85, 247, 0.15)',
          borderRadius: '50%',
          filter: 'blur(100px)',
          zIndex: 0,
        }}
      />

      <div style={{ position: 'relative', zIndex: 1, width: '100%', maxWidth: '440px' }}>
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            <span style={{ background: 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Antigravity
            </span>
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.95rem' }}>
            Your Intelligent AI Study Companion
          </p>
        </div>

        {/* Content Panel */}
        <div className="glass-panel" style={{ padding: '2.5rem 2rem' }}>
          <Outlet />
        </div>
      </div>
    </div>
  );
};
export default AuthLayout;
