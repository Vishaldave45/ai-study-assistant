import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { InputField, PasswordField } from '../components';
import { loginSchema } from '../modules/Auth/validation-schema/login.schema';
import type { LoginFormData } from '../modules/Auth/validation-schema/login.schema';

interface LocationState {
  message?: string;
}

export function Login() {
  const { login, error: apiError, isLoading, clearError } = useAuth();
  const location = useLocation();
  const [infoMessage, setInfoMessage] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: yupResolver(loginSchema),
    mode: 'onTouched',
  });

  useEffect(() => {
    const state = location.state as LocationState | null;
    if (state?.message) {
      setInfoMessage(state.message);
    }
  }, [location.state]);

  const onSubmit = async (data: LoginFormData) => {
    clearError();
    setInfoMessage(null);
    try {
      await login({
        email: data.email.trim(),
        password: data.password,
      });
    } catch (err) {
      console.error('Login submit failed:', err);
    }
  };

  return (
    <div className="auth-page-container">
      <main className="auth-card" aria-labelledby="login-heading">
        <header className="auth-header">
          <h1 id="login-heading">Welcome Back</h1>
          <p>Sign in to access your study assistant.</p>
        </header>

        {apiError && (
          <div className="auth-alert error" role="alert" style={{ marginBottom: '20px' }}>
            <span>⚠️</span>
            <p>{apiError}</p>
          </div>
        )}

        {infoMessage && (
          <div className="auth-alert info" role="status" style={{ marginBottom: '20px' }}>
            <span>ℹ️</span>
            <p>{infoMessage}</p>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <InputField<LoginFormData>
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

          <PasswordField<LoginFormData>
            name="password"
            label="Password"
            placeholder="••••••••"
            register={register}
            errors={errors}
            disabled={isLoading}
            autoComplete="current-password"
            required
          />

          <button type="submit" className="auth-btn" disabled={isLoading} style={{ marginTop: '10px' }}>
            {isLoading ? 'Logging in...' : 'Log In'}
          </button>
        </form>

        <footer className="auth-footer">
          <p>
            <Link to="/forgot-password" onClick={clearError}>
              Forgot password?
            </Link>
          </p>
          <p>
            Don't have an account?{' '}
            <Link to="/register" onClick={clearError}>
              Sign up here
            </Link>
          </p>
        </footer>
      </main>
    </div>
  );
}

export default Login;
