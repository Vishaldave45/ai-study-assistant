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
    <main aria-labelledby="reset-password-heading">
      <section>
        <h1 id="reset-password-heading">Reset Password</h1>
        <p>Set a new password for your account.</p>

        {/* Display validation or API error states */}
        {(validationError || apiError) && (
          <div role="alert" style={{ color: 'red', margin: '15px 0' }}>
            <p>{validationError || apiError}</p>
          </div>
        )}

        {/* Display success message */}
        {successMessage && (
          <div role="status" style={{ color: 'green', margin: '15px 0' }}>
            <p>{successMessage}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div>
            <label htmlFor="token">Reset Token</label>
            <input
              id="token"
              type="text"
              value={token}
              onChange={(e) => {
                setToken(e.target.value);
                if (validationError) setValidationError(null);
              }}
              disabled={isLoading || !!tokenFromUrl} // Lock field if token is supplied via URL query
              required
              placeholder="Paste token here if not in URL"
            />
          </div>

          <div>
            <label htmlFor="password">New Password (Min 8 characters)</label>
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
              autoComplete="new-password"
            />
          </div>

          <div>
            <label htmlFor="confirm-password">Confirm New Password</label>
            <input
              id="confirm-password"
              type="password"
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

          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Resetting...' : 'Update Password'}
          </button>
        </form>

        <footer>
          <p>
            <Link to="/login" onClick={clearError}>
              Back to Login
            </Link>
          </p>
        </footer>
      </section>
    </main>
  );
}

export default ResetPassword;
