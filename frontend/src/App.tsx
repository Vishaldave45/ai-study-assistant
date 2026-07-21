import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './hooks/useAuth';
import ProtectedRoute from './routes/ProtectedRoute';
import GuestRoute from './routes/GuestRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Heading from './components/Heading';
import Card from './components/Card';

/**
 * Placeholder Dashboard component.
 * Displays logged-in user profile attributes and trigger logout.
 */
function Dashboard() {
  const { user, logout, isLoading } = useAuth();

  return (
    <main style={{ padding: '40px' }} aria-labelledby="dashboard-heading">
      <Card>
        <header>
          <Heading title="📚 AI Study Assistant Dashboard" />
          <h2 id="dashboard-heading">Welcome, {user?.full_name}!</h2>
        </header>

        <section>
          <h3>Profile Overview</h3>
          <ul>
            <li><strong>Email:</strong> {user?.email}</li>
            <li><strong>Status:</strong> {user?.status}</li>
            <li><strong>Verified:</strong> {user?.is_verified ? 'Yes' : 'No'}</li>
            <li><strong>Account ID:</strong> {user?.id}</li>
          </ul>
        </section>

        <footer>
          <button onClick={logout} disabled={isLoading}>
            {isLoading ? 'Logging out...' : 'Log Out'}
          </button>
        </footer>
      </Card>
    </main>
  );
}

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Guest-only Routes */}
          <Route element={<GuestRoute />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
          </Route>

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Dashboard />} />
          </Route>

          {/* Fallback Redirection */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
