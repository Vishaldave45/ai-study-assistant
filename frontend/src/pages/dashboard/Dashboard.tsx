import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { ShieldCheck, ShieldAlert, Award, BookOpen, Clock, Settings } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Welcome banner */}
      <div
        className="glass-panel"
        style={{
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1.5rem',
          padding: '2.5rem',
        }}
      >
        <div>
          <h2 style={{ fontSize: '2.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Welcome back,{' '}
            <span
              style={{
                background: 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              {user.full_name}
            </span>
            !
          </h2>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '1rem', maxWidth: '600px' }}>
            Ready to continue your learning journey? Access your workspace, study materials, and AI study buddies below.
          </p>
        </div>
        <div
          className="flex-center"
          style={{
            width: '4rem',
            height: '4rem',
            borderRadius: 'var(--radius-lg)',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--glass-border)',
            color: 'var(--color-secondary)',
          }}
        >
          <Award size={36} />
        </div>
      </div>

      {/* Main Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.5rem',
        }}
      >
        {/* Profile Details Card */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3>Account Security</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingBottom: '0.75rem',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
              }}
            >
              <span style={{ color: 'var(--color-text-secondary)' }}>Full Name</span>
              <span style={{ fontWeight: 600 }}>{user.full_name}</span>
            </div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingBottom: '0.75rem',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
              }}
            >
              <span style={{ color: 'var(--color-text-secondary)' }}>Email</span>
              <span style={{ fontWeight: 600 }}>{user.email}</span>
            </div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingBottom: '0.75rem',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
              }}
            >
              <span style={{ color: 'var(--color-text-secondary)' }}>Status</span>
              <span
                style={{
                  fontWeight: 600,
                  textTransform: 'capitalize',
                  color: user.status === 'active' ? 'var(--color-success)' : 'var(--color-warning)',
                }}
              >
                {user.status}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>Verification Status</span>
              {user.verified ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--color-success)', fontWeight: 600 }}>
                  <ShieldCheck size={18} />
                  <span>Verified</span>
                </div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--color-warning)', fontWeight: 600 }}>
                  <ShieldAlert size={18} />
                  <span>Pending</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Study Stats Card */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3>Study Progress</h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '1rem',
              height: '100%',
              alignContent: 'center',
            }}
          >
            <div
              style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--glass-border)',
                padding: '1.25rem',
                borderRadius: 'var(--radius-md)',
                textAlign: 'center',
              }}
            >
              <BookOpen size={24} color="var(--color-primary)" style={{ margin: '0 auto 0.5rem' }} />
              <h4 style={{ fontSize: '1.5rem', fontWeight: 700 }}>0</h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>Workspaces</p>
            </div>
            <div
              style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--glass-border)',
                padding: '1.25rem',
                borderRadius: 'var(--radius-md)',
                textAlign: 'center',
              }}
            >
              <Clock size={24} color="var(--color-secondary)" style={{ margin: '0 auto 0.5rem' }} />
              <h4 style={{ fontSize: '1.5rem', fontWeight: 700 }}>0h</h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>Study Time</p>
            </div>
          </div>
        </div>

        {/* Quick Actions Card */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3>Quick Links</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <button
              onClick={() => alert('Workspaces feature is coming soon!')}
              className="btn btn-secondary"
              style={{ justifyContent: 'flex-start', padding: '0.85rem 1.25rem', width: '100%' }}
            >
              <BookOpen size={18} />
              <span>Create New Workspace</span>
            </button>
            <button
              onClick={() => alert('Settings feature is coming soon!')}
              className="btn btn-secondary"
              style={{ justifyContent: 'flex-start', padding: '0.85rem 1.25rem', width: '100%' }}
            >
              <Settings size={18} />
              <span>Account Settings</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
