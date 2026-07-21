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
    } catch (err) {
      console.error('Login submit failed:', err);
    }
  };

  return (
    <div className="auth-page-container">
      <main className="auth-card" aria-labelledby="login-heading">
        <header className="auth-header">
          <h1 id="login-heading">Welcome Back</h1>
          <p>Sign in to access your study assistant.</p>
        </header>

        {/* Display validation or API error states */}
        {(validationError || apiError) && (
          <div className="auth-alert error" role="alert" style={{ marginBottom: '20px' }}>
            <span>⚠️</span>
            <p>{validationError || apiError}</p>
          </div>
        )}

        {/* Display info messages e.g. successful registration redirects */}
        {infoMessage && (
          <div className="auth-alert info" role="status" style={{ marginBottom: '20px' }}>
            <span>ℹ️</span>
            <p>{infoMessage}</p>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              placeholder="name@example.com"
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

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
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

          <button type="submit" className="auth-btn" disabled={isLoading} style={{ marginTop: '10px' }}>
            {isLoading ? 'Logging in...' : 'Log In'}
          </button>
        </form>

        <footer className="auth-footer">
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
      </main>
    </div>
  );
}

export default Login;
