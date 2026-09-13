import React from 'react';

export const CaseStatusBadge = ({ status }) => {
  const statusLower = (status || 'active').toLowerCase();

  const statusStyles = {
    active: {
      color: 'var(--color-case-active-text)',
      backgroundColor: 'var(--color-case-active-wash)'
    },
    pending: {
      color: 'var(--color-case-pending-text)',
      backgroundColor: 'var(--color-case-pending-wash)'
    },
    upcoming: {
      color: 'var(--color-case-upcoming-text)',
      backgroundColor: 'var(--color-case-upcoming-wash)'
    },
    urgent: {
      color: 'var(--color-case-urgent-text)',
      backgroundColor: 'var(--color-case-urgent-wash)'
    },
    closed: {
      color: 'var(--color-case-closed-text)',
      backgroundColor: 'var(--color-case-closed-wash)'
    },
    archived: {
      color: 'var(--color-case-archived-text)',
      backgroundColor: 'var(--color-case-archived-wash)'
    }
  };

  const currentStyle = statusStyles[statusLower] || statusStyles.active;

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px var(--space-xs)',
        borderRadius: 'var(--radius-sm)',
        fontSize: 'var(--text-caption)',
        fontWeight: 500,
        fontFamily: 'var(--font-sans)',
        lineHeight: 1.3,
        ...currentStyle
      }}
    >
      {status}
    </span>
  );
};

export const DocumentStatusDot = ({ status, label }) => {
  const isProcessing = status === 'processing';
  const isReady = status === 'ready' || status === 'indexed';
  const isFailed = status === 'failed';

  const dotColor = isReady 
    ? 'var(--color-success-text)' 
    : isProcessing 
      ? 'var(--color-information-text)' 
      : isFailed 
        ? 'var(--color-error-text)' 
        : 'var(--color-text-muted)';

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
      <span
        style={{
          width: '7px',
          height: '7px',
          borderRadius: '50%',
          backgroundColor: dotColor,
          display: 'inline-block',
          animation: isProcessing ? 'pulseDot 1.5s ease-in-out infinite' : 'none'
        }}
      />
      {label || (isReady ? 'Ready for AI search' : isProcessing ? 'Processing' : isFailed ? 'Failed' : status)}
      <style>{`
        @keyframes pulseDot {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
      `}</style>
    </span>
  );
};

export const ReliabilityBadge = ({ reliability, label }) => {
  const isSupported = reliability === 'supported';
  const isLimited = reliability === 'limited';

  const borderColor = isSupported
    ? 'var(--color-success-text)'
    : isLimited
      ? 'var(--color-warning-text)'
      : 'var(--color-text-muted)';

  const textColor = borderColor;

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        fontSize: 'var(--text-caption)',
        color: textColor,
        fontWeight: 500
      }}
    >
      <span
        style={{
          display: 'inline-block',
          width: '8px',
          height: '8px',
          borderRadius: isSupported ? '50%' : isLimited ? '0%' : '50%',
          border: `1.5px solid ${borderColor}`,
          backgroundColor: isSupported ? borderColor : 'transparent'
        }}
      />
      <span>{label || (isSupported ? 'Supported by sources' : isLimited ? 'Limited supporting evidence' : 'Verification recommended')}</span>
    </div>
  );
};
