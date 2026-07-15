import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BookOpen, FileX, ArrowRight, CornerUpLeft } from 'lucide-react';

export const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: '#f8fafc',
        fontFamily: 'var(--font-sans)',
      }}
    >
      {/* 404 Header (Matching mockup) */}
      <header
        style={{
          background: '#ffffff',
          borderBottom: '1px solid #e2e8f0',
          height: '4.5rem',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <div className="container" style={{ width: '100%' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              color: '#3730a3',
              fontWeight: 700,
              fontSize: '1.25rem',
              fontFamily: 'var(--font-display)',
            }}
          >
            <BookOpen size={22} strokeWidth={2.5} />
            <span>AI Study Assistant</span>
          </div>
        </div>
      </header>

      {/* Main 404 Body */}
      <main
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          padding: '2rem 1.5rem',
          position: 'relative',
        }}
      >
        {/* Large Faded '404' Text Backdrop */}
        <div
          style={{
            position: 'absolute',
            fontSize: '14rem',
            fontWeight: 800,
            color: '#f1f5f9',
            zIndex: 0,
            userSelect: 'none',
            fontFamily: 'var(--font-display)',
            top: '40%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
          }}
        >
          404
        </div>

        {/* Card Content (Relative above backdrop) */}
        <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {/* Document Graphic Panel */}
          <div
            className="flex-center"
            style={{
              width: '5.5rem',
              height: '7rem',
              background: '#ffffff',
              border: '1.5px dashed #cbd5e1',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-primary)',
              marginBottom: '2rem',
              boxShadow: '0 4px 12px rgba(15, 23, 42, 0.01)',
              position: 'relative',
            }}
          >
            <FileX size={36} strokeWidth={1.5} />
            {/* Corner fold simulation */}
            <div
              style={{
                position: 'absolute',
                top: -1,
                right: -1,
                width: '1.25rem',
                height: '1.25rem',
                borderLeft: '1.5px dashed #cbd5e1',
                borderBottom: '1.5px dashed #cbd5e1',
                background: '#f8fafc',
                borderTopRightRadius: 'var(--radius-md)',
              }}
            ></div>
          </div>

          {/* Heading */}
          <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.75rem' }}>
            Page not found.
          </h2>

          {/* Description */}
          <p
            style={{
              color: '#475569',
              maxWidth: '500px',
              fontSize: '0.92rem',
              lineHeight: '1.6',
              marginBottom: '2rem',
            }}
          >
            The requested lesson, resource, or module seems to have moved or disappeared. Let's get you back to your learning path.
          </p>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '2.5rem' }}>
            <Link to="/login" className="btn btn-primary" style={{ padding: '0.7rem 1.35rem', fontSize: '0.88rem' }}>
              <span>Go to Login</span>
              <ArrowRight size={15} />
            </Link>

            <button
              onClick={() => navigate(-1)}
              className="btn btn-secondary"
              style={{ padding: '0.7rem 1.35rem', fontSize: '0.88rem', fontWeight: 600, border: '1px solid #d1d5db' }}
            >
              <CornerUpLeft size={15} style={{ marginRight: '0.25rem' }} />
              <span>Go Back</span>
            </button>
          </div>

          {/* Monospace debug pill */}
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.68rem',
              letterSpacing: '0.05em',
              background: '#f1f5f9',
              border: '1px solid #e2e8f0',
              padding: '0.45rem 1.25rem',
              borderRadius: 'var(--radius-full)',
              color: '#64748b',
              fontWeight: 600,
            }}
          >
            ERRORCODE: 404_NULL_REFERENCE | TRACE_ID: 99x-AI-STU-404
          </div>
        </div>
      </main>

      {/* 404 Footer */}
      <footer
        style={{
          borderTop: '1px solid #e2e8f0',
          padding: '1.5rem 0',
          fontSize: '0.78rem',
          color: '#94a3b8',
          background: '#ffffff',
        }}
      >
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>© 2026 AI Study Assistant</span>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <a href="#" style={{ color: '#94a3b8' }}>Support</a>
              <a href="#" style={{ color: '#94a3b8' }}>Documentation</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default NotFound;
