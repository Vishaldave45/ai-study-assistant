import { memo } from 'react';

export const PageLoader = memo(function PageLoader() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '200px',
        color: '#94a3b8',
      }}
    >
      <div
        style={{
          width: '32px',
          height: '32px',
          border: '3px solid #6366f1',
          borderTopColor: 'transparent',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
          marginBottom: '12px',
        }}
      />
      <p style={{ fontSize: '0.9rem' }}>Loading workspace components...</p>
    </div>
  );
});

export default PageLoader;
