import type { ButtonHTMLAttributes, ReactNode } from 'react';
import './Button.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'glass';
  isLoading?: boolean;
}

export default function Button({ children, variant = 'primary', isLoading, className = '', ...props }: ButtonProps) {
  return (
    <button 
      className={`custom-button btn-${variant} ${isLoading ? 'loading' : ''} ${className}`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? <span className="spinner-mini"></span> : null}
      {children}
    </button>
  );
}
