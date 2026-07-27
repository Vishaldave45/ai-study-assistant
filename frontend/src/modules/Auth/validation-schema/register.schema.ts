import * as yup from 'yup';

export const registerSchema = yup.object({
  email: yup
    .string()
    .required('Email address is required')
    .email('Please enter a valid email address'),
  full_name: yup.string().required('Full name is required'),
  password: yup
    .string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters long'),
  confirm_password: yup
    .string()
    .required('Please confirm your password')
    .oneOf([yup.ref('password')], 'Passwords must match'),
});

export type RegisterFormData = yup.InferType<typeof registerSchema>;
