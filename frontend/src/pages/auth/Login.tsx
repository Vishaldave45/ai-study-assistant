import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, AlertCircle } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import styles from './Login.module.css';

const loginSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [apiError, setApiError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormValues) => {
    setApiError(null);
    setSubmitting(true);
    try {
      await login(data);
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
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

      <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
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
              className={`form-input ${styles.inputWithIcon} ${errors.email ? 'error' : ''}`}
              {...register('email')}
            />
            <Mail className={styles.inputIcon} size={18} />
          </div>
          {errors.email && <span className="form-error">{errors.email.message}</span>}
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
              className={`form-input ${styles.inputWithIcon} ${errors.password ? 'error' : ''}`}
              {...register('password')}
            />
            <Lock className={styles.inputIcon} size={18} />
          </div>
          {errors.password && <span className="form-error">{errors.password.message}</span>}
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
              alert('Password reset function is not implemented in this demo backend.');
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
