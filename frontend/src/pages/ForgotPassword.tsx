import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function ForgotPassword() {
  const { forgotPassword, error: apiError, isLoading, clearError } = useAuth();
  const [email, setEmail] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const validateForm = (): boolean => {
    setValidationError(null);

    if (!email) {
      setValidationError('Please enter your email address.');
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
    setSuccessMessage(null);

    if (!validateForm()) {
      return;
    }

    try {
      await forgotPassword({ email: email.trim() });
      setSuccessMessage(
        'Password reset request submitted. Check the backend server terminal logs for your reset token!'
      );
      setEmail('');
    } catch (err) {
      console.error('Forgot password request failed:', err);
    }
  };

  return (
    <div className="auth-page-container">
      <main className="auth-card" aria-labelledby="forgot-password-heading">
        <header className="auth-header">
          <h1 id="forgot-password-heading">Recover Password</h1>
          <p>Enter your email address to receive your recovery token.</p>
        </header>

        {/* Display validation or API error states */}
        {(validationError || apiError) && (
          <div className="auth-alert error" role="alert" style={{ marginBottom: '20px' }}>
            <span>⚠️</span>
            <p>{validationError || apiError}</p>
          </div>
        )}

        {/* Display success message */}
        {successMessage && (
          <div className="auth-alert info" role="status" style={{ marginBottom: '20px', background: 'rgba(52, 211, 153, 0.1)', border: '1px solid rgba(52, 211, 153, 0.2)', color: 'var(--text-success)' }}>
            <span>✔️</span>
            <p>{successMessage}</p>
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

          <button type="submit" className="auth-btn" disabled={isLoading} style={{ marginTop: '10px' }}>
            {isLoading ? 'Submitting...' : 'Send Reset Link'}
          </button>
        </form>

        <footer className="auth-footer">
          <p>
            <Link to="/login" onClick={clearError}>
              Back to Login
            </Link>
          </p>
        </footer>
      </main>
    </div>
  );
}

export default ForgotPassword;
