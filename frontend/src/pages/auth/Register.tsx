import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import styles from './Register.module.css';

const registerSchema = z
  .object({
    fullName: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().min(1, 'Email is required').email('Invalid email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    confirmPassword: z.string().min(1, 'Confirm Password is required'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

type RegisterFormValues = z.infer<typeof registerSchema>;

export const Register: React.FC = () => {
  const { register: authRegister } = useAuth();
  const navigate = useNavigate();
  const [apiError, setApiError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      fullName: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data: RegisterFormValues) => {
    setApiError(null);
    setSubmitting(true);
    try {
      await authRegister({
        email: data.email,
        full_name: data.fullName,
        password: data.password,
      });
      setSuccess(true);
      // Wait a moment and navigate to login
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

      <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
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
              className={`form-input ${styles.inputWithIcon} ${errors.fullName ? 'error' : ''}`}
              {...register('fullName')}
            />
            <User className={styles.inputIcon} size={18} />
          </div>
          {errors.fullName && <span className="form-error">{errors.fullName.message}</span>}
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
              className={`form-input ${styles.inputWithIcon} ${errors.confirmPassword ? 'error' : ''}`}
              {...register('confirmPassword')}
            />
            <Lock className={styles.inputIcon} size={18} />
          </div>
          {errors.confirmPassword && (
            <span className="form-error">{errors.confirmPassword.message}</span>
          )}
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
