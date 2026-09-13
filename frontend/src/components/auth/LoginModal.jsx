import React, { useState } from 'react';
import { Lock, ShieldCheck, ArrowRight, AlertCircle } from 'lucide-react';
import { Button } from '../common/Button';

export const LoginScreen = ({ onLoginSuccess }) => {
  const [step, setStep] = useState('credentials'); // 'credentials' | '2fa'
  const [email, setEmail] = useState('e.vance@vance-legal.org');
  const [password, setPassword] = useState('••••••••••••');
  const [rememberMe, setRememberMe] = useState(true);
  const [twoFactorCode, setTwoFactorCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCredentialsSubmit = (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    setTimeout(() => {
      setLoading(false);
      if (email === 'error@vance-legal.org') {
        setError("That email and password combination doesn't match our records.");
        return;
      }
      setStep('2fa');
    }, 450);
  };

  const handle2FASubmit = (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    setTimeout(() => {
      setLoading(false);
      if (twoFactorCode.length !== 6 && twoFactorCode !== '123456') {
        setError('Invalid verification code. Please check your authenticator app.');
        return;
      }
      onLoginSuccess();
    }, 400);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: 'var(--color-bg-canvas)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-md)'
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '420px',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border-subtle)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-xl)',
          boxShadow: 'var(--elevation-2)'
        }}
      >
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--space-sm)' }}>
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 3H15L20 8V21H4V3Z" stroke="var(--color-ink-700)" strokeWidth="2" strokeLinejoin="round" />
              <path d="M15 3V8H20" stroke="var(--color-accent-500)" strokeWidth="2" strokeLinejoin="round" />
            </svg>
          </div>
          <h1
            style={{
              fontFamily: 'var(--font-serif)',
              fontSize: '24px',
              fontWeight: 600,
              color: 'var(--color-ink-700)',
              marginBottom: 'var(--space-3xs)'
            }}
          >
            Legal AI
          </h1>
          <p
            style={{
              fontFamily: 'var(--font-sans)',
              fontSize: 'var(--text-caption)',
              color: 'var(--color-text-secondary)'
            }}
          >
            Workspace for Advocates & Chambers
          </p>
        </div>

        {error && (
          <div
            style={{
              backgroundColor: 'var(--color-error-wash)',
              border: '1px solid var(--color-error-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-xs) var(--space-sm)',
              marginBottom: 'var(--space-md)',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 'var(--space-xs)',
              fontSize: 'var(--text-caption)',
              color: 'var(--color-error-text)'
            }}
          >
            <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>{error}</span>
          </div>
        )}

        {step === 'credentials' ? (
          <form onSubmit={handleCredentialsSubmit}>
            <div style={{ marginBottom: 'var(--space-md)' }}>
              <label
                style={{
                  display: 'block',
                  fontSize: 'var(--text-label)',
                  fontWeight: 500,
                  color: 'var(--color-text-secondary)',
                  marginBottom: 'var(--space-3xs)'
                }}
              >
                Chambers Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-base"
                placeholder="advocate@chambers.org"
              />
            </div>

            <div style={{ marginBottom: 'var(--space-md)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3xs)' }}>
                <label
                  style={{
                    fontSize: 'var(--text-label)',
                    fontWeight: 500,
                    color: 'var(--color-text-secondary)'
                  }}
                >
                  Password
                </label>
                <a
                  href="#forgot"
                  onClick={(e) => { e.preventDefault(); alert("In a production system, a secure reset link would be sent to your verified chamber address."); }}
                  style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-link)' }}
                >
                  Forgot password?
                </a>
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-base"
                placeholder="••••••••••••"
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', marginBottom: 'var(--space-lg)' }}>
              <input
                type="checkbox"
                id="rememberMe"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                style={{ accentColor: 'var(--color-accent-500)', cursor: 'pointer' }}
              />
              <label htmlFor="rememberMe" style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', cursor: 'pointer' }}>
                Remember this device for 30 days
              </label>
            </div>

            <Button
              type="submit"
              variant="primary"
              fullWidth
              loading={loading}
              icon={ArrowRight}
              iconPosition="right"
            >
              Sign In
            </Button>
          </form>
        ) : (
          <form onSubmit={handle2FASubmit}>
            <div style={{ marginBottom: 'var(--space-lg)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-xs)' }}>
                <ShieldCheck size={18} color="var(--color-accent-500)" />
                <span style={{ fontSize: 'var(--text-h3)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                  Two-Step Verification
                </span>
              </div>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)' }}>
                Enter the 6-digit verification code from your authenticator app or hardware token.
              </p>
              <input
                type="text"
                autoFocus
                maxLength={6}
                value={twoFactorCode}
                onChange={(e) => setTwoFactorCode(e.target.value.replace(/\D/g, ''))}
                className="input-base"
                placeholder="123456"
                style={{
                  textAlign: 'center',
                  letterSpacing: '0.25em',
                  fontSize: '20px',
                  fontFamily: 'var(--font-mono)'
                }}
              />
              <div style={{ marginTop: '8px', fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)' }}>
                Test code: <strong>123456</strong>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              fullWidth
              loading={loading}
            >
              Verify & Enter Chambers
            </Button>

            <button
              type="button"
              onClick={() => setStep('credentials')}
              style={{
                width: '100%',
                background: 'none',
                border: 'none',
                marginTop: 'var(--space-md)',
                color: 'var(--color-text-link)',
                fontSize: 'var(--text-caption)',
                cursor: 'pointer'
              }}
            >
              Back to email sign-in
            </button>
          </form>
        )}

        {/* Quiet Security Message (§27) */}
        <div
          style={{
            marginTop: 'var(--space-xl)',
            paddingTop: 'var(--space-md)',
            borderTop: '1px solid var(--color-border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            color: 'var(--color-text-muted)',
            fontSize: 'var(--text-caption)'
          }}
        >
          <Lock size={13} />
          <span>Your connection is 256-bit encrypted</span>
        </div>
      </div>
    </div>
  );
};
