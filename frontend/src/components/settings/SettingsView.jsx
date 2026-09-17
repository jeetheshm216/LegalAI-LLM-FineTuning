import React, { useState } from 'react';
import { 
  User, 
  Shield, 
  ShieldCheck,
  Sun, 
  Eye, 
  Sparkles, 
  LogOut, 
  Check, 
  KeyRound, 
  Monitor, 
  Smartphone,
  CheckCircle2,
  XCircle,
  Keyboard,
  Info,
  Laptop
} from 'lucide-react';
import { Button } from '../common/Button';
import { PROTOTYPE_DISCLAIMER } from '../../services/verificationService';

export const SettingsView = ({ 
  currentUser, 
  themeMode, 
  onThemeChange, 
  onLogout,
  onUpdateUserSettings 
}) => {
  const [activeSection, setActiveSection] = useState('appearance'); // 'account' | 'verification' | 'security' | 'appearance' | 'accessibility' | 'ai'
  const [fontSize, setFontSize] = useState('default');
  const [contrast, setContrast] = useState('default');
  const [reducedMotion, setReducedMotion] = useState(false);
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(currentUser?.twoFactorEnabled ?? true);
  const [aiLength, setAiLength] = useState('Standard');
  const [aiCitations, setAiCitations] = useState('Collapsed');

  const handleContrastToggle = (isHigh) => {
    const val = isHigh ? 'high' : 'default';
    setContrast(val);
    document.documentElement.setAttribute('data-contrast', val);
  };

  const handleMotionToggle = (isReduced) => {
    setReducedMotion(isReduced);
    document.documentElement.setAttribute('data-motion', isReduced ? 'reduced' : 'normal');
  };

  const sections = [
    { id: 'account', label: 'Account Profile', icon: User },
    { id: 'verification', label: 'Professional Verification', icon: ShieldCheck },
    { id: 'security', label: 'Security & 2FA', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Sun },
    { id: 'accessibility', label: 'Accessibility', icon: Eye },
    { id: 'ai', label: 'AI Preferences', icon: Sparkles }
  ];

  return (
    <div className="container" style={{ padding: 'var(--space-xl) var(--space-md)' }}>
      <div style={{ marginBottom: 'var(--space-lg)' }}>
        <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h1)', color: 'var(--color-text-primary)' }}>
          Chambers & Application Settings
        </h1>
        <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
          Security keys, appearance preferences, accessibility features, and AI synthesis parameters
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gap: 'var(--space-xl)' }} className="settings-layout">
        
        {/* Left Vertical Sub-Nav (§16) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {sections.map((sec) => {
            const Icon = sec.icon;
            const isActive = activeSection === sec.id;
            return (
              <button
                key={sec.id}
                onClick={() => setActiveSection(sec.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-xs)',
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-md)',
                  border: 'none',
                  backgroundColor: isActive ? 'var(--color-bg-surface-sunken)' : 'transparent',
                  color: isActive ? 'var(--color-ink-700)' : 'var(--color-text-secondary)',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: 'var(--text-caption)',
                  cursor: 'pointer',
                  textAlign: 'left'
                }}
              >
                <Icon size={16} color={isActive ? 'var(--color-ink-700)' : 'var(--color-text-secondary)'} />
                <span>{sec.label}</span>
              </button>
            );
          })}

          <div style={{ borderTop: '1px solid var(--color-border-subtle)', marginTop: 'var(--space-xl)', paddingTop: 'var(--space-md)' }}>
            <button
              onClick={onLogout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-xs)',
                padding: '10px 12px',
                borderRadius: 'var(--radius-md)',
                border: 'none',
                background: 'none',
                color: 'var(--color-error-text)',
                fontWeight: 500,
                fontSize: 'var(--text-caption)',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              <LogOut size={16} />
              <span>Sign out of Chambers</span>
            </button>
          </div>
        </div>

        {/* Right Content Panel (§16) */}
        <div className="card-base" style={{ padding: 'var(--space-xl)' }}>
          
          {/* Section: Appearance */}
          {activeSection === 'appearance' && (
            <div>
              <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', marginBottom: 'var(--space-xs)' }}>
                Appearance & Theme
              </h2>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-lg)' }}>
                Choose how Legal AI renders. Dark mode uses a dedicated low-eye-strain charcoal palette.
              </p>

              <div style={{ marginBottom: 'var(--space-xl)' }}>
                <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 'var(--space-xs)' }}>
                  Theme Mode
                </label>

                {/* 3-way Segmented Control per §16 */}
                <div
                  style={{
                    display: 'inline-flex',
                    backgroundColor: 'var(--color-bg-surface-sunken)',
                    padding: '4px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--color-border-default)'
                  }}
                >
                  {['light', 'dark', 'system'].map((m) => {
                    const isSelected = themeMode === m;
                    return (
                      <button
                        key={m}
                        onClick={() => onThemeChange(m)}
                        style={{
                          padding: '6px 16px',
                          borderRadius: 'var(--radius-md)',
                          border: 'none',
                          backgroundColor: isSelected ? 'var(--color-bg-surface)' : 'transparent',
                          boxShadow: isSelected ? 'var(--elevation-1)' : 'none',
                          color: isSelected ? 'var(--color-ink-700)' : 'var(--color-text-secondary)',
                          fontSize: 'var(--text-caption)',
                          fontWeight: isSelected ? 600 : 500,
                          cursor: 'pointer',
                          textTransform: 'capitalize'
                        }}
                      >
                        {m}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Section: Account Profile */}
          {activeSection === 'account' && (
            <div>
              <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', marginBottom: 'var(--space-xs)' }}>
                Advocate Profile & Credentials
              </h2>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-lg)' }}>
                Credentials verified with High Court Registry for electronic filing and bar authorization.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)', marginBottom: 'var(--space-md)' }}>
                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                    Full Name & Title
                  </label>
                  <input type="text" readOnly value={currentUser?.name || "Adv. Elena Vance"} className="input-base" />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                    Chambers Email
                  </label>
                  <input type="email" readOnly value={currentUser?.email || "e.vance@vance-legal.org"} className="input-base" />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)', marginBottom: 'var(--space-lg)' }}>
                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                    Bar Enrollment Number
                  </label>
                  <input type="text" readOnly value={currentUser?.barNumber || "NY-BAR-481920"} className="input-base" style={{ fontFamily: 'var(--font-mono)' }} />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                    Chambers Entity
                  </label>
                  <input type="text" readOnly value={currentUser?.chambers || "Vance & Associates"} className="input-base" />
                </div>
              </div>
            </div>
          )}

          {/* Section: Professional Verification */}
          {activeSection === 'verification' && (
            <div>
              <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', marginBottom: 'var(--space-xs)' }}>
                Professional Advocate Verification
              </h2>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-lg)' }}>
                Statutory verification of legal licensure and bar credentials for privileged chambers access.
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

              {/* Status Overview Card */}
              <div
                style={{
                  backgroundColor: 'var(--color-bg-surface-sunken)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-lg)',
                  padding: 'var(--space-lg)',
                  marginBottom: 'var(--space-xl)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', marginBottom: 'var(--space-md)' }}>
                  <div
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--color-success-wash)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <CheckCircle2 size={22} color="var(--color-success-text)" />
                  </div>
                  <div>
                    <div style={{ fontSize: 'var(--text-body)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                      Advocate Identity Verified
                    </div>
                    <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-success-text)' }}>
                      Professional verification valid for chambers session
                    </div>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
                  <div>
                    <div style={{ fontSize: 'var(--text-label)', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>
                      State Bar Council
                    </div>
                    <div style={{ fontSize: 'var(--text-body)', fontWeight: 500 }}>
                      {currentUser?.state_bar_council || 'Bar Council of Tamil Nadu & Puducherry'}
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: 'var(--text-label)', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>
                      Enrollment Number
                    </div>
                    <div style={{ fontSize: 'var(--text-body)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                      {(() => {
                        const num = currentUser?.enrollment_number || currentUser?.barNumber || 'TN/1942/2018';
                        const parts = num.split('/');
                        if (parts.length === 3) {
                          return `${parts[0]}/••••/${parts[2]}`;
                        }
                        return num.slice(0, 3) + '••••' + num.slice(-4);
                      })()}
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: 'var(--text-label)', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>
                      Verification Status
                    </div>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--color-success-text)', fontWeight: 600, fontSize: 'var(--text-caption)' }}>
                      <Check size={14} /> Verified Advocate
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: 'var(--text-label)', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>
                      Mobile Verification
                    </div>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--color-success-text)', fontWeight: 500, fontSize: 'var(--text-caption)' }}>
                      <Check size={14} /> Verified
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: 'var(--text-label)', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>
                      Chambers Email
                    </div>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--color-success-text)', fontWeight: 500, fontSize: 'var(--text-caption)' }}>
                      <Check size={14} /> Verified ({currentUser?.email || 'e.vance@vance-legal.org'})
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: 'var(--text-label)', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>
                      Two-Factor Authentication
                    </div>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--color-success-text)', fontWeight: 500, fontSize: 'var(--text-caption)' }}>
                      <Check size={14} /> Enabled
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Section: Security & 2FA */}
          {activeSection === 'security' && (
            <div>
              <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', marginBottom: 'var(--space-xs)' }}>
                Security & Authentication Audit
              </h2>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-lg)' }}>
                Multi-factor protection and session monitoring for privileged attorney-client work product.
              </p>

              {/* 2FA Card */}
              <div
                style={{
                  padding: 'var(--space-md)',
                  backgroundColor: 'var(--color-bg-surface-sunken)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--color-border-subtle)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 'var(--space-xl)'
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                    Two-Factor Authentication (2FA)
                  </div>
                  <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                    Requires a 6-digit TOTP code during every new browser session.
                  </div>
                </div>

                <Button
                  variant={twoFactorEnabled ? "secondary" : "primary"}
                  size="sm"
                  onClick={() => setTwoFactorEnabled(!twoFactorEnabled)}
                >
                  {twoFactorEnabled ? "Enabled (Configured)" : "Enable 2FA"}
                </Button>
              </div>

              {/* Active Sessions UI (§21) */}
              <div style={{ marginBottom: 'var(--space-xl)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
                  <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', margin: 0 }}>
                    Active Sessions
                  </h3>
                  <button
                    type="button"
                    onClick={() => alert('Other remote sessions have been terminated. Current device remains active.')}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--color-text-link)',
                      fontSize: 'var(--text-caption)',
                      cursor: 'pointer',
                      textDecoration: 'underline'
                    }}
                  >
                    Sign out other sessions
                  </button>
                </div>
                <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-sm)' }}>
                  Devices currently authenticated to your chambers account.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: 'var(--space-sm) var(--space-md)',
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--color-border-subtle)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                      <Laptop size={18} color="var(--color-accent-500)" />
                      <div>
                        <div style={{ fontSize: 'var(--text-body)', fontWeight: 500 }}>Current Device</div>
                        <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                          Windows • Chrome Browser • Chennai, India
                        </div>
                      </div>
                    </div>
                    <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-success-text)', fontWeight: 600 }}>
                      Active now
                    </span>
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: 'var(--space-sm) var(--space-md)',
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--color-border-subtle)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                      <Laptop size={18} color="var(--color-text-muted)" />
                      <div>
                        <div style={{ fontSize: 'var(--text-body)', fontWeight: 500 }}>Chambers Laptop</div>
                        <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                          MacBook Pro • Safari • New Delhi, India
                        </div>
                      </div>
                    </div>
                    <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)' }}>
                      2 hours ago
                    </span>
                  </div>
                </div>
              </div>

              {/* Login History Table (§16) */}
              <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', marginBottom: 'var(--space-xs)' }}>
                Recent Access History
              </h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-caption)', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
                    <th style={{ padding: '8px 0', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Timestamp</th>
                    <th style={{ padding: '8px 0', color: 'var(--color-text-secondary)', fontWeight: 500 }}>IP Address</th>
                    <th style={{ padding: '8px 0', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Device / Client</th>
                    <th style={{ padding: '8px 0', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {currentUser?.loginHistory?.map((log) => (
                    <tr key={log.id} style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
                      <td style={{ padding: '8px 0', fontFamily: 'var(--font-mono)' }}>{log.timestamp}</td>
                      <td style={{ padding: '8px 0', fontFamily: 'var(--font-mono)' }}>{log.ip}</td>
                      <td style={{ padding: '8px 0' }}>{log.device}</td>
                      <td style={{ padding: '8px 0' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: log.status === 'success' ? 'var(--color-success-text)' : 'var(--color-error-text)' }}>
                          {log.status === 'success' ? <CheckCircle2 size={13} /> : <XCircle size={13} />}
                          {log.status === 'success' ? 'Authorized' : 'Blocked'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Section: Accessibility (§16, §18) */}
          {activeSection === 'accessibility' && (
            <div>
              <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', marginBottom: 'var(--space-xs)' }}>
                Accessibility & Visual Assistance
              </h2>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-lg)' }}>
                Full WCAG 2.1 AA/AAA support, live text scaling, high-contrast borders, and motion reduction.
              </p>

              {/* High Contrast Mode Toggle */}
              <div style={{ marginBottom: 'var(--space-lg)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 'var(--text-body)' }}>High Contrast Mode</div>
                    <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                      Raises subtle borders to strong emphasis and enhances secondary copy readability.
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={contrast === 'high'}
                    onChange={(e) => handleContrastToggle(e.target.checked)}
                    style={{ accentColor: 'var(--color-accent-500)', width: '18px', height: '18px', cursor: 'pointer' }}
                  />
                </div>
              </div>

              {/* Reduced Motion Toggle */}
              <div style={{ marginBottom: 'var(--space-xl)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 'var(--text-body)' }}>Reduced Motion</div>
                    <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                      Collapses all non-essential transitions and disables animated processing dots.
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={reducedMotion}
                    onChange={(e) => handleMotionToggle(e.target.checked)}
                    style={{ accentColor: 'var(--color-accent-500)', width: '18px', height: '18px', cursor: 'pointer' }}
                  />
                </div>
              </div>

              {/* Keyboard Navigation Shortcuts Guide */}
              <div style={{ backgroundColor: 'var(--color-bg-surface-sunken)', padding: 'var(--space-md)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, fontSize: 'var(--text-caption)', marginBottom: 'var(--space-xs)' }}>
                  <Keyboard size={15} />
                  <span>Keyboard Navigation Shortcuts</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                  <div><kbd style={{ fontFamily: 'var(--font-mono)', padding: '1px 5px', border: '1px solid var(--color-border-default)', borderRadius: '3px' }}>Tab</kbd> Move focus forward</div>
                  <div><kbd style={{ fontFamily: 'var(--font-mono)', padding: '1px 5px', border: '1px solid var(--color-border-default)', borderRadius: '3px' }}>Shift+Tab</kbd> Move focus backward</div>
                  <div><kbd style={{ fontFamily: 'var(--font-mono)', padding: '1px 5px', border: '1px solid var(--color-border-default)', borderRadius: '3px' }}>Esc</kbd> Close open modal / preview</div>
                  <div><kbd style={{ fontFamily: 'var(--font-mono)', padding: '1px 5px', border: '1px solid var(--color-border-default)', borderRadius: '3px' }}>Enter</kbd> Submit search / prompt</div>
                </div>
              </div>
            </div>
          )}

          {/* Section: AI Preferences (§16) */}
          {activeSection === 'ai' && (
            <div>
              <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', marginBottom: 'var(--space-xs)' }}>
                AI Synthesis Preferences
              </h2>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-lg)' }}>
                Tailor synthesis depth, citation visibility, and automatic case scoping.
              </p>

              <div style={{ marginBottom: 'var(--space-lg)' }}>
                <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, marginBottom: '6px' }}>
                  Default Response Length
                </label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {['Concise', 'Standard', 'Detailed'].map((len) => (
                    <button
                      key={len}
                      onClick={() => setAiLength(len)}
                      style={{
                        padding: '6px 12px',
                        borderRadius: 'var(--radius-sm)',
                        border: aiLength === len ? '1px solid var(--color-ai-500)' : '1px solid var(--color-border-default)',
                        backgroundColor: aiLength === len ? 'var(--color-ai-100)' : 'var(--color-bg-surface)',
                        color: aiLength === len ? 'var(--color-ai-500)' : 'var(--color-text-secondary)',
                        fontSize: 'var(--text-caption)',
                        fontWeight: 500,
                        cursor: 'pointer'
                      }}
                    >
                      {len}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ marginBottom: 'var(--space-lg)' }}>
                <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, marginBottom: '6px' }}>
                  Citation Cards Presentation
                </label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {['Collapsed', 'Inline Expanded'].map((cit) => (
                    <button
                      key={cit}
                      onClick={() => setAiCitations(cit)}
                      style={{
                        padding: '6px 12px',
                        borderRadius: 'var(--radius-sm)',
                        border: aiCitations === cit ? '1px solid var(--color-ai-500)' : '1px solid var(--color-border-default)',
                        backgroundColor: aiCitations === cit ? 'var(--color-ai-100)' : 'var(--color-bg-surface)',
                        color: aiCitations === cit ? 'var(--color-ai-500)' : 'var(--color-text-secondary)',
                        fontSize: 'var(--text-caption)',
                        fontWeight: 500,
                        cursor: 'pointer'
                      }}
                    >
                      {cit}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

        </div>

      </div>

      <style>{`
        @media (max-width: 800px) {
          .settings-layout {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};
