import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { InputField, PasswordField } from '../components';
import { resetPasswordSchema } from '../modules/Auth/validation-schema/reset-password.schema';
import type { ResetPasswordFormData } from '../modules/Auth/validation-schema/reset-password.schema';

export function ResetPassword() {
  const { resetPassword, error: apiError, isLoading, clearError } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const tokenFromUrl = searchParams.get('token') || '';
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: yupResolver(resetPasswordSchema),
    mode: 'onTouched',
    defaultValues: {
      token: tokenFromUrl,
      password: '',
      confirmPassword: '',
    },
  });

  useEffect(() => {
    if (tokenFromUrl) {
      setValue('token', tokenFromUrl);
    }
  }, [tokenFromUrl, setValue]);

  const onSubmit = async (data: ResetPasswordFormData) => {
    clearError();
    setSuccessMessage(null);

    try {
      await resetPassword({
        token: data.token.trim(),
        password: data.password,
      });

      setSuccessMessage('Password has been reset successfully! Redirecting to login...');
      reset();

      setTimeout(() => {
        navigate('/login', {
          state: { message: 'Password reset successful. Please log in with your new password.' },
        });
      }, 2000);
    } catch (err) {
      console.error('Password reset failed:', err);
    }
  };

  return (
    <div className="auth-page-container">
      <main className="auth-card" aria-labelledby="reset-password-heading">
        <header className="auth-header">
          <h1 id="reset-password-heading">Reset Password</h1>
          <p>Set a secure new password for your account.</p>
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
          <InputField<ResetPasswordFormData>
            name="token"
            type="text"
            label="Reset Token"
            placeholder="Paste token here if not in URL"
            register={register}
            errors={errors}
            disabled={isLoading || !!tokenFromUrl}
            required
          />

          <PasswordField<ResetPasswordFormData>
            name="password"
            label="New Password (Min 8 characters)"
            placeholder="••••••••"
            register={register}
            errors={errors}
            disabled={isLoading}
            autoComplete="new-password"
            required
          />

          <PasswordField<ResetPasswordFormData>
            name="confirmPassword"
            label="Confirm New Password"
            placeholder="••••••••"
            register={register}
            errors={errors}
            disabled={isLoading}
            autoComplete="new-password"
            required
          />

          <button type="submit" className="auth-btn" disabled={isLoading} style={{ marginTop: '10px' }}>
            {isLoading ? 'Resetting...' : 'Update Password'}
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

export default ResetPassword;
