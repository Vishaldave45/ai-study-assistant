import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Shield, Sparkles } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();

  if (!user) return null;

  // Extract first name for the personal greeting
  const firstName = user.full_name.split(' ')[0];

  return (
    <div className="flex-center" style={{ width: '100%', minHeight: '60vh', padding: '1rem' }}>
      {/* Central Welcome Card */}
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '560px',
          background: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: 'var(--radius-lg)',
          boxShadow: '0 8px 30px rgba(15, 23, 42, 0.03)',
          padding: '3rem 2rem 2.5rem',
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Floating sparkles background decor */}
        <div
          style={{
            position: 'absolute',
            top: '2.5rem',
            right: '2.5rem',
            color: '#c7d2fe', // Indigo 200
          }}
        >
          <Sparkles size={56} strokeWidth={1} />
        </div>

        {/* Green Shield Check Icon */}
        <div
          className="flex-center"
          style={{
            width: '4.5rem',
            height: '4.5rem',
            borderRadius: 'var(--radius-full)',
            background: '#d1fae5', // Emerald 100
            color: '#10b981', // Emerald 500
            margin: '0 auto 1.5rem',
            border: '2px solid #a7f3d0',
          }}
        >
          <Shield size={36} fill="#10b981" stroke="#d1fae5" strokeWidth={1.5} />
        </div>

        {/* Greetings header */}
        <h2
          style={{
            fontSize: '1.85rem',
            fontWeight: 700,
            color: '#0f172a',
            marginBottom: '0.75rem',
          }}
        >
          Welcome, {firstName}
        </h2>

        {/* Session Status Pill */}
        <div
          className="flex-center"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: '#eff6ff',
            color: '#1e40af',
            fontSize: '0.8rem',
            fontWeight: 600,
            padding: '0.4rem 1.15rem',
            borderRadius: 'var(--radius-full)',
            marginBottom: '2.5rem',
          }}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#10b981', // Solid Green Dot
              display: 'inline-block',
            }}
          ></span>
          <span>Your session is active.</span>
        </div>

        {/* Inner Columns for Identity and Node */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '1rem',
            textAlign: 'left',
          }}
        >
          {/* Identity Column Box */}
          <div
            style={{
              border: '1px solid #e2e8f0',
              borderRadius: 'var(--radius-md)',
              padding: '1.15rem 1rem',
              background: '#f8fafc',
            }}
          >
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.68rem',
                fontWeight: 700,
                letterSpacing: '0.08em',
                color: '#6366f1',
                display: 'block',
                marginBottom: '0.25rem',
              }}
            >
              IDENTITY VERIFIED
            </span>
            <span
              style={{
                fontSize: '0.9rem',
                fontWeight: 700,
                color: '#0f172a',
              }}
            >
              {user.full_name}
            </span>
          </div>

          {/* Account Node Box */}
          <div
            style={{
              border: '1px solid #e2e8f0',
              borderRadius: 'var(--radius-md)',
              padding: '1.15rem 1rem',
              background: '#f8fafc',
            }}
          >
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.68rem',
                fontWeight: 700,
                letterSpacing: '0.08em',
                color: '#6366f1',
                display: 'block',
                marginBottom: '0.25rem',
              }}
            >
              ACCOUNT NODE
            </span>
            <span
              style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: '#0f172a',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: 'block',
              }}
              title={user.email}
            >
              {user.email}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
