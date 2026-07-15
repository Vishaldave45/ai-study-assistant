import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LogOut, BookOpen } from 'lucide-react';

export const DashboardLayout: React.FC = () => {
  const { user, logout } = useAuth();

  const getInitials = (name?: string) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map((part) => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#f8fafc' }}>
      {/* Top Navbar */}
      <header
        style={{
          background: '#ffffff',
          borderBottom: '1px solid #e2e8f0',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <div
          className="container"
          style={{
            height: '4.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          {/* Logo (Left) */}
          <Link
            to="/dashboard"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              color: '#3730a3', // Indigo-800 matching mockup
              fontWeight: 700,
              fontSize: '1.25rem',
              fontFamily: 'var(--font-display)',
            }}
          >
            <BookOpen size={22} strokeWidth={2.5} />
            <span>AI Study Assistant</span>
          </Link>

          {/* User Profile & Actions (Right) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {user && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a', lineHeight: '1.2' }}>
                    {user.full_name}
                  </p>
                  <p style={{ fontSize: '0.75rem', color: '#64748b' }}>
                    {user.email}
                  </p>
                </div>

                {/* Avatar Icon */}
                <div
                  className="flex-center"
                  style={{
                    width: '2.5rem',
                    height: '2.5rem',
                    borderRadius: 'var(--radius-full)',
                    background: '#e0f2fe',
                    border: '1px solid #bae6fd',
                    fontSize: '0.85rem',
                    fontWeight: 700,
                    color: '#0369a1',
                    fontFamily: 'var(--font-mono)',
                  }}
                >
                  {getInitials(user.full_name)}
                </div>
              </div>
            )}

            <button
              onClick={() => logout()}
              className="btn"
              style={{
                background: '#ffffff',
                color: '#0f172a',
                border: '1px solid #d1d5db',
                padding: '0.5rem 0.85rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                borderRadius: 'var(--radius-md)',
                boxShadow: 'none',
              }}
            >
              <LogOut size={14} style={{ marginRight: '0.25rem' }} />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '3.5rem 0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="container" style={{ width: '100%' }}>
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <footer
        style={{
          padding: '1.5rem 0',
          textAlign: 'center',
          color: '#94a3b8',
          fontSize: '0.8rem',
          background: 'transparent',
        }}
      >
        <div className="container">
          <p>AI Study Assistant — Precision Minimalism Interface</p>
        </div>
      </footer>
    </div>
  );
};

export default DashboardLayout;
