import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, AlertCircle } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import styles from './Login.module.css';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  // Simple state variables for form inputs
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // States for handling load states and validation/API errors
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [apiError, setApiError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Manual validation checks
  const validateForm = () => {
    let isValid = true;
    setEmailError('');
    setPasswordError('');

    if (!email) {
      setEmailError('Email is required');
      isValid = false;
    } else if (!email.includes('@')) {
      setEmailError('Please enter a valid email address');
      isValid = false;
    }

    if (!password) {
      setPasswordError('Password is required');
      isValid = false;
    } else if (password.length < 8) {
      setPasswordError('Password must be at least 8 characters long');
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);

    // Run validations
    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    try {
      // Call the simple login context action
      await login({ email, password });
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login error details:', err);
      if (err.response && err.response.data && err.response.data.detail) {
        setApiError(err.response.data.detail);
      } else {
        setApiError('Unable to connect to the server. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h2 className={styles.title}>Welcome Back</h2>
      <p className={styles.subtitle}>Sign in to resume your learning session</p>

      {apiError && (
        <div className={styles.alert}>
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <span>{apiError}</span>
        </div>
      )}

      <form className={styles.form} onSubmit={handleSubmit}>
        {/* Email Field */}
        <div className="form-group">
          <label htmlFor="email" className="form-label">
            Email Address
          </label>
          <div className={styles.inputWrapper}>
            <input
              id="email"
              type="email"
              placeholder="name@example.com"
              className={`form-input ${styles.inputWithIcon} ${emailError ? 'error' : ''}`}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Mail className={styles.inputIcon} size={18} />
          </div>
          {emailError && <span className="form-error">{emailError}</span>}
        </div>

        {/* Password Field */}
        <div className="form-group">
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <div className={styles.inputWrapper}>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              className={`form-input ${styles.inputWithIcon} ${passwordError ? 'error' : ''}`}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Lock className={styles.inputIcon} size={18} />
          </div>
          {passwordError && <span className="form-error">{passwordError}</span>}
        </div>

        {/* Actions Row */}
        <div className={styles.optionsRow}>
          <label className={styles.rememberMe}>
            <input type="checkbox" className={styles.checkbox} />
            <span>Remember me</span>
          </label>
          <a
            href="#"
            className={styles.forgotPassword}
            onClick={(e) => {
              e.preventDefault();
              alert('Password reset is not configured.');
            }}
          >
            Forgot Password?
          </a>
        </div>

        {/* Submit Button */}
        <button type="submit" disabled={submitting} className={`btn btn-primary ${styles.submitBtn}`}>
          {submitting ? (
            <>
              <div className="spinner"></div>
              <span>Signing In...</span>
            </>
          ) : (
            <span>Sign In</span>
          )}
        </button>
      </form>

      <p className={styles.footerText}>
        Don't have an account?
        <Link to="/register" className={styles.footerLink}>
          Sign up
        </Link>
      </p>
    </div>
  );
};

export default Login;
