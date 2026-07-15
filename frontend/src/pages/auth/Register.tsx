import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import styles from './Register.module.css';

export const Register: React.FC = () => {
  const { register: authRegister } = useAuth();
  const navigate = useNavigate();

  // Simple state variables for form inputs
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // States for errors and statuses
  const [fullNameError, setFullNameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');
  const [apiError, setApiError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Manual validation logic
  const validateForm = () => {
    let isValid = true;
    setFullNameError('');
    setEmailError('');
    setPasswordError('');
    setConfirmPasswordError('');

    if (!fullName) {
      setFullNameError('Name is required');
      isValid = false;
    } else if (fullName.length < 2) {
      setFullNameError('Name must be at least 2 characters long');
      isValid = false;
    }

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

    if (!confirmPassword) {
      setConfirmPasswordError('Confirm password is required');
      isValid = false;
    } else if (password !== confirmPassword) {
      setConfirmPasswordError('Passwords do not match');
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);

    // Validate inputs
    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    try {
      // Call the register context action
      await authRegister({
        email,
        full_name: fullName,
        password,
      });
      setSuccess(true);
      // Wait a moment and navigate to login
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err: any) {
      console.error('Registration error details:', err);
      if (err.response && err.response.data && err.response.data.detail) {
        setApiError(err.response.data.detail);
      } else {
        setApiError('Unable to complete registration. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className={styles.successAlert}>
        <div className="flex-center" style={{ marginBottom: '1rem' }}>
          <CheckCircle size={48} color="var(--color-success)" />
        </div>
        <h3 className={styles.successTitle}>Registration Successful!</h3>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', lineHeight: '1.5' }}>
          Your account has been created. Redirecting to login in a few seconds...
        </p>
        <div style={{ marginTop: '1.5rem' }}>
          <Link to="/login" className="btn btn-primary" style={{ width: '100%' }}>
            Sign In Now
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h2 className={styles.title}>Create Account</h2>
      <p className={styles.subtitle}>Get started with your personalized dashboard</p>

      {apiError && (
        <div className={styles.alert}>
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <span>{apiError}</span>
        </div>
      )}

      <form className={styles.form} onSubmit={handleSubmit}>
        {/* Full Name Field */}
        <div className="form-group">
          <label htmlFor="fullName" className="form-label">
            Full Name
          </label>
          <div className={styles.inputWrapper}>
            <input
              id="fullName"
              type="text"
              placeholder="John Doe"
              className={`form-input ${styles.inputWithIcon} ${fullNameError ? 'error' : ''}`}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
            <User className={styles.inputIcon} size={18} />
          </div>
          {fullNameError && <span className="form-error">{fullNameError}</span>}
        </div>

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

        {/* Confirm Password Field */}
        <div className="form-group">
          <label htmlFor="confirmPassword" className="form-label">
            Confirm Password
          </label>
          <div className={styles.inputWrapper}>
            <input
              id="confirmPassword"
              type="password"
              placeholder="••••••••"
              className={`form-input ${styles.inputWithIcon} ${confirmPasswordError ? 'error' : ''}`}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
            <Lock className={styles.inputIcon} size={18} />
          </div>
          {confirmPasswordError && <span className="form-error">{confirmPasswordError}</span>}
        </div>

        {/* Submit Button */}
        <button type="submit" disabled={submitting} className={`btn btn-primary ${styles.submitBtn}`}>
          {submitting ? (
            <>
              <div className="spinner"></div>
              <span>Creating Account...</span>
            </>
          ) : (
            <span>Create Account</span>
          )}
        </button>
      </form>

      <p className={styles.footerText}>
        Already have an account?
        <Link to="/login" className={styles.footerLink}>
          Sign in
        </Link>
      </p>
    </div>
  );
};

export default Register;
