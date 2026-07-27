import type { InputHTMLAttributes, ReactNode } from 'react';

export type FieldValues = Record<string, any>;

export interface BaseFieldProps<T extends FieldValues = any> {
  name: (keyof T & string) | string;
  register?: any;
  errors?: Record<string, { message?: string } | any>;
  label?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  autoComplete?: string;
  className?: string;
  wrapperClass?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export type FieldSize = 'sm' | 'md' | 'lg';

export interface InputFieldProps<T extends FieldValues = any> extends BaseFieldProps<T> {
  type?: 'text' | 'email' | 'number' | 'tel' | 'url' | 'search' | 'date' | 'password';
  size?: FieldSize;
  helperText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  isLoading?: boolean;
  id?: string;
  inputMode?: InputHTMLAttributes<HTMLInputElement>['inputMode'];
  maxLength?: number;
  autoFocus?: boolean;
  inputProps?: Omit<
    InputHTMLAttributes<HTMLInputElement>,
    'size' | 'type' | 'id' | 'name' | 'className'
  >;
}

export type PasswordFieldProps<T extends FieldValues = any> = BaseFieldProps<T>;
