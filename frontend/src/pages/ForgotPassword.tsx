import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { InputField } from '../components/FormField';
import { forgotPasswordSchema } from '../modules/Auth/validation-schema/forgot-password.schema';
import type { ForgotPasswordFormData } from '../modules/Auth/validation-schema/forgot-password.schema';

export function ForgotPassword() {
  const { forgotPassword, error: apiError, isLoading, clearError } = useAuth();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: yupResolver(forgotPasswordSchema),
    mode: 'onTouched',
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    clearError();
    setSuccessMessage(null);

    try {
      await forgotPassword({ email: data.email.trim() });
      setSuccessMessage(
        'Password reset request submitted. Check the backend server terminal logs for your reset token!'
      );
      reset();
    } catch (err) {
      console.error('Forgot password request failed:', err);
    }
  };

  return (
    <div className="auth-page-container">
      <main className="auth-card" aria-labelledby="forgot-password-heading">
        <header className="auth-header">
          <h1 id="forgot-password-heading">Recover Password</h1>
          <p>Enter your email address to receive your recovery token.</p>
        </header>

        {apiError && (
          <div className="auth-alert error" role="alert" style={{ marginBottom: '20px' }}>
            <span>⚠️</span>
            <p>{apiError}</p>
          </div>
        )}

        {successMessage && (
          <div
            className="auth-alert info"
            role="status"
            style={{
              marginBottom: '20px',
              background: 'rgba(52, 211, 153, 0.1)',
              border: '1px solid rgba(52, 211, 153, 0.2)',
              color: 'var(--text-success)',
            }}
          >
            <span>✔️</span>
            <p>{successMessage}</p>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <InputField<ForgotPasswordFormData>
            name="email"
            type="email"
            label="Email Address"
            placeholder="name@example.com"
            register={register}
            errors={errors}
            disabled={isLoading}
            autoComplete="email"
            required
          />

          <button type="submit" className="auth-btn" disabled={isLoading} style={{ marginTop: '10px' }}>
            {isLoading ? 'Submitting...' : 'Send Reset Link'}
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

export default ForgotPassword;
