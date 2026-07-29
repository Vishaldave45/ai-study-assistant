import { useState } from 'react';
import Label from './Label';
import HelperText from './HelperText';
import type { FieldValues, PasswordFieldProps } from '../../types/formField.types';

export const PasswordField = <T extends FieldValues = any>({
  name,
  register,
  errors,
  label,
  placeholder = '••••••••',
  required = false,
  disabled = false,
  autoComplete = 'current-password',
  className = '',
  wrapperClass = '',
  value,
  onChange,
}: PasswordFieldProps<T>) => {
  const [visible, setVisible] = useState(false);
  const error = errors?.[name]?.message as string | undefined;
  const registrationProps = register ? register(name) : {};

  return (
    <div style={{ width: '100%', marginBottom: '12px' }} className={wrapperClass}>
      {label && (
        <Label htmlFor={name} required={required}>
          {label}
        </Label>
      )}

      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        <input
          id={name}
          type={visible ? 'text' : 'password'}
          placeholder={placeholder}
          disabled={disabled}
          autoComplete={autoComplete}
          value={value}
          onChange={onChange}
          style={{
            width: '100%',
            padding: '8px 36px 8px 12px',
            fontSize: '0.9rem',
            borderRadius: '6px',
            border: error ? '1px solid #ef4444' : '1px solid #cbd5e1',
            outline: 'none',
            background: disabled ? '#f8fafc' : '#ffffff',
            color: disabled ? '#94a3b8' : '#0f172a',
            transition: 'border-color 0.15s ease',
          }}
          className={className}
          {...registrationProps}
        />

        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          style={{
            position: 'absolute',
            right: '8px',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontSize: '1rem',
            color: '#64748b',
            padding: '4px',
          }}
          aria-label={visible ? 'Hide password' : 'Show password'}
        >
          {visible ? '👁️' : '🔒'}
        </button>
      </div>

      <HelperText error={error} />
    </div>
  );
};

export default PasswordField;
