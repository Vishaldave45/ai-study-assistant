import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { InputField, PasswordField } from '../components';
import { registerSchema } from '../modules/Auth/validation-schema/register.schema';
import type { RegisterFormData } from '../modules/Auth/validation-schema/register.schema';

export function Register() {
  const { register: authRegister, error: apiError, isLoading, clearError } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: yupResolver(registerSchema),
    mode: 'onTouched',
  });

  const onSubmit = async (data: RegisterFormData) => {
    clearError();
    try {
      await authRegister({
        email: data.email.trim(),
        full_name: data.full_name.trim(),
        password: data.password,
      });

      navigate('/login', {
        state: { message: 'Registration successful! Please log in with your credentials.' },
      });
    } catch (err) {
      console.error('Registration failed:', err);
    }
  };

  return (
    <div className="auth-page-container">
      <main className="auth-card" aria-labelledby="register-heading">
        <header className="auth-header">
          <h1 id="register-heading">Create Account</h1>
          <p>Sign up to start parsing study materials.</p>
        </header>

        {apiError && (
          <div className="auth-alert error" role="alert" style={{ marginBottom: '20px' }}>
            <span>⚠️</span>
            <p>{apiError}</p>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <InputField<RegisterFormData>
            name="full_name"
            label="Full Name"
            placeholder="John Doe"
            register={register}
            errors={errors}
            disabled={isLoading}
            autoComplete="name"
            required
          />

          <InputField<RegisterFormData>
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

          <PasswordField<RegisterFormData>
            name="password"
            label="Password (Min 8 chars)"
            placeholder="••••••••"
            register={register}
            errors={errors}
            disabled={isLoading}
            autoComplete="new-password"
            required
          />

          <PasswordField<RegisterFormData>
            name="confirm_password"
            label="Confirm Password"
            placeholder="••••••••"
            register={register}
            errors={errors}
            disabled={isLoading}
            autoComplete="new-password"
            required
          />

          <button type="submit" className="auth-btn" disabled={isLoading} style={{ marginTop: '10px' }}>
            {isLoading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>

        <footer className="auth-footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" onClick={clearError}>
              Log in here
            </Link>
          </p>
        </footer>
      </main>
    </div>
  );
}

export default Register;
