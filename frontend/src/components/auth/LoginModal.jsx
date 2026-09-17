import React, { useState } from 'react';
import { Lock, ShieldCheck, ArrowRight, AlertCircle, Info, UserCheck, KeyRound, Eye, EyeOff } from 'lucide-react';
import { Button } from '../common/Button';
import { authService } from '../../services/authService';
import { RegisterAdvocateModal } from './RegisterAdvocateModal';
import { PROTOTYPE_DISCLAIMER } from '../../services/verificationService';

export const LoginScreen = ({ onLoginSuccess, initialError = '' }) => {
  const [step, setStep] = useState('credentials'); // 'credentials' | '2fa'
  const [email, setEmail] = useState('e.vance@vance-legal.org');
  const [password, setPassword] = useState('••••••••••••');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [twoFactorCode, setTwoFactorCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(initialError);
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);

  const handleCredentialsSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await authService.login({
        email,
        password: password === '••••••••••••' ? 'demo-password' : password,
        rememberMe
      });

      setLoading(false);
      if (res.requires2FA) {
        setStep('2fa');
      } else {
        onLoginSuccess();
      }
    } catch (err) {
      setLoading(false);
      setError(err.message || "We couldn't verify the account credentials.");
    }
  };

  const handle2FASubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.verify2FA({ code: twoFactorCode });
      setLoading(false);
      onLoginSuccess();
    } catch (err) {
      setLoading(false);
      setError(err.message || 'Invalid verification code. Please check your authenticator app.');
    }
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
          maxWidth: '440px',
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
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 3H15L20 8V21H4V3Z" stroke="var(--color-ink-700)" strokeWidth="2" strokeLinejoin="round" />
              <path d="M15 3V8H20" stroke="var(--color-accent-500)" strokeWidth="2" strokeLinejoin="round" />
            </svg>
          </div>
          <h1
            style={{
              fontFamily: 'var(--font-serif)',
              fontSize: '26px',
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
            Secure workspace for verified legal professionals
          </p>
        </div>

        {/* Prototype Verification Disclaimer */}
        <div
          style={{
            backgroundColor: 'var(--color-bg-surface-sunken)',
            border: '1px solid var(--color-border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--space-xs) var(--space-sm)',
            marginBottom: 'var(--space-md)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-xs)',
            fontSize: '11px',
            color: 'var(--color-text-secondary)'
          }}
        >
          <Info size={14} color="var(--color-accent-500)" style={{ flexShrink: 0 }} />
          <span>{PROTOTYPE_DISCLAIMER}</span>
        </div>

        {/* Error Alert */}
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
          <div>
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
                  Chambers Email or Registered Mobile
                  <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
                </label>
                <input
                  type="text"
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
                    <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
                  </label>
                  <a
                    href="#forgot"
                    onClick={(e) => {
                      e.preventDefault();
                      alert('In production, a cryptographic reset token is transmitted to your registered State Bar roll address.');
                    }}
                    style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-link)' }}
                  >
                    Forgot password?
                  </a>
                </div>
                <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input-base"
                    placeholder="••••••••••••"
                    style={{ paddingRight: '40px', width: '100%' }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    title={showPassword ? 'Hide password' : 'Show password'}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    style={{
                      position: 'absolute',
                      right: '10px',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      color: 'var(--color-text-muted)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '4px'
                    }}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
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
                Sign In to Chambers
              </Button>
            </form>

            {/* Register as Advocate Option */}
            <div
              style={{
                marginTop: 'var(--space-xl)',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                border: '1px solid var(--color-border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-sm) var(--space-md)',
                textAlign: 'center'
              }}
            >
              <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                New legal practitioner or chamber?
              </div>
              <button
                type="button"
                onClick={() => setIsRegisterOpen(true)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--color-accent-700)',
                  fontWeight: 600,
                  fontSize: 'var(--text-body)',
                  cursor: 'pointer',
                  textDecoration: 'underline'
                }}
              >
                Register as Advocate →
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handle2FASubmit}>
            <div style={{ marginBottom: 'var(--space-lg)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-xs)' }}>
                <ShieldCheck size={20} color="var(--color-accent-500)" />
                <span style={{ fontSize: 'var(--text-h3)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                  Two-Step Verification
                  <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
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
                  fontSize: '22px',
                  fontFamily: 'var(--font-mono)'
                }}
              />
              <div style={{ marginTop: '8px', fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)', textAlign: 'center' }}>
                Simulated 2FA code: <strong>123456</strong>
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
              onClick={() => { setError(''); setStep('credentials'); }}
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
      </div>

      {/* Multi-Step Advocate Registration Modal */}
      {isRegisterOpen && (
        <RegisterAdvocateModal
          onClose={() => setIsRegisterOpen(false)}
          onComplete={() => {
            setIsRegisterOpen(false);
            onLoginSuccess();
          }}
        />
      )}
    </div>
  );
};
