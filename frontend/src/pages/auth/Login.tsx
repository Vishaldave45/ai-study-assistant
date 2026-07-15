import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, AlertCircle, ArrowRight, BookOpen } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import styles from './Login.module.css';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  // Inputs state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Field error states
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [apiError, setApiError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Manual validation logic matching the mockup's strict requirements
  const validateForm = () => {
    let isValid = true;
    setEmailError('');
    setPasswordError('');

    if (!email) {
      setEmailError('Email address is required');
      isValid = false;
    } else if (!email.includes('@')) {
      setEmailError('Invalid email address');
      isValid = false;
    }

    if (!password) {
      setPasswordError('Password is required');
      isValid = false;
    } else if (password.length < 8) {
      setPasswordError('Password must be at least 8 characters');
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    try {
      await login({ email, password });
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
      if (err.response && err.response.data && err.response.data.detail) {
        setApiError(err.response.data.detail);
      } else {
        setApiError('Invalid credentials. Please verify and try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Brand Header (Outside card) */}
      <div className={styles.brandLogoWrap}>
        <div className={styles.logoSquare}>
          <BookOpen size={24} strokeWidth={2.5} />
        </div>
        <span className={styles.brandName}>AI Study Assistant</span>
      </div>

      {/* Main Login Card */}
      <div className={styles.loginCard}>
        <h2 className={styles.title}>Welcome Back</h2>
        <p className={styles.subtitle}>Sign in to continue your session</p>

        {apiError && (
          <div className={styles.alert}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            <span>{apiError}</span>
          </div>
        )}

        <form className={styles.form} onSubmit={handleSubmit}>
          {/* Email Address */}
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <div className={styles.inputWrapper}>
              <input
                id="email"
                type="text"
                placeholder="user@invalid-study"
                className={`form-input ${styles.inputWithIcon} ${emailError ? 'error' : ''}`}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <Mail className={styles.inputIcon} size={16} />
            </div>
            {emailError && (
              <span className="form-error">
                <AlertCircle size={12} /> {emailError}
              </span>
            )}
          </div>

          {/* Password */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <a
                href="#"
                className={styles.forgotPassword}
                onClick={(e) => {
                  e.preventDefault();
                  alert('Password recovery is not implemented.');
                }}
              >
                Forgot?
              </a>
            </div>
            <div className={styles.inputWrapper}>
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                className={`form-input ${styles.inputWithIcon} ${passwordError ? 'error' : ''}`}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <Lock className={styles.inputIcon} size={16} />
              <button
                type="button"
                className={styles.eyeButton}
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {passwordError && (
              <span className="form-error">
                <AlertCircle size={12} /> {passwordError}
              </span>
            )}
          </div>

          {/* Submit Action */}
          <button type="submit" disabled={submitting} className={styles.submitBtn}>
            {submitting ? (
              <>
                <div className="spinner"></div>
                <span>Logging in...</span>
              </>
            ) : (
              <>
                <span>Login</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        {/* Third-Party Auth Separator */}
        <div className={styles.dividerRow}>
          <div className={styles.dividerLine}></div>
          <span className={styles.dividerText}>OR CONTINUE WITH</span>
          <div className={styles.dividerLine}></div>
        </div>

        {/* Google Authentication */}
        <button
          type="button"
          className={styles.googleBtn}
          onClick={() => alert('Google authentication is mock-only.')}
        >
          {/* Simple Colored Google Logo SVG */}
          <svg className={styles.googleIcon} viewBox="0 0 24 24" width="20" height="20">
            <path
              fill="#EA4335"
              d="M12.24 10.285V14.4h6.887c-.648 2.41-2.519 4.114-5.136 4.114-3.51 0-6.386-2.876-6.386-6.386 0-3.51 2.876-6.386 6.386-6.386 1.62 0 3.096.612 4.23 1.62l3.024-3.024C19.18 2.295 15.93 1 12.24 1 6.03 1 1 6.03 1 12.24s4.97 11.24 11.24 11.24c6.318 0 11.24-5.04 11.24-11.24 0-.792-.072-1.548-.198-2.286H12.24z"
            />
          </svg>
          <span>Google</span>
        </button>

        {/* Redirect Option */}
        <p className={styles.footerText}>
          Don't have an account?
          <Link to="/register" className={styles.footerLink}>
            Register for free
          </Link>
        </p>
      </div>

      {/* Footer Details (Screenshot 2 bottom info) */}
      <div className={styles.pageFooter}>
        <div className={styles.footerLinks}>
          <a href="#">Privacy Policy</a>
          <span>•</span>
          <a href="#">Terms of Service</a>
        </div>
        <span className={styles.monoSecured}>SECURED BY ENCRYPTION PROTOCOL 2.4.0</span>
      </div>
    </div>
  );
};

export default Login;
