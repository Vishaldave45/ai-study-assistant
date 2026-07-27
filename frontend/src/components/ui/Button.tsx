import type { ButtonHTMLAttributes, ReactNode } from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  disabled,
  className = '',
  style,
  ...props
}: ButtonProps) {
  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case 'secondary':
        return { background: '#64748b', color: '#ffffff', border: 'none' };
      case 'outline':
        return { background: 'transparent', color: '#6366f1', border: '1px solid #6366f1' };
      case 'danger':
        return { background: '#ef4444', color: '#ffffff', border: 'none' };
      case 'ghost':
        return { background: 'transparent', color: '#94a3b8', border: 'none' };
      case 'primary':
      default:
        return { background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)', color: '#ffffff', border: 'none' };
    }
  };

  const getSizeStyles = (): React.CSSProperties => {
    switch (size) {
      case 'sm':
        return { padding: '4px 10px', fontSize: '0.8rem' };
      case 'lg':
        return { padding: '12px 24px', fontSize: '1rem' };
      case 'md':
      default:
        return { padding: '8px 16px', fontSize: '0.9rem' };
    }
  };

  return (
    <button
      disabled={disabled || isLoading}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '6px',
        fontWeight: 600,
        borderRadius: '6px',
        cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
        opacity: disabled || isLoading ? 0.6 : 1,
        transition: 'all 0.15s ease',
        boxShadow: variant === 'primary' ? '0 4px 12px rgba(99, 102, 241, 0.25)' : 'none',
        ...getSizeStyles(),
        ...getVariantStyles(),
        ...style,
      }}
      className={className}
      {...props}
    >
      {isLoading ? (
        <span
          style={{
            width: '14px',
            height: '14px',
            border: '2px solid currentColor',
            borderTopColor: 'transparent',
            borderRadius: '50%',
            animation: 'spin 0.6s linear infinite',
          }}
        />
      ) : (
        leftIcon
      )}
      {children}
      {!isLoading && rightIcon}
    </button>
  );
}

export default Button;
