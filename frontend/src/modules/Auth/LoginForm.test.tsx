import { describe, it, expect } from 'vitest';
import { render, screen, userEvent } from '../../test/test-utils';
import { Login } from '../../pages/Login';
import { loginSchema } from './validation-schema/login.schema';

describe('Login Form Validation Schema (Yup)', () => {
  it('validates correct email and password inputs', async () => {
    const validData = { email: 'user@example.com', password: 'password123' };
    const result = await loginSchema.isValid(validData);
    expect(result).toBe(true);
  });

  it('rejects invalid email formats', async () => {
    const invalidData = { email: 'invalid-email-format', password: 'password123' };
    const result = await loginSchema.isValid(invalidData);
    expect(result).toBe(false);
  });

  it('rejects empty password field', async () => {
    const invalidData = { email: 'user@example.com', password: '' };
    const result = await loginSchema.isValid(invalidData);
    expect(result).toBe(false);
  });
});

describe('Login Component UI & Interaction', () => {
  it('renders login heading, form inputs, and submit button', () => {
    render(<Login />);

    expect(screen.getByRole('heading', { level: 1, name: /welcome back/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i, { selector: 'input' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
  });

  it('allows user to type into email and password inputs', async () => {
    const user = userEvent.setup();
    render(<Login />);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i, { selector: 'input' });

    await user.type(emailInput, 'student@example.com');
    await user.type(passwordInput, 'securePassword123');

    expect(emailInput).toHaveValue('student@example.com');
    expect(passwordInput).toHaveValue('securePassword123');
  });
});



