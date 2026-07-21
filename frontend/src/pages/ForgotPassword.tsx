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
    <main aria-labelledby="forgot-password-heading">
      <section>
        <h1 id="forgot-password-heading">Recover Password</h1>
        <p>Enter your email address and we'll log a reset token to the terminal.</p>

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

          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Submitting...' : 'Send Reset Link'}
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

export default ForgotPassword;
