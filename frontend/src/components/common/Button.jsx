import React from 'react';

export const Button = ({
  children,
  variant = 'primary', // primary, secondary, text, accent
  size = 'md', // sm, md, lg
  icon: Icon,
  iconPosition = 'left',
  loading = false,
  disabled = false,
  onClick,
  type = 'button',
  fullWidth = false,
  className = '',
  style = {}
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: 'var(--color-ink-700)',
          color: 'var(--color-text-on-ink)',
          border: '1px solid var(--color-ink-700)'
        };
      case 'secondary':
        return {
          backgroundColor: 'var(--color-bg-surface)',
          color: 'var(--color-text-primary)',
          border: '1px solid var(--color-border-default)'
        };
      case 'text':
        return {
          backgroundColor: 'transparent',
          color: 'var(--color-text-link)',
          border: '1px solid transparent',
          paddingLeft: 'var(--space-xs)',
          paddingRight: 'var(--space-xs)'
        };
      case 'accent':
        return {
          backgroundColor: 'var(--color-accent-500)',
          color: '#FFFFFF',
          border: '1px solid var(--color-accent-700)'
        };
      default:
        return {};
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return {
          padding: '4px var(--space-sm)',
          fontSize: 'var(--text-caption)',
          minHeight: '32px'
        };
      case 'lg':
        return {
          padding: 'var(--space-sm) var(--space-xl)',
          fontSize: 'var(--text-body)',
          minHeight: '44px'
        };
      case 'md':
      default:
        return {
          padding: 'var(--space-xs) var(--space-md)',
          fontSize: 'var(--text-button)',
          minHeight: '38px'
        };
    }
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`btn-legal btn-${variant} ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 'var(--space-xs)',
        borderRadius: 'var(--radius-md)',
        fontWeight: 500,
        fontFamily: 'var(--font-sans)',
        cursor: disabled || loading ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.4 : 1,
        width: fullWidth ? '100%' : 'auto',
        transition: 'all var(--duration-fast) var(--easing-standard)',
        ...getVariantStyles(),
        ...getSizeStyles(),
        ...style
      }}
    >
      {loading ? (
        <span
          style={{
            width: '14px',
            height: '14px',
            border: '2px solid currentColor',
            borderRightColor: 'transparent',
            borderRadius: '50%',
            animation: 'spin 0.6s linear infinite'
          }}
        />
      ) : (
        <>
          {Icon && iconPosition === 'left' && <Icon size={size === 'sm' ? 14 : 16} />}
          {children}
          {Icon && iconPosition === 'right' && <Icon size={size === 'sm' ? 14 : 16} />}
        </>
      )}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .btn-primary:hover:not(:disabled) {
          background-color: #0F1720 !important;
        }
        .btn-secondary:hover:not(:disabled) {
          background-color: var(--color-bg-surface-sunken) !important;
          border-color: var(--color-border-strong) !important;
        }
        .btn-text:hover:not(:disabled) {
          text-decoration: underline;
        }
        .btn-legal:active:not(:disabled) {
          transform: scale(0.98);
        }
      `}</style>
    </button>
  );
};
