import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, User, Eye, EyeOff, AlertCircle, ArrowRight, Sparkles, Clock } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import styles from './Register.module.css';

export const Register: React.FC = () => {
  const { register: authRegister } = useAuth();
  const navigate = useNavigate();

  // Input states
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Error states
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
      setFullNameError('Full Name is required');
      isValid = false;
    } else if (fullName.length < 2) {
      setFullNameError('Name must be at least 2 characters');
      isValid = false;
    }

    if (!email) {
      setEmailError('Email Address is required');
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

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    try {
      await authRegister({
        email,
        full_name: fullName,
        password,
      });
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err: any) {
      console.error('Registration error:', err);
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
      <div className={styles.container}>
        <div className={styles.successCard}>
          <div className="flex-center" style={{ marginBottom: '1.5rem', color: 'var(--color-success)' }}>
            <Sparkles size={48} />
          </div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: '0.5rem' }}>
            Registration Successful!
          </h3>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', lineHeight: '1.6', marginBottom: '2rem' }}>
            Your account has been created successfully. Redirecting you to login...
          </p>
          <Link to="/login" className="btn btn-primary" style={{ width: '100%' }}>
            Sign In
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Split register card */}
      <div className={styles.registerCard}>
        {/* Left Side: Form Column */}
        <div className={styles.formColumn}>
          <div className={styles.brandHeader}>
            <div className={styles.logoSquare}>
              <Sparkles size={18} />
            </div>
            <span className={styles.brandName}>AI Study Assistant</span>
            <span className={styles.subtitle}>Create Account</span>
          </div>

          {apiError && (
            <div className={styles.alert}>
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <span>{apiError}</span>
            </div>
          )}

          <form className={styles.form} onSubmit={handleSubmit}>
            {/* Full Name */}
            <div className="form-group">
              <label htmlFor="fullName" className="form-label">
                Full Name
              </label>
              <div className={styles.inputWrapper}>
                <input
                  id="fullName"
                  type="text"
                  placeholder="Alex Johnson"
                  className={`form-input ${styles.inputField} ${fullNameError ? 'error' : ''}`}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
                <User className={styles.inputIcon} size={16} />
              </div>
              {fullNameError && (
                <span className="form-error">
                  <AlertCircle size={12} /> {fullNameError}
                </span>
              )}
            </div>

            {/* Email Address */}
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <div className={styles.inputWrapper}>
                <input
                  id="email"
                  type="text"
                  placeholder="alex@university.edu"
                  className={`form-input ${styles.inputField} ${emailError ? 'error' : ''}`}
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
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <div className={styles.inputWrapper}>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  className={`form-input ${styles.inputField} ${passwordError ? 'error' : ''}`}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className={styles.eyeButton}
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              <span className={styles.passwordHelp}>Use 8+ characters with letters and numbers</span>
              {passwordError && (
                <span className="form-error" style={{ marginTop: '0.2rem' }}>
                  <AlertCircle size={12} /> {passwordError}
                </span>
              )}
            </div>

            {/* Confirm Password */}
            <div className="form-group" style={{ marginBottom: '0.5rem' }}>
              <label htmlFor="confirmPassword" className="form-label">
                Confirm Password
              </label>
              <div className={styles.inputWrapper}>
                <input
                  id="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  className={`form-input ${styles.inputField} ${confirmPasswordError ? 'error' : ''}`}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
              {confirmPasswordError && (
                <span className="form-error">
                  <AlertCircle size={12} /> {confirmPasswordError}
                </span>
              )}
            </div>

            {/* Submit Button */}
            <button type="submit" disabled={submitting} className={styles.submitBtn}>
              {submitting ? (
                <>
                  <div className="spinner"></div>
                  <span>Registering...</span>
                </>
              ) : (
                <>
                  <span>Register</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          <p className={styles.footerText}>
            Already have an account?
            <Link to="/login" className={styles.footerLink}>
              Login
            </Link>
          </p>
        </div>

        {/* Right Side: Info Sidebar Column */}
        <div className={styles.infoColumn}>
          {/* Badge */}
          <div className={styles.infoBadge}>
            <Sparkles size={14} />
            <span>POWERED BY RK ADVANCED LLMS</span>
          </div>

          {/* Description */}
          <div>
            <h3 className={styles.infoTitle}>Master your courses with AI precision.</h3>
            <p className={styles.infoDesc}>
              Join over 50,000 students using our AI-driven study tools to generate flashcards, summarize lectures, and solve complex problems in seconds.
            </p>
          </div>

          {/* Stats Metrics Cards */}
          <div className={styles.statsGrid}>
            <div className={styles.statCard}>
              <div className={styles.statIconWrap}>
                <Sparkles size={18} />
              </div>
              <span className={styles.statText}>94%</span>
              <span className={styles.statLabel}>Study Efficiency</span>
            </div>

            <div className={styles.statCard}>
              <div className={styles.statIconWrap}>
                <Clock size={18} />
              </div>
              <span className={styles.statText}>12h</span>
              <span className={styles.statLabel}>Saved weekly</span>
            </div>
          </div>
        </div>
      </div>

      {/* Page Footer */}
      <div className={styles.pageFooter}>
        <a href="#" style={{ color: 'var(--color-text-muted)' }}>Privacy Policy</a>
        <a href="#" style={{ color: 'var(--color-text-muted)' }}>Terms of Service</a>
      </div>
    </div>
  );
};

export default Register;
