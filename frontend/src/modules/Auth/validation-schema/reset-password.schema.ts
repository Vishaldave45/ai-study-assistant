import * as yup from 'yup';

export const resetPasswordSchema = yup.object({
  token: yup
    .string()
    .required('A reset token is required'),
  password: yup
    .string()
    .required('New password is required')
    .min(8, 'Password must be at least 8 characters long'),
  confirmPassword: yup
    .string()
    .required('Please confirm your new password')
    .oneOf([yup.ref('password')], 'Passwords do not match'),
});

export type ResetPasswordFormData = yup.InferType<typeof resetPasswordSchema>;
