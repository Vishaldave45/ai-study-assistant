import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * Route guard that requires users to NOT be authenticated.
 * Renders nested routes (Outlet) if unauthenticated, otherwise redirects to / (dashboard).
 */
export function GuestRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <main style={{ padding: '40px', textAlign: 'center' }} aria-busy="true" aria-live="polite">
        <p>Loading session...</p>
      </main>
    );
  }

  return !isAuthenticated ? <Outlet /> : <Navigate to="/" replace />;
}

export default GuestRoute;
