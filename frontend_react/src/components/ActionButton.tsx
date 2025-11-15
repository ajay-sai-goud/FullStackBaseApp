import React from 'react';
import './ActionButton.css';

export type ActionButtonVariant = 'edit' | 'delete' | 'save' | 'cancel' | 'download';

interface ActionButtonProps {
  variant: ActionButtonVariant;
  onClick: () => void;
  disabled?: boolean;
  title?: string;
  ariaLabel?: string;
}

/**
 * Professional action button component
 * Supports edit, delete, save, and cancel variants
 */
const ActionButton: React.FC<ActionButtonProps> = ({
  variant,
  onClick,
  disabled = false,
  title,
  ariaLabel,
}) => {
  const getIcon = () => {
    switch (variant) {
      case 'edit':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
        );
      case 'delete':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        );
      case 'save':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        );
      case 'cancel':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        );
      case 'download':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <button
      className={`action-btn action-btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
      title={title}
      aria-label={ariaLabel || title}
    >
      {getIcon()}
    </button>
  );
};

export default ActionButton;

