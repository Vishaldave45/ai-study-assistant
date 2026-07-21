import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface LocationState {
  message?: string;
}

export function Login() {
  const { login, error: apiError, isLoading, clearError } = useAuth();
  const location = useLocation();

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Validation states
  const [validationError, setValidationError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);

  // Retrieve info message passed from Register redirects safely without "any"
  useEffect(() => {
    const state = location.state as LocationState | null;
    if (state?.message) {
      setInfoMessage(state.message);
    }
  }, [location.state]);

  const validateForm = (): boolean => {
    setValidationError(null);

    if (!email || !password) {
      setValidationError('Please enter both your email and password.');
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setValidationError('Please enter a valid email address.');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    clearError();
    setInfoMessage(null);

    if (!validateForm()) {
      return;
    }

    try {
      await login({
        email: email.trim(),
        password,
      });
      // AuthProvider automatically updates state, triggering ProtectedRoute redirect
    } catch (err) {
      console.error('Login submit failed:', err);
    }
  };

  return (
    <main aria-labelledby="login-heading">
      <section>
        <h1 id="login-heading">Welcome Back</h1>
        <p>Log in to access your study assistant.</p>

        {/* Display validation or API error states */}
        {(validationError || apiError) && (
          <div role="alert" style={{ color: 'red', margin: '15px 0' }}>
            <p>{validationError || apiError}</p>
          </div>
        )}

        {/* Display info messages e.g. successful registration redirects */}
        {infoMessage && (
          <div role="status" style={{ color: 'blue', margin: '15px 0' }}>
            <p>{infoMessage}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div>
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (validationError) setValidationError(null);
              }}
              disabled={isLoading}
              required
              autoComplete="email"
            />
          </div>

          <div>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (validationError) setValidationError(null);
              }}
              disabled={isLoading}
              required
              autoComplete="current-password"
            />
          </div>

          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Log In'}
          </button>
        </form>

        <footer>
          <p>
            <Link to="/forgot-password" onClick={clearError}>
              Forgot password?
            </Link>
          </p>
          <p>
            Don't have an account?{' '}
            <Link to="/register" onClick={clearError}>
              Sign up here
            </Link>
          </p>
        </footer>
      </section>
    </main>
  );
}

export default Login;
