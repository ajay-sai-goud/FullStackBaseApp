import React from 'react';
import './Button.css';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'success' | 'outline' | 'ghost';
export type ButtonSize = 'small' | 'medium' | 'large';
export type ButtonIconPosition = 'left' | 'right' | 'only';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: React.ReactNode;
  iconPosition?: ButtonIconPosition;
  isLoading?: boolean;
  fullWidth?: boolean;
  collapse?: {
    isCollapsed: boolean;
    onToggle: () => void;
  };
}

/**
 * Unified Button component for use throughout the application
 * Supports multiple variants, sizes, icons, loading states, and collapse functionality
 */
const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  icon,
  iconPosition = 'left',
  isLoading = false,
  fullWidth = false,
  collapse,
  children,
  className = '',
  disabled,
  ...props
}) => {
  // If collapse prop is provided, render as collapse button
  if (collapse) {
    return (
      <button
        type="button"
        className={`btn btn-collapse ${collapse.isCollapsed ? 'collapsed' : ''} ${className}`}
        onClick={collapse.onToggle}
        disabled={disabled}
        aria-expanded={!collapse.isCollapsed}
        aria-label={collapse.isCollapsed ? 'Expand' : 'Collapse'}
        {...props}
      >
        <svg
          className="collapse-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          {collapse.isCollapsed ? (
            <polyline points="9 18 15 12 9 6"></polyline>
          ) : (
            <polyline points="6 9 12 15 18 9"></polyline>
          )}
        </svg>
        {children && <span className="collapse-text">{children}</span>}
      </button>
    );
  }

  const buttonClasses = [
    'btn',
    `btn-${variant}`,
    `btn-${size}`,
    fullWidth && 'btn-full-width',
    isLoading && 'btn-loading',
    iconPosition === 'only' && 'btn-icon-only',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const renderIcon = () => {
    if (isLoading) {
      return (
        <svg className="btn-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" strokeOpacity="0.25"></circle>
          <path d="M12 2a10 10 0 0 1 10 10" strokeLinecap="round"></path>
        </svg>
      );
    }
    return icon;
  };

  return (
    <button
      type="button"
      className={buttonClasses}
      disabled={disabled || isLoading}
      {...props}
    >
      {iconPosition === 'left' && renderIcon() && (
        <span className="btn-icon btn-icon-left">{renderIcon()}</span>
      )}
      {children && <span className="btn-text">{children}</span>}
      {iconPosition === 'right' && renderIcon() && (
        <span className="btn-icon btn-icon-right">{renderIcon()}</span>
      )}
      {iconPosition === 'only' && renderIcon() && (
        <span className="btn-icon">{renderIcon()}</span>
      )}
    </button>
  );
};

export default Button;

