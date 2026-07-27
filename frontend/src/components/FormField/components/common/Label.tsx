import type { ReactNode } from 'react';

interface LabelProps {
  htmlFor?: string;
  required?: boolean;
  className?: string;
  children: ReactNode;
}

export const Label = ({ htmlFor, required, className = '', children }: LabelProps) => {
  return (
    <label
      htmlFor={htmlFor}
      style={{
        display: 'block',
        fontSize: '0.88rem',
        fontWeight: 600,
        color: '#334155',
        marginBottom: '4px',
      }}
      className={className}
    >
      {children}
      {required && <span style={{ color: '#ef4444', marginLeft: '4px' }}>*</span>}
    </label>
  );
};

export default Label;
