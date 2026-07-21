import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function ResetPassword() {
  const { resetPassword, error: apiError, isLoading, clearError } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // Retrieve token from search query param (?token=xyz)
  const tokenFromUrl = searchParams.get('token') || '';

  // Form states
  const [token, setToken] = useState(tokenFromUrl);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Validation states
  const [validationError, setValidationError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Sync token state if URL parameter changes
  useEffect(() => {
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    }
  }, [tokenFromUrl]);

  const validateForm = (): boolean => {
    setValidationError(null);

    if (!token) {
      setValidationError('A reset token is required. Please check your recovery URL or paste the token.');
      return false;
    }

    if (!password || !confirmPassword) {
      setValidationError('Please fill in both password fields.');
      return false;
    }

    if (password.length < 8) {
      setValidationError('Password must be at least 8 characters long.');
      return false;
    }

    if (password !== confirmPassword) {
      setValidationError('Passwords do not match.');
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
      await resetPassword({
        token: token.trim(),
        password,
      });

      setSuccessMessage('Password has been reset successfully! Redirecting to login...');
      setToken('');
      setPassword('');
      setConfirmPassword('');

      // Redirect to login page after 2 seconds
      setTimeout(() => {
        navigate('/login', { state: { message: 'Password reset successful. Please log in with your new password.' } });
      }, 2000);
    } catch (err) {
      console.error('Password reset failed:', err);
    }
  };

  return (
    <div className="auth-page-container">
      <main className="auth-card" aria-labelledby="reset-password-heading">
        <header className="auth-header">
          <h1 id="reset-password-heading">Reset Password</h1>
          <p>Set a secure new password for your account.</p>
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
            <label htmlFor="token">Reset Token</label>
            <input
              id="token"
              type="text"
              value={token}
              onChange={(e) => {
                setToken(e.target.value);
                if (validationError) setValidationError(null);
              }}
              disabled={isLoading || !!tokenFromUrl}
              required
              placeholder="Paste token here if not in URL"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">New Password (Min 8 characters)</label>
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
            <label htmlFor="confirm-password">Confirm New Password</label>
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
            {isLoading ? 'Resetting...' : 'Update Password'}
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

export default ResetPassword;
