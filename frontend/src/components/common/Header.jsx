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
  FolderLock
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
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'cases', label: 'Cases' },
    { id: 'calendar', label: 'Calendar' },
    { id: 'ai', label: 'AI Assistant' },
    { id: 'drafting', label: 'Drafting' },
    { id: 'billing', label: 'Billing' }
  ];

  const cycleTheme = () => {
    if (themeMode === 'light') onThemeChange('dark');
    else if (themeMode === 'dark') onThemeChange('system');
    else onThemeChange('light');
  };

  return (
    <header
      style={{
        height: 'var(--header-height)',
        backgroundColor: 'var(--color-bg-surface)',
        borderBottom: '1px solid var(--color-border-subtle)',
        position: 'sticky',
        top: 0,
        zIndex: 'var(--z-sticky-header)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 var(--space-lg)'
      }}
    >
      {/* Brand & Wordmark */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2xl)' }}>
        <button
          onClick={() => onNavigate('dashboard')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-xs)',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: 0
          }}
          aria-label="Legal AI Home"
        >
          {/* Concept: "The Marked Page" per §3.1 */}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
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
          <span
            style={{
              fontFamily: 'var(--font-serif)',
              fontSize: '18px',
              fontWeight: 600,
              color: 'var(--color-ink-700)',
              letterSpacing: '0'
            }}
          >
            Legal AI
          </span>
        </button>

        {/* Desktop Primary Navigation */}
        <nav className="desktop-nav" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
          {navItems.map((item) => {
            const isActive = activeView === item.id || 
              (item.id === 'cases' && activeView === 'case-detail') ||
              (item.id === 'drafting' && (activeView === 'drafting' || activeView === 'editor'));
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: 'var(--space-sm) var(--space-md)',
                  fontFamily: 'var(--font-sans)',
                  fontSize: 'var(--text-h3)',
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? 'var(--color-ink-700)' : 'var(--color-text-secondary)',
                  position: 'relative',
                  borderRadius: 'var(--radius-md)',
                  transition: 'color var(--duration-fast) var(--easing-standard)'
                }}
              >
                {item.label}
                {isActive && (
                  <span
                    style={{
                      position: 'absolute',
                      bottom: '2px',
                      left: 'var(--space-md)',
                      right: 'var(--space-md)',
                      height: '2px',
                      backgroundColor: 'var(--color-accent-500)',
                      borderRadius: '1px'
                    }}
                  />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Right Utility Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
        {/* Dark Mode 3-state toggle right in header (§8.1) */}
        <button
          onClick={cycleTheme}
          title={`Theme: ${themeMode} (Click to switch)`}
          aria-label="Toggle theme"
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '8px',
            borderRadius: 'var(--radius-md)',
            color: 'var(--color-text-secondary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          {themeMode === 'light' ? (
            <Sun size={18} />
          ) : themeMode === 'dark' ? (
            <Moon size={18} />
          ) : (
            <Laptop size={18} />
          )}
        </button>

        {/* Notifications */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setNotifOpen(!notifOpen)}
            aria-label="Notifications"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-text-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative'
            }}
          >
            <Bell size={18} />
            <span
              style={{
                position: 'absolute',
                top: '6px',
                right: '6px',
                width: '7px',
                height: '7px',
                backgroundColor: 'var(--color-error-text)',
                borderRadius: '50%'
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
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '8px',
            borderRadius: 'var(--radius-md)',
            color: activeView === 'settings' ? 'var(--color-ink-700)' : 'var(--color-text-secondary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <SettingsIcon size={18} />
        </button>

        {/* Profile Popover Anchor */}
        <div ref={profileRef} style={{ position: 'relative', marginLeft: 'var(--space-2xs)' }}>
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            aria-label="User profile menu"
            style={{
              background: 'var(--color-bg-surface-sunken)',
              border: '1px solid var(--color-border-default)',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 600,
              fontFamily: 'var(--font-sans)',
              color: 'var(--color-ink-700)'
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
            padding: '8px',
            color: 'var(--color-text-primary)'
          }}
        >
          {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Nav Drawer */}
      {mobileMenuOpen && (
        <div
          style={{
            position: 'fixed',
            top: 'var(--header-height)',
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
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                onNavigate(item.id);
                setMobileMenuOpen(false);
              }}
              style={{
                width: '100%',
                background: activeView === item.id ? 'var(--color-bg-surface-sunken)' : 'none',
                border: 'none',
                textAlign: 'left',
                padding: 'var(--space-sm) var(--space-md)',
                fontSize: 'var(--text-h3)',
                color: activeView === item.id ? 'var(--color-ink-700)' : 'var(--color-text-secondary)',
                fontWeight: activeView === item.id ? 600 : 500,
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer'
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      )}

      <style>{`
        @media (max-width: 768px) {
          .desktop-nav { display: none !important; }
          .mobile-hamburger { display: flex !important; }
        }
        .profile-menu-item:hover {
          background-color: var(--color-bg-surface-sunken) !important;
        }
      `}</style>
    </header>
  );
};
