import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function Register() {
  const { register, error: apiError, isLoading, clearError } = useAuth();
  const navigate = useNavigate();

  // Form states
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Local validation states
  const [validationError, setValidationError] = useState<string | null>(null);

  const validateForm = (): boolean => {
    setValidationError(null);

    // Empty fields check
    if (!fullName || !email || !password || !confirmPassword) {
      setValidationError('All fields are required.');
      return false;
    }

    // Email structure check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setValidationError('Please enter a valid email address.');
      return false;
    }

    // Password length constraint check (minimum 8 characters as per standard security)
    if (password.length < 8) {
      setValidationError('Password must be at least 8 characters long.');
      return false;
    }

    // Passwords match check
    if (password !== confirmPassword) {
      setValidationError('Passwords do not match.');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    clearError();

    if (!validateForm()) {
      return;
    }

    try {
      await register({
        email: email.trim(),
        full_name: fullName.trim(),
        password,
      });

      // Redirect to Login page with a success message state
      navigate('/login', {
        state: { message: 'Registration successful! Please log in with your credentials.' },
      });
    } catch (err) {
      console.error('Registration failed:', err);
    }
  };

  return (
    <div className="auth-page-container">
      <main className="auth-card" aria-labelledby="register-heading">
        <header className="auth-header">
          <h1 id="register-heading">Create Account</h1>
          <p>Sign up to start parsing study materials.</p>
        </header>

        {/* Display validation or API error states */}
        {(validationError || apiError) && (
          <div className="auth-alert error" role="alert" style={{ marginBottom: '20px' }}>
            <span>⚠️</span>
            <p>{validationError || apiError}</p>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="full-name">Full Name</label>
            <input
              id="full-name"
              type="text"
              placeholder="John Doe"
              value={fullName}
              onChange={(e) => {
                setFullName(e.target.value);
                if (validationError) setValidationError(null);
              }}
              disabled={isLoading}
              required
              autoComplete="name"
            />
          </div>

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
            <label htmlFor="password">Password (Min 8 chars)</label>
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
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirm-password">Confirm Password</label>
            <input
              id="confirm-password"
              type="password"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                if (validationError) setValidationError(null);
              }}
              disabled={isLoading}
              required
              autoComplete="new-password"
            />
          </div>

          <button type="submit" className="auth-btn" disabled={isLoading} style={{ marginTop: '10px' }}>
            {isLoading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>

        <footer className="auth-footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" onClick={clearError}>
              Log in here
            </Link>
          </p>
        </footer>
      </main>
    </div>
  );
}

export default Register;
