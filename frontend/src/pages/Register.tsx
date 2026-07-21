import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function Register() {
  const { register, error: apiError, isLoading, clearError } = useAuth();
  const navigate = useNavigate();

  // Form states
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // Validation states
  const [validationError, setValidationError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const validateForm = (): boolean => {
    setValidationError(null);

    if (!email || !fullName || !password || !confirmPassword) {
      setValidationError('All fields are required.');
      return false;
    }

    if (fullName.trim().length < 2) {
      setValidationError('Full name must be at least 2 characters long.');
      return false;
    }

    // Simple email regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setValidationError('Please enter a valid email address.');
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
      await register({
        email: email.trim(),
        full_name: fullName.trim(),
        password,
      });

      setSuccessMessage('Registration successful! Redirecting to login...');
      // Clear form
      setEmail('');
      setFullName('');
      setPassword('');
      setConfirmPassword('');
      
      // Redirect to login page after 2 seconds
      setTimeout(() => {
        navigate('/login', { state: { message: 'Registration successful. Please log in.' } });
      }, 2000);
    } catch (err) {
      // Errors are captured and set in the AuthContext, displayed via apiError
      console.error('Registration failed:', err);
    }
  };

  return (
    <main aria-labelledby="register-heading">
      <section>
        <h1 id="register-heading">Create an Account</h1>
        <p>Sign up to start organizing your study workspaces.</p>

        {/* Display validation or API error states */}
        {(validationError || apiError) && (
          <div role="alert" style={{ color: 'red', margin: '15px 0' }}>
            <p>{validationError || apiError}</p>
          </div>
        )}

        {/* Display success messages */}
        {successMessage && (
          <div role="status" style={{ color: 'green', margin: '15px 0' }}>
            <p>{successMessage}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div>
            <label htmlFor="full-name">Full Name</label>
            <input
              id="full-name"
              type="text"
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
            <label htmlFor="password">Password (Min 8 characters)</label>
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
            <label htmlFor="confirm-password">Confirm Password</label>
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
            {isLoading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <footer>
          <p>
            Already have an account?{' '}
            <Link to="/login" onClick={clearError}>
              Log in here
            </Link>
          </p>
        </footer>
      </section>
    </main>
  );
}

export default Register;
