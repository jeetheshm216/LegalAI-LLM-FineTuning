import React, { useState } from 'react';
import { 
  Shield, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight, 
  ArrowLeft, 
  Smartphone, 
  Mail, 
  Lock, 
  KeyRound, 
  Info,
  Check,
  QrCode,
  Eye,
  EyeOff
} from 'lucide-react';
import { Button } from '../common/Button';
import { STATE_BAR_COUNCILS, VerificationStatus } from '../../types/authTypes';
import { verificationService, PROTOTYPE_DISCLAIMER } from '../../services/verificationService';
import { authService } from '../../services/authService';

export const RegisterAdvocateModal = ({ onClose, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1); // 1 to 6
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Step 1: Professional Identity
  const [fullName, setFullName] = useState('');
  const [stateBarCouncil, setStateBarCouncil] = useState(STATE_BAR_COUNCILS[0]);
  const [enrollmentNumber, setEnrollmentNumber] = useState('');
  const [verificationResult, setVerificationResult] = useState(null);

  // Step 2: Mobile
  const [mobileNumber, setMobileNumber] = useState('');
  const [mobileOtp, setMobileOtp] = useState('');
  const [mobileOtpSent, setMobileOtpSent] = useState(false);
  const [mobileVerified, setMobileVerified] = useState(false);

  // Step 3: Email
  const [email, setEmail] = useState('');
  const [emailCode, setEmailCode] = useState('');
  const [emailCodeSent, setEmailCodeSent] = useState(false);
  const [emailVerified, setEmailVerified] = useState(false);

  // Step 4: Password
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Step 5: 2FA
  const [twoFactorCode, setTwoFactorCode] = useState('');
  const [twoFactorConfigured, setTwoFactorConfigured] = useState(false);

  // Step 1 Handler: Verify Advocate Credentials
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

  // Step 2 Handler: Send & Verify Mobile OTP
  const handleSendMobileOtp = () => {
    if (!mobileNumber || mobileNumber.length < 10) {
      setError('Please enter a valid 10-digit mobile number.');
      return;
    }
    setError('');
    setMobileOtpSent(true);
  };

  const handleVerifyMobileOtp = () => {
    if (mobileOtp !== '123456' && mobileOtp !== '888888') {
      setError('Invalid OTP code. Please enter the simulated demo code: 123456');
      return;
    }
    setError('');
    setMobileVerified(true);
  };

  // Step 3 Handler: Send & Verify Email
  const handleSendEmailCode = () => {
    if (!email || !email.includes('@')) {
      setError('Please enter a valid chambers email address.');
      return;
    }
    setError('');
    setEmailCodeSent(true);
  };

  const handleVerifyEmailCode = () => {
    if (emailCode !== '123456' && emailCode !== '888888') {
      setError('Invalid code. Please enter the simulated verification code: 123456');
      return;
    }
    setError('');
    setEmailVerified(true);
  };

  // Step 4: Password Validation Check
  const hasMinLength = password.length >= 8;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[^A-Za-z0-9]/.test(password);
  const passwordsMatch = password && password === confirmPassword;
  const isPasswordValid = hasMinLength && hasUpper && hasLower && hasNumber && hasSpecial && passwordsMatch;

  // Step 5 Handler: Complete 2FA
  const handleVerify2FACode = () => {
    if (twoFactorCode !== '123456' && twoFactorCode !== '888888') {
      setError('Invalid 2FA code. Please enter simulated code: 123456');
      return;
    }
    setError('');
    setTwoFactorConfigured(true);
    setCurrentStep(6);
  };

  // Step 6 Handler: Final Registration Submission
  const handleCompleteRegistration = async () => {
    setLoading(true);
    setError('');
    try {
      await authService.registerAdvocate({
        fullName,
        stateBarCouncil,
        enrollmentNumber,
        email,
        password,
        mobileNumber,
        verificationResult
      });
      if (onComplete) {
        onComplete();
      }
    } catch (err) {
      setError(err.message || 'Registration could not be completed.');
    } finally {
      setLoading(false);
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
          maxWidth: '560px',
          maxHeight: '90vh',
          overflowY: 'auto',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border-subtle)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-xl)',
          boxShadow: 'var(--elevation-3)'
        }}
      >
        {/* Step Indicator Header */}
        <div style={{ marginBottom: 'var(--space-lg)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
            <span style={{ fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-accent-700)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Step {currentStep} of 6 — Advocate Onboarding
            </span>
            <button
              onClick={onClose}
              style={{ background: 'none', border: 'none', color: 'var(--color-text-muted)', cursor: 'pointer', fontSize: '18px' }}
            >
              ✕
            </button>
          </div>

          <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-ink-700)', margin: 0 }}>
            {currentStep === 1 && 'Professional Advocate Verification'}
            {currentStep === 2 && 'Chambers Mobile Verification'}
            {currentStep === 3 && 'Verified Email Address'}
            {currentStep === 4 && 'Account Security & Credentials'}
            {currentStep === 5 && 'Two-Factor Authentication (2FA)'}
            {currentStep === 6 && 'LegalAI Chambers Access'}
          </h2>

          <div style={{ display: 'flex', gap: '4px', marginTop: 'var(--space-sm)' }}>
            {[1, 2, 3, 4, 5, 6].map((st) => (
              <div
                key={st}
                style={{
                  flex: 1,
                  height: '4px',
                  borderRadius: '2px',
                  backgroundColor: st <= currentStep ? 'var(--color-accent-500)' : 'var(--color-border-subtle)',
                  transition: 'background-color 0.2s ease'
                }}
              />
            ))}
          </div>
        </div>

        {/* Prototype Disclaimer Banner */}
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

        {/* STEP 1: Professional Identity */}
        {currentStep === 1 && (
          <form onSubmit={handleVerifyAdvocate}>
            <div style={{ marginBottom: 'var(--space-md)' }}>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Advocate Full Name (As registered in Bar roll)
                <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Adv. Elena Vance"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
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
                {STATE_BAR_COUNCILS.map((council) => (
                  <option key={council} value={council}>
                    {council}
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
                placeholder="e.g. TN/1942/2018 or D/3819/2015"
                value={enrollmentNumber}
                onChange={(e) => setEnrollmentNumber(e.target.value)}
                className="input-base"
                style={{ fontFamily: 'var(--font-mono)' }}
              />
              <div style={{ marginTop: '4px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                Demo enrollments: <strong>TN/1942/2018</strong> (Elena Vance) or <strong>D/3819/2015</strong> (Rajesh Kumar)
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
                    {verificationResult.verifiedName} • {verificationResult.enrollmentNumber} ({verificationResult.stateBarCouncil})
                  </div>
                </div>
              </div>
            )}

            {verificationResult?.status === VerificationStatus.NEEDS_REVIEW && (
              <div
                style={{
                  backgroundColor: 'var(--color-warning-wash)',
                  border: '1px solid var(--color-warning-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--space-sm)',
                  marginBottom: 'var(--space-lg)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-sm)'
                }}
              >
                <AlertCircle size={20} color="var(--color-warning-text)" />
                <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-warning-text)' }}>
                  Your professional credentials require manual review before chambers access can be authorized.
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
                  onClick={() => { setError(''); setCurrentStep(2); }}
                >
                  Proceed to Mobile Verification
                </Button>
              )}
            </div>
          </form>
        )}

        {/* STEP 2: Mobile Verification */}
        {currentStep === 2 && (
          <div>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)' }}>
              Enter your registered mobile number for urgent hearing notices and dual-channel verification.
            </p>

            <div style={{ marginBottom: 'var(--space-md)' }}>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Advocate Mobile Number
                <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
              </label>
              <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
                <input
                  type="tel"
                  placeholder="+91 98765 43210"
                  value={mobileNumber}
                  disabled={mobileVerified}
                  onChange={(e) => setMobileNumber(e.target.value)}
                  className="input-base"
                  style={{ flex: 1 }}
                />
                {!mobileVerified && (
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={handleSendMobileOtp}
                  >
                    {mobileOtpSent ? 'Resend OTP' : 'Send OTP'}
                  </Button>
                )}
              </div>
            </div>

            {mobileOtpSent && !mobileVerified && (
              <div style={{ marginBottom: 'var(--space-lg)' }}>
                <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                  6-Digit Mobile OTP
                  <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
                </label>
                <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
                  <input
                    type="text"
                    maxLength={6}
                    placeholder="123456"
                    value={mobileOtp}
                    onChange={(e) => setMobileOtp(e.target.value)}
                    className="input-base"
                    style={{ letterSpacing: '0.2em', fontFamily: 'var(--font-mono)' }}
                  />
                  <Button type="button" variant="primary" onClick={handleVerifyMobileOtp}>
                    Verify OTP
                  </Button>
                </div>
                <div style={{ marginTop: '4px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                  Simulated OTP code: <strong>123456</strong>
                </div>
              </div>
            )}

            {mobileVerified && (
              <div
                style={{
                  backgroundColor: 'var(--color-success-wash)',
                  border: '1px solid var(--color-success-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--space-sm)',
                  marginBottom: 'var(--space-lg)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-xs)',
                  color: 'var(--color-success-text)',
                  fontSize: 'var(--text-body)',
                  fontWeight: 500
                }}
              >
                <CheckCircle2 size={18} />
                <span>✓ Mobile number verified (+91 {mobileNumber})</span>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button variant="secondary" icon={ArrowLeft} onClick={() => setCurrentStep(1)}>
                Back
              </Button>
              <Button
                variant="primary"
                disabled={!mobileVerified}
                icon={ArrowRight}
                iconPosition="right"
                onClick={() => { setError(''); setCurrentStep(3); }}
              >
                Next: Email Verification
              </Button>
            </div>
          </div>
        )}

        {/* STEP 3: Email Verification */}
        {currentStep === 3 && (
          <div>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)' }}>
              Provide your official chambers email address for case filings, encrypted transcripts, and court alerts.
            </p>

            <div style={{ marginBottom: 'var(--space-md)' }}>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Chambers Email Address
                <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
              </label>
              <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
                <input
                  type="email"
                  placeholder="advocate@chambers.org"
                  value={email}
                  disabled={emailVerified}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-base"
                  style={{ flex: 1 }}
                />
                {!emailVerified && (
                  <Button type="button" variant="secondary" onClick={handleSendEmailCode}>
                    {emailCodeSent ? 'Resend Code' : 'Send Code'}
                  </Button>
                )}
              </div>
            </div>

            {emailCodeSent && !emailVerified && (
              <div style={{ marginBottom: 'var(--space-lg)' }}>
                <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                  Verification Code
                  <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
                </label>
                <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
                  <input
                    type="text"
                    maxLength={6}
                    placeholder="123456"
                    value={emailCode}
                    onChange={(e) => setEmailCode(e.target.value)}
                    className="input-base"
                    style={{ letterSpacing: '0.2em', fontFamily: 'var(--font-mono)' }}
                  />
                  <Button type="button" variant="primary" onClick={handleVerifyEmailCode}>
                    Verify Email
                  </Button>
                </div>
                <div style={{ marginTop: '4px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                  Simulated verification code: <strong>123456</strong>
                </div>
              </div>
            )}

            {emailVerified && (
              <div
                style={{
                  backgroundColor: 'var(--color-success-wash)',
                  border: '1px solid var(--color-success-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--space-sm)',
                  marginBottom: 'var(--space-lg)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-xs)',
                  color: 'var(--color-success-text)',
                  fontSize: 'var(--text-body)',
                  fontWeight: 500
                }}
              >
                <CheckCircle2 size={18} />
                <span>✓ Chambers email verified ({email})</span>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button variant="secondary" icon={ArrowLeft} onClick={() => setCurrentStep(2)}>
                Back
              </Button>
              <Button
                variant="primary"
                disabled={!emailVerified}
                icon={ArrowRight}
                iconPosition="right"
                onClick={() => { setError(''); setCurrentStep(4); }}
              >
                Next: Account Security
              </Button>
            </div>
          </div>
        )}

        {/* STEP 4: Password Creation */}
        {currentStep === 4 && (
          <div>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)' }}>
              Create a high-entropy password to protect confidential client records and privileged drafts.
            </p>

            <div style={{ marginBottom: 'var(--space-md)' }}>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Master Chambers Password
                <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
              </label>
              <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-base"
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

            <div style={{ marginBottom: 'var(--space-md)' }}>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Confirm Master Password
                <span style={{ color: 'var(--color-error-text, #C0392B)', marginLeft: '4px', fontWeight: 600 }}>*</span>
              </label>
              <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="••••••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="input-base"
                  style={{ paddingRight: '40px', width: '100%' }}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword((prev) => !prev)}
                  title={showConfirmPassword ? 'Hide password' : 'Show password'}
                  aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
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
                  {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {/* Password Criteria Checklist */}
            <div
              style={{
                backgroundColor: 'var(--color-bg-surface-sunken)',
                padding: 'var(--space-sm)',
                borderRadius: 'var(--radius-md)',
                marginBottom: 'var(--space-lg)',
                fontSize: '12px'
              }}
            >
              <div style={{ fontWeight: 600, marginBottom: '6px', color: 'var(--color-text-secondary)' }}>
                Security Requirements:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: hasMinLength ? 'var(--color-success-text)' : 'var(--color-text-muted)' }}>
                  <Check size={14} /> 8+ Characters
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: hasUpper ? 'var(--color-success-text)' : 'var(--color-text-muted)' }}>
                  <Check size={14} /> Uppercase Letter (A-Z)
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: hasLower ? 'var(--color-success-text)' : 'var(--color-text-muted)' }}>
                  <Check size={14} /> Lowercase Letter (a-z)
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: hasNumber ? 'var(--color-success-text)' : 'var(--color-text-muted)' }}>
                  <Check size={14} /> Number (0-9)
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: hasSpecial ? 'var(--color-success-text)' : 'var(--color-text-muted)' }}>
                  <Check size={14} /> Special Character (!@#$)
                </div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  color: passwordsMatch
                    ? 'var(--color-success-text)'
                    : (password && confirmPassword ? 'var(--color-error-text)' : 'var(--color-text-muted)')
                }}>
                  <Check size={14} /> {passwordsMatch ? 'Passwords Match' : (password && confirmPassword ? 'Passwords Do Not Match' : 'Passwords Match')}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button variant="secondary" icon={ArrowLeft} onClick={() => setCurrentStep(3)}>
                Back
              </Button>
              <Button
                variant="primary"
                disabled={!isPasswordValid}
                icon={ArrowRight}
                iconPosition="right"
                onClick={() => { setError(''); setCurrentStep(5); }}
              >
                Next: Configure 2FA
              </Button>
            </div>
          </div>
        )}

        {/* STEP 5: Two-Factor Authentication Setup */}
        {currentStep === 5 && (
          <div>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)' }}>
              Scan the QR code with your authenticator app (Google Authenticator, Microsoft Authenticator, or 1Password).
            </p>

            {/* QR Mockup */}
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
                  width: '140px',
                  height: '140px',
                  backgroundColor: '#FFFFFF',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px solid var(--color-border-default)'
                }}
              >
                <QrCode size={110} color="#171E26" />
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
                <Button type="button" variant="primary" onClick={handleVerify2FACode}>
                  Confirm 2FA
                </Button>
              </div>
              <div style={{ marginTop: '4px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                Simulated 2FA code: <strong>123456</strong>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button variant="secondary" icon={ArrowLeft} onClick={() => setCurrentStep(4)}>
                Back
              </Button>
            </div>
          </div>
        )}

        {/* STEP 6: Final Verification Status & Access Granted */}
        {currentStep === 6 && (
          <div>
            <div
              style={{
                textAlign: 'center',
                padding: 'var(--space-lg) var(--space-md)',
                backgroundColor: 'var(--color-success-wash)',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--color-success-border)',
                marginBottom: 'var(--space-lg)'
              }}
            >
              <ShieldCheck size={48} color="var(--color-success-text)" style={{ marginBottom: 'var(--space-xs)' }} />
              <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: '20px', color: 'var(--color-success-text)', margin: '0 0 6px 0' }}>
                LEGALAI ACCESS GRANTED
              </h3>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-success-text)', margin: 0 }}>
                Advocate credentials and dual-factor security successfully verified.
              </p>
            </div>

            {/* Checklist */}
            <div
              style={{
                border: '1px solid var(--color-border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-sm) var(--space-md)',
                marginBottom: 'var(--space-xl)',
                fontSize: 'var(--text-caption)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Professional Advocate Roll:</span>
                <span style={{ fontWeight: 600, color: 'var(--color-success-text)' }}>✓ {stateBarCouncil}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Enrollment Registration:</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{enrollmentNumber}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Mobile Verification:</span>
                <span style={{ fontWeight: 600, color: 'var(--color-success-text)' }}>✓ Verified</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Chambers Email:</span>
                <span style={{ fontWeight: 600, color: 'var(--color-success-text)' }}>✓ {email}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Two-Factor Authentication:</span>
                <span style={{ fontWeight: 600, color: 'var(--color-success-text)' }}>✓ Enabled</span>
              </div>
            </div>

            <Button
              type="button"
              variant="primary"
              fullWidth
              loading={loading}
              onClick={handleCompleteRegistration}
            >
              Enter Chambers Dashboard
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
