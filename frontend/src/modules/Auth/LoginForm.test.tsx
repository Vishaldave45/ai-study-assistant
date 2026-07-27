import { describe, it, expect } from 'vitest';
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
