import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
}

export function Card({ children }: CardProps) {
  return (
    <div
      style={{
        border: '1px solid #ddd',
        padding: '20px',
        borderRadius: '10px',
        marginBottom: '20px',
        background: '#fff',
      }}
    >
      {children}
    </div>
  );
}

export default Card;
