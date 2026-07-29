import Label from './Label';
import HelperText from './HelperText';
import type { FieldValues, InputFieldProps } from '../../types/formField.types';

export const InputField = <T extends FieldValues = any>({
  name,
  register,
  errors,
  label,
  placeholder,
  type = 'text',
  required = false,
  disabled = false,
  readOnly = false,
  autoComplete,
  helperText,
  leftIcon,
  rightIcon,
  isLoading = false,
  id,
  inputMode,
  maxLength,
  autoFocus,
  className = '',
  wrapperClass = '',
  value,
  onChange,
  inputProps,
}: InputFieldProps<T>) => {
  const error = errors?.[name]?.message as string | undefined;
  const inputId = id ?? name;
  const errorId = `${inputId}-error`;
  const helperId = `${inputId}-helper`;
  const describedBy = error ? errorId : helperText ? helperId : undefined;

  const registrationProps = register ? register(name) : {};

  return (
    <div style={{ width: '100%', marginBottom: '12px' }} className={wrapperClass}>
      {label && (
        <Label htmlFor={inputId} required={required}>
          {label}
        </Label>
      )}

      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        {leftIcon && (
          <span
            style={{
              position: 'absolute',
              left: '10px',
              color: '#94a3b8',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {leftIcon}
          </span>
        )}

        <input
          id={inputId}
          type={type}
          placeholder={placeholder}
          disabled={disabled}
          readOnly={readOnly}
          autoComplete={autoComplete}
          inputMode={inputMode}
          maxLength={maxLength}
          autoFocus={autoFocus}
          value={value}
          onChange={onChange}
          aria-invalid={error ? true : undefined}
          aria-required={required || undefined}
          aria-describedby={describedBy}
          style={{
            width: '100%',
            padding: '8px 12px',
            paddingLeft: leftIcon ? '32px' : '12px',
            paddingRight: isLoading || rightIcon ? '32px' : '12px',
            fontSize: '0.9rem',
            borderRadius: '6px',
            border: error ? '1px solid #ef4444' : '1px solid #cbd5e1',
            outline: 'none',
            background: disabled ? '#f8fafc' : '#ffffff',
            color: disabled ? '#94a3b8' : '#0f172a',
            transition: 'border-color 0.15s ease',
          }}
          className={className}
          {...inputProps}
          {...registrationProps}
        />

        {(isLoading || rightIcon) && (
          <span
            style={{
              position: 'absolute',
              right: '10px',
              color: '#94a3b8',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {isLoading ? <span className="spinner"></span> : rightIcon}
          </span>
        )}
      </div>

      <HelperText error={error} helperText={helperText} errorId={errorId} helperId={helperId} />
    </div>
  );
};

export default InputField;
