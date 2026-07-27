interface HelperTextProps {
  error?: string;
  helperText?: string;
  errorId?: string;
  helperId?: string;
}

export const HelperText = ({ error, helperText, errorId, helperId }: HelperTextProps) => {
  if (error) {
    return (
      <p id={errorId} role="alert" style={{ marginTop: '4px', fontSize: '0.78rem', color: '#ef4444' }}>
        ⚠️ {error}
      </p>
    );
  }

  if (helperText) {
    return (
      <p id={helperId} style={{ marginTop: '4px', fontSize: '0.78rem', color: '#64748b' }}>
        {helperText}
      </p>
    );
  }

  return null;
};

export default HelperText;
