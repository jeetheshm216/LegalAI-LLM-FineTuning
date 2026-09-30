import React, { useState, useRef, useEffect } from 'react';
import { 
  Bell, 
  Settings as SettingsIcon, 
  Sun, 
  Moon, 
  Laptop, 
  Menu, 
  X, 
  User, 
  Shield, 
  LogOut,
  LayoutDashboard,
  Briefcase,
  Calendar,
  Sparkles,
  FileEdit,
  Receipt,
  Scale
} from 'lucide-react';

export const Header = ({ 
  activeView, 
  onNavigate, 
  themeMode, 
  onThemeChange, 
  currentUser, 
  onLogout 
}) => {
  const [profileOpen, setProfileOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const profileRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', shortLabel: 'Dashboard', icon: LayoutDashboard },
    { id: 'cases', label: 'Matters & Cases', shortLabel: 'Cases', icon: Briefcase },
    { id: 'calendar', label: 'Calendar', shortLabel: 'Calendar', icon: Calendar },
    { id: 'ai', label: 'LegalChat', shortLabel: 'LegalChat', icon: Sparkles, badge: 'AI' },
    { id: 'courtroom', label: 'Courtroom Simulator', shortLabel: 'Courtroom', icon: Scale, badge: 'Live' },
    { id: 'drafting', label: 'Drafting Studio', shortLabel: 'Drafting', icon: FileEdit },
    { id: 'billing', label: 'Billing & Ledger', shortLabel: 'Billing', icon: Receipt }
  ];

  const cycleTheme = () => {
    if (themeMode === 'light') onThemeChange('dark');
    else if (themeMode === 'dark') onThemeChange('system');
    else onThemeChange('light');
  };

  return (
    <header
      style={{
        height: 'var(--header-height, 64px)',
        backgroundColor: 'var(--color-bg-surface)',
        borderBottom: '1px solid var(--color-border-subtle)',
        position: 'sticky',
        top: 0,
        zIndex: 'var(--z-sticky-header)',
        width: '100%',
        boxShadow: '0 1px 3px rgba(15, 23, 32, 0.04)',
        transition: 'background-color var(--duration-default) var(--easing-standard)'
      }}
    >
      <div
        className="container"
        style={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 'var(--space-md)'
        }}
      >
        {/* Brand & Wordmark */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
          <button
            onClick={() => onNavigate('dashboard')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '6px 4px',
              borderRadius: 'var(--radius-md)'
            }}
            aria-label="Legal AI Home"
          >
            {/* Concept: "The Marked Page" */}
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                border: '1px solid var(--color-border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 1px 2px rgba(15, 23, 32, 0.05)',
                flexShrink: 0
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path 
                  d="M4 3H15L20 8V21H4V3Z" 
                  stroke="var(--color-ink-700)" 
                  strokeWidth="2" 
                  strokeLinejoin="round" 
                />
                <path 
                  d="M15 3V8H20" 
                  stroke="var(--color-accent-500)" 
                  strokeWidth="2" 
                  strokeLinejoin="round" 
                />
              </svg>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', textAlign: 'left' }}>
              <span
                style={{
                  fontFamily: 'var(--font-serif)',
                  fontSize: '17px',
                  fontWeight: 700,
                  color: 'var(--color-ink-900)',
                  letterSpacing: '-0.01em',
                  lineHeight: 1.2
                }}
              >
                Legal AI
              </span>
              <span
                className="desktop-chamber-tag"
                style={{
                  fontSize: '10px',
                  fontFamily: 'var(--font-sans)',
                  color: 'var(--color-text-muted)',
                  letterSpacing: '0.04em',
                  textTransform: 'uppercase',
                  fontWeight: 600
                }}
              >
                Chambers Suite
              </span>
            </div>
          </button>
        </div>

        {/* Desktop Primary Navigation: Modern Segmented Pill Island */}
        <nav
          className="desktop-nav"
          style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: 'var(--color-bg-surface-sunken)',
            border: '1px solid var(--color-border-subtle)',
            borderRadius: '9999px',
            padding: '3px 4px',
            gap: '2px',
            boxShadow: 'inset 0 1px 2px rgba(15, 23, 32, 0.04)'
          }}
        >
          {navItems.map((item) => {
            const isActive = activeView === item.id || 
              (item.id === 'cases' && activeView === 'case-detail') ||
              (item.id === 'drafting' && (activeView === 'drafting' || activeView === 'editor'));
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`nav-pill-btn ${isActive ? 'is-active' : ''}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '7px',
                  padding: '6px 13px',
                  borderRadius: '9999px',
                  border: 'none',
                  backgroundColor: isActive ? 'var(--color-bg-surface-raised)' : 'transparent',
                  color: isActive ? 'var(--color-ink-900)' : 'var(--color-text-secondary)',
                  fontFamily: 'var(--font-sans)',
                  fontSize: '13px',
                  fontWeight: isActive ? 600 : 500,
                  cursor: 'pointer',
                  position: 'relative',
                  whiteSpace: 'nowrap',
                  boxShadow: isActive ? '0 1px 3px rgba(15, 23, 32, 0.08), 0 1px 2px rgba(15, 23, 32, 0.04)' : 'none',
                  transition: 'all 0.15s cubic-bezier(0.2, 0.0, 0.0, 1.0)'
                }}
              >
                <Icon
                  size={15}
                  color={isActive ? (item.id === 'ai' ? 'var(--color-ai-500)' : 'var(--color-accent-700)') : 'var(--color-ink-300)'}
                  style={{
                    flexShrink: 0,
                    transition: 'color 0.15s ease'
                  }}
                />
                <span className="nav-label-full">{item.label}</span>
                <span className="nav-label-short" style={{ display: 'none' }}>{item.shortLabel}</span>
                {item.badge && (
                  <span
                    style={{
                      fontSize: '10px',
                      fontWeight: 700,
                      padding: '1px 5px',
                      borderRadius: '6px',
                      backgroundColor: isActive ? 'var(--color-accent-100)' : 'rgba(79, 95, 138, 0.12)',
                      color: isActive ? 'var(--color-accent-700)' : 'var(--color-ai-500)',
                      letterSpacing: '0.03em'
                    }}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Right Utility Navigation */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {/* Dark Mode 3-state toggle */}
          <button
            onClick={cycleTheme}
            title={`Theme: ${themeMode} (Click to switch)`}
            aria-label="Toggle theme"
            className="header-icon-btn"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              width: '34px',
              height: '34px',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-text-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'background-color 0.15s ease, color 0.15s ease'
            }}
          >
            {themeMode === 'light' ? (
              <Sun size={17} />
            ) : themeMode === 'dark' ? (
              <Moon size={17} />
            ) : (
              <Laptop size={17} />
            )}
          </button>

          {/* Notifications */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setNotifOpen(!notifOpen)}
              aria-label="Notifications"
              className="header-icon-btn"
              style={{
                background: notifOpen ? 'var(--color-bg-surface-sunken)' : 'none',
                border: 'none',
                cursor: 'pointer',
                width: '34px',
                height: '34px',
                borderRadius: 'var(--radius-md)',
                color: 'var(--color-text-secondary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                transition: 'background-color 0.15s ease, color 0.15s ease'
              }}
            >
              <Bell size={17} />
              <span
                style={{
                  position: 'absolute',
                  top: '7px',
                  right: '7px',
                  width: '7px',
                  height: '7px',
                  backgroundColor: 'var(--color-error-text)',
                  borderRadius: '50%',
                  border: '1.5px solid var(--color-bg-surface)'
                }}
              />
            </button>

            {notifOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  right: 0,
                  width: '320px',
                  backgroundColor: 'var(--color-bg-surface)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-lg)',
                  boxShadow: 'var(--elevation-2)',
                  zIndex: 'var(--z-dropdown)',
                  padding: 'var(--space-md)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-sm)' }}>
                  <span style={{ fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                    Notifications
                  </span>
                  <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)' }}>
                    1 unread
                  </span>
                </div>
                <div style={{ borderTop: '1px solid var(--color-border-subtle)', paddingTop: 'var(--space-sm)' }}>
                  <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-primary)', marginBottom: '4px' }}>
                    <strong>Hearing in 4 days:</strong> Martinez v. Coastal Holdings
                  </div>
                  <div style={{ fontSize: 'var(--text-label)', color: 'var(--color-text-muted)' }}>
                    Sep 17, 10:30 AM — Bench IV
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Settings Shortcut */}
          <button
            onClick={() => onNavigate('settings')}
            aria-label="Settings"
            className="header-icon-btn"
            style={{
              background: activeView === 'settings' ? 'var(--color-bg-surface-sunken)' : 'none',
              border: 'none',
              cursor: 'pointer',
              width: '34px',
              height: '34px',
              borderRadius: 'var(--radius-md)',
              color: activeView === 'settings' ? 'var(--color-ink-900)' : 'var(--color-text-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'background-color 0.15s ease, color 0.15s ease'
            }}
          >
            <SettingsIcon size={17} />
          </button>

          {/* Divider */}
          <div style={{ width: '1px', height: '22px', backgroundColor: 'var(--color-border-subtle)', margin: '0 4px' }} />

          {/* Profile Popover Anchor */}
          <div ref={profileRef} style={{ position: 'relative' }}>
            <button
              onClick={() => setProfileOpen(!profileOpen)}
              aria-label="User profile menu"
              style={{
                background: 'var(--color-bg-surface-sunken)',
                border: '1px solid var(--color-border-default)',
                borderRadius: '50%',
                width: '34px',
                height: '34px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: 600,
                fontFamily: 'var(--font-sans)',
                color: 'var(--color-ink-700)',
                transition: 'transform 0.15s ease, border-color 0.15s ease'
              }}
            >
              {currentUser?.avatarInitials || "EV"}
            </button>

            {profileOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  right: 0,
                  width: '260px',
                  backgroundColor: 'var(--color-bg-surface)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-lg)',
                  boxShadow: 'var(--elevation-2)',
                  zIndex: 'var(--z-dropdown)',
                  padding: 'var(--space-sm)'
                }}
              >
                <div style={{ padding: 'var(--space-xs) var(--space-sm)', borderBottom: '1px solid var(--color-border-subtle)', marginBottom: 'var(--space-xs)' }}>
                  <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                    {currentUser?.name || "Adv. Elena Vance"}
                  </div>
                  <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
                    {currentUser?.barNumber?.split(' ')[0] || "NY-BAR-481920"}
                  </div>
                </div>

                <button
                  onClick={() => {
                    setProfileOpen(false);
                    onNavigate('settings');
                  }}
                  className="profile-menu-item"
                  style={{
                    width: '100%',
                    background: 'none',
                    border: 'none',
                    padding: '8px var(--space-sm)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-xs)',
                    fontSize: 'var(--text-caption)',
                    color: 'var(--color-text-primary)',
                    cursor: 'pointer',
                    borderRadius: 'var(--radius-md)',
                    textAlign: 'left'
                  }}
                >
                  <User size={15} color="var(--color-text-secondary)" />
                  <span>Account Profile</span>
                </button>

                <button
                  onClick={() => {
                    setProfileOpen(false);
                    onNavigate('settings');
                  }}
                  className="profile-menu-item"
                  style={{
                    width: '100%',
                    background: 'none',
                    border: 'none',
                    padding: '8px var(--space-sm)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-xs)',
                    fontSize: 'var(--text-caption)',
                    color: 'var(--color-text-primary)',
                    cursor: 'pointer',
                    borderRadius: 'var(--radius-md)',
                    textAlign: 'left'
                  }}
                >
                  <Shield size={15} color="var(--color-text-secondary)" />
                  <span>Security & 2FA</span>
                </button>

                <div style={{ borderTop: '1px solid var(--color-border-subtle)', margin: 'var(--space-xs) 0' }} />

                <button
                  onClick={() => {
                    setProfileOpen(false);
                    onLogout();
                  }}
                  className="profile-menu-item"
                  style={{
                    width: '100%',
                    background: 'none',
                    border: 'none',
                    padding: '8px var(--space-sm)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-xs)',
                    fontSize: 'var(--text-caption)',
                    color: 'var(--color-error-text)',
                    cursor: 'pointer',
                    borderRadius: 'var(--radius-md)',
                    textAlign: 'left'
                  }}
                >
                  <LogOut size={15} />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>

          {/* Mobile Hamburger Menu Toggle */}
          <button
            className="mobile-hamburger"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            style={{
              display: 'none',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '6px',
              color: 'var(--color-text-primary)'
            }}
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile Nav Drawer */}
      {mobileMenuOpen && (
        <div
          style={{
            position: 'fixed',
            top: 'var(--header-height, 64px)',
            left: 0,
            bottom: 0,
            width: '280px',
            backgroundColor: 'var(--color-bg-surface)',
            borderRight: '1px solid var(--color-border-subtle)',
            boxShadow: 'var(--elevation-3)',
            zIndex: 'var(--z-slide-over)',
            padding: 'var(--space-lg) var(--space-md)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-xs)'
          }}
        >
          {navItems.map((item) => {
            const isActive = activeView === item.id || 
              (item.id === 'cases' && activeView === 'case-detail') ||
              (item.id === 'drafting' && (activeView === 'drafting' || activeView === 'editor'));
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onNavigate(item.id);
                  setMobileMenuOpen(false);
                }}
                style={{
                  width: '100%',
                  background: isActive ? 'var(--color-bg-surface-sunken)' : 'transparent',
                  border: 'none',
                  textAlign: 'left',
                  padding: '10px 14px',
                  fontSize: '14px',
                  color: isActive ? 'var(--color-ink-900)' : 'var(--color-text-secondary)',
                  fontWeight: isActive ? 600 : 500,
                  borderRadius: 'var(--radius-md)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  transition: 'background-color 0.15s ease'
                }}
              >
                <Icon size={16} color={isActive ? 'var(--color-accent-700)' : 'var(--color-ink-300)'} />
                <span>{item.label}</span>
                {item.badge && (
                  <span
                    style={{
                      marginLeft: 'auto',
                      fontSize: '10px',
                      fontWeight: 700,
                      padding: '1px 6px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--color-ai-100)',
                      color: 'var(--color-ai-500)'
                    }}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}

      <style>{`
        @media (max-width: 1200px) {
          .nav-label-full { display: none !important; }
          .nav-label-short { display: inline !important; }
        }
        @media (max-width: 900px) {
          .desktop-nav { display: none !important; }
          .desktop-chamber-tag { display: none !important; }
          .mobile-hamburger { display: flex !important; }
        }
        .nav-pill-btn:not(.is-active):hover {
          background-color: rgba(15, 23, 32, 0.05) !important;
          color: var(--color-ink-900) !important;
        }
        [data-theme="dark"] .nav-pill-btn:not(.is-active):hover {
          background-color: rgba(255, 255, 255, 0.08) !important;
          color: var(--color-ink-900) !important;
        }
        .header-icon-btn:hover {
          background-color: var(--color-bg-surface-sunken) !important;
          color: var(--color-ink-900) !important;
        }
        .profile-menu-item:hover {
          background-color: var(--color-bg-surface-sunken) !important;
        }
      `}</style>
    </header>
  );
};
