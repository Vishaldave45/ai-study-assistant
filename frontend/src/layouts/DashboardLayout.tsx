import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LogOut, User as UserIcon, BookOpen } from 'lucide-react';

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
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar */}
      <header
        style={{
          background: 'rgba(11, 15, 25, 0.7)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          borderBottom: '1px solid var(--glass-border)',
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
          {/* Logo */}
          <Link
            to="/dashboard"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              color: 'var(--color-text-primary)',
              fontWeight: 700,
              fontSize: '1.25rem',
              fontFamily: 'var(--font-display)',
            }}
          >
            <div
              className="flex-center"
              style={{
                width: '2.5rem',
                height: '2.5rem',
                borderRadius: 'var(--radius-md)',
                background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%)',
              }}
            >
              <BookOpen size={20} color="#fff" />
            </div>
            <span>Antigravity</span>
          </Link>

          {/* User Section */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            {user && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ textAlign: 'right', display: 'none', md: 'block' } as any}>
                  <p style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                    {user.full_name}
                  </p>
                  <p style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                    {user.email}
                  </p>
                </div>

                {/* Avatar */}
                <div
                  className="flex-center"
                  style={{
                    width: '2.5rem',
                    height: '2.5rem',
                    borderRadius: 'var(--radius-full)',
                    background: 'rgba(255,255,255,0.08)',
                    border: '1px solid var(--glass-border)',
                    fontSize: '0.9rem',
                    fontWeight: 600,
                    color: 'var(--color-primary)',
                    fontFamily: 'var(--font-display)',
                  }}
                  title={`${user.full_name} (${user.email})`}
                >
                  {getInitials(user.full_name)}
                </div>
              </div>
            )}

            <button
              onClick={() => logout()}
              className="btn btn-secondary"
              style={{ padding: '0.5rem 0.8rem', fontSize: '0.85rem' }}
              title="Logout"
            >
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '2.5rem 0', position: 'relative' }}>
        <div className="container">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <footer
        style={{
          borderTop: '1px solid var(--glass-border)',
          padding: '1.5rem 0',
          textAlign: 'center',
          color: 'var(--color-text-muted)',
          fontSize: '0.85rem',
          background: 'rgba(3, 7, 18, 0.5)',
        }}
      >
        <div className="container">
          <p>© {new Date().getFullYear()} Antigravity. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};
export default DashboardLayout;
