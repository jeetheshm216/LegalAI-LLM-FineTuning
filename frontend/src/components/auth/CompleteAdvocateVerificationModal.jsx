import React, { useState } from 'react';
import { 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight, 
  Info, 
  Check, 
  QrCode 
} from 'lucide-react';
import { Button } from '../common/Button';
import { STATE_BAR_COUNCILS, VerificationStatus } from '../../types/authTypes.js';
import { verificationService, PROTOTYPE_DISCLAIMER } from '../../services/verificationService.js';
import { authService } from '../../services/authService.js';

export const CompleteAdvocateVerificationModal = ({ currentUser, profile, onClose, onComplete }) => {
  const [step, setStep] = useState(1); // 1: Bar Credentials, 2: 2FA TOTP, 3: Success
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [fullName, setFullName] = useState(profile?.full_name || currentUser?.user_metadata?.full_name || '');
  const [stateBarCouncil, setStateBarCouncil] = useState(profile?.state_bar_council || currentUser?.user_metadata?.state_bar_council || STATE_BAR_COUNCILS[0]);
  const [enrollmentNumber, setEnrollmentNumber] = useState(profile?.enrollment_number || currentUser?.user_metadata?.enrollment_number || '');
  const [verificationResult, setVerificationResult] = useState(null);

  const [twoFactorCode, setTwoFactorCode] = useState('');

  const handleVerifyAdvocate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setVerificationResult(null);

    try {
      const result = await verificationService.verifyAdvocate({
        fullName,
        stateBarCouncil,
        enrollmentNumber
      });
      setVerificationResult(result);

      if (result.status === VerificationStatus.FAILED) {
        setError(result.message);
      }
    } catch (err) {
      setError('Verification service temporarily unavailable.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify2FACode = async () => {
    if (twoFactorCode !== '123456' && twoFactorCode !== '888888') {
      setError('Invalid 2FA code. Please enter simulated code: 123456');
      return;
    }
    setError('');
    setLoading(true);

    try {
      await authService.completeVerificationForCurrentUser({
        fullName,
        stateBarCouncil,
        enrollmentNumber
      });
      setLoading(false);
      if (onComplete) onComplete();
    } catch (err) {
      setLoading(false);
      setError(err.message || 'Could not complete verification.');
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(15, 23, 32, 0.65)',
        backdropFilter: 'blur(4px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-md)'
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '520px',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border-subtle)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-xl)',
          boxShadow: 'var(--elevation-3)'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
          <span style={{ fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-accent-700)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Advocate Verification Required
          </span>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--color-text-muted)', cursor: 'pointer', fontSize: '18px' }}
          >
            ✕
          </button>
        </div>

        <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-ink-700)', margin: '0 0 var(--space-xs) 0' }}>
          {step === 1 && 'Verify State Bar Credentials'}
          {step === 2 && 'Set Up Two-Factor Authentication (2FA)'}
        </h2>

        <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)' }}>
          Authenticated as <strong>{currentUser?.email || profile?.email}</strong>. LegalAI requires verified advocate eligibility before granting chambers access.
        </p>

        {/* Prototype Disclaimer */}
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

        {step === 1 && (
          <form onSubmit={handleVerifyAdvocate}>
            <div style={{ marginBottom: 'var(--space-md)' }}>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Full Name (As enrolled in Bar roll)
                <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Adv. Priya Sharma"
                className="input-base"
              />
            </div>

            <div style={{ marginBottom: 'var(--space-md)' }}>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                State Bar Council
                <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
              </label>
              <select
                value={stateBarCouncil}
                onChange={(e) => setStateBarCouncil(e.target.value)}
                className="input-base"
                style={{ cursor: 'pointer' }}
              >
                {STATE_BAR_COUNCILS.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ marginBottom: 'var(--space-lg)' }}>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Bar Registration / Enrolment Number
                <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
              </label>
              <input
                type="text"
                required
                value={enrollmentNumber}
                onChange={(e) => setEnrollmentNumber(e.target.value)}
                placeholder="e.g. TN/1942/2018 or MAH/5120/2017"
                className="input-base"
                style={{ fontFamily: 'var(--font-mono)' }}
              />
              <div style={{ marginTop: '4px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                Demo enrollments: <strong>TN/1942/2018</strong> or <strong>D/3819/2015</strong>
              </div>
            </div>

            {verificationResult?.status === VerificationStatus.VERIFIED && (
              <div
                style={{
                  backgroundColor: 'var(--color-success-wash)',
                  border: '1px solid var(--color-success-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--space-sm)',
                  marginBottom: 'var(--space-lg)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-sm)'
                }}
              >
                <CheckCircle2 size={20} color="var(--color-success-text)" />
                <div>
                  <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-success-text)' }}>
                    ✓ Advocate Identity Verified
                  </div>
                  <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-success-text)' }}>
                    {verificationResult.verifiedName} • {verificationResult.enrollmentNumber}
                  </div>
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
              <Button
                type="submit"
                variant={verificationResult?.status === VerificationStatus.VERIFIED ? 'secondary' : 'primary'}
                loading={loading}
              >
                Verify Advocate Credentials
              </Button>

              {verificationResult?.status === VerificationStatus.VERIFIED && (
                <Button
                  type="button"
                  variant="primary"
                  icon={ArrowRight}
                  iconPosition="right"
                  onClick={() => { setError(''); setStep(2); }}
                >
                  Proceed to 2FA Setup
                </Button>
              )}
            </div>
          </form>
        )}

        {step === 2 && (
          <div>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)' }}>
              Two-factor authentication is required for all legal chambers accounts to protect privileged work product.
            </p>

            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: 'var(--space-md)',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--color-border-subtle)',
                marginBottom: 'var(--space-md)'
              }}
            >
              <div
                style={{
                  width: '130px',
                  height: '130px',
                  backgroundColor: '#FFFFFF',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px solid var(--color-border-default)'
                }}
              >
                <QrCode size={100} color="#171E26" />
              </div>
              <div style={{ marginTop: '8px', fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--color-text-secondary)' }}>
                Secret Key: <strong>LEGAL-AI-CHAMBERS-AUTH</strong>
              </div>
            </div>

            <div style={{ marginBottom: 'var(--space-lg)' }}>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Enter 6-Digit Authenticator Code
                <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
              </label>
              <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
                <input
                  type="text"
                  maxLength={6}
                  placeholder="123456"
                  value={twoFactorCode}
                  onChange={(e) => setTwoFactorCode(e.target.value.replace(/\D/g, ''))}
                  className="input-base"
                  style={{ textAlign: 'center', letterSpacing: '0.25em', fontSize: '18px', fontFamily: 'var(--font-mono)' }}
                />
                <Button type="button" variant="primary" loading={loading} onClick={handleVerify2FACode}>
                  Confirm & Enter Chambers
                </Button>
              </div>
              <div style={{ marginTop: '4px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                Simulated 2FA code: <strong>123456</strong>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
