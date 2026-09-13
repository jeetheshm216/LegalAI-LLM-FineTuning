import React from 'react';
import { Button } from './Button';

export const EmptyState = ({
  icon: Icon,
  title = "No cases yet.",
  description = "Add your first case to start organizing documents, hearings, and AI research in one place.",
  actionLabel = "Add your first case",
  onAction,
  actionIcon
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-3xl) var(--space-xl)',
        textAlign: 'center',
        maxWidth: '560px',
        margin: '0 auto'
      }}
    >
      {Icon && (
        <div
          style={{
            marginBottom: 'var(--space-md)',
            color: 'var(--color-ink-300)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <Icon size={44} strokeWidth={1.5} />
        </div>
      )}

      <h2
        style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'var(--text-h1)',
          color: 'var(--color-text-primary)',
          fontWeight: 600,
          marginBottom: 'var(--space-xs)'
        }}
      >
        {title}
      </h2>

      <p
        style={{
          fontFamily: 'var(--font-sans)',
          fontSize: 'var(--text-body)',
          color: 'var(--color-text-secondary)',
          lineHeight: 1.6,
          marginBottom: onAction ? 'var(--space-lg)' : 0
        }}
      >
        {description}
      </p>

      {onAction && actionLabel && (
        <Button
          variant="primary"
          size="md"
          icon={actionIcon}
          onClick={onAction}
        >
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
