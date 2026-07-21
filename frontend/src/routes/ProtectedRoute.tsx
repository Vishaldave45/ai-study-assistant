import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * Route guard that requires users to be authenticated.
 * Renders nested routes (Outlet) if authenticated, otherwise redirects to /login.
 */
export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <main style={{ padding: '40px', textAlign: 'center' }} aria-busy="true" aria-live="polite">
        <p>Loading session...</p>
      </main>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

export default ProtectedRoute;
