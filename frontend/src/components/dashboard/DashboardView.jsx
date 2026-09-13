import React, { useState } from 'react';
import { 
  Briefcase, 
  Calendar as CalendarIcon, 
  FileText, 
  Sparkles, 
  ArrowUpRight, 
  Clock, 
  AlertTriangle,
  Plus,
  Send,
  Eye,
  Layers
} from 'lucide-react';
import { Button } from '../common/Button';
import { CaseStatusBadge } from '../common/Badge';
import { EmptyState } from '../common/EmptyState';

export const DashboardView = ({ 
  cases, 
  documents, 
  events, 
  onNavigate, 
  onSelectCase, 
  onOpenAddCase,
  onStartAIChat
}) => {
  // Support toggling to empty state for testing and reviewing empty UI per §9.2
  const [showEmptyStateDemo, setShowEmptyStateDemo] = useState(false);
  const [quickAIInput, setQuickAIInput] = useState('');

  const activeCasesCount = cases.filter(c => c.status === 'Active' || c.status === 'Urgent').length;
  const upcomingHearingsCount = events.filter(e => e.eventType === 'hearing').length;
  const pendingDocsCount = documents.filter(d => d.status === 'processing' || d.status === 'uploading').length;

  const handleQuickAISubmit = (e) => {
    e.preventDefault();
    if (quickAIInput.trim()) {
      onStartAIChat(quickAIInput.trim());
    } else {
      onNavigate('ai');
    }
  };

  if (showEmptyStateDemo || cases.length === 0) {
    return (
      <div className="container" style={{ padding: 'var(--space-2xl) var(--space-md)' }}>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 'var(--space-md)' }}>
          <button
            onClick={() => setShowEmptyStateDemo(!showEmptyStateDemo)}
            style={{
              background: 'none',
              border: '1px dashed var(--color-border-default)',
              borderRadius: 'var(--radius-sm)',
              padding: '4px 8px',
              fontSize: '11px',
              color: 'var(--color-text-muted)',
              cursor: 'pointer'
            }}
          >
            {showEmptyStateDemo ? "Switch to Populated State" : "Test Empty State"}
          </button>
        </div>

        {/* Empty State per §9.2: Centered, 48px mark, "No cases yet.", "Add your first case" CTA */}
        <EmptyState
          icon={Briefcase}
          title="No cases yet."
          description="Add your first case to start organizing documents, hearings, and AI research in one place."
          actionLabel="Add your first case"
          onAction={onOpenAddCase}
        />
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: 'var(--space-xl) var(--space-md)' }}>
      {/* Dev preview toggle for evaluating both states */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 'var(--space-xs)' }}>
        <button
          onClick={() => setShowEmptyStateDemo(true)}
          style={{
            background: 'none',
            border: '1px dashed var(--color-border-default)',
            borderRadius: 'var(--radius-sm)',
            padding: '2px 8px',
            fontSize: '11px',
            color: 'var(--color-text-muted)',
            cursor: 'pointer'
          }}
          title="Click to view the pure empty state per §9.2"
        >
          View Empty State View
        </button>
      </div>

      {/* 1. Welcome Area (§9.1) */}
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <h1
          style={{
            fontFamily: 'var(--font-serif)',
            fontSize: 'var(--text-display)',
            fontWeight: 600,
            color: 'var(--color-text-primary)',
            marginBottom: 'var(--space-3xs)'
          }}
        >
          Good morning, Adv. Vance
        </h1>
        <p
          style={{
            fontFamily: 'var(--font-sans)',
            fontSize: 'var(--text-body)',
            color: 'var(--color-text-secondary)'
          }}
        >
          Sunday, September 13, 2026 &mdash; <strong>3 hearings</strong> scheduled this month, <strong>1 urgent matter</strong> awaiting notice of motion.
        </p>
      </div>

      {/* 2. Stat Cards Grid (4-up, exactly 1 highlighted with 4px verdigris left border per §9.1) */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 'var(--space-md)',
          marginBottom: 'var(--space-xl)'
        }}
      >
        {/* Stat 1: Active Cases */}
        <div
          className="card-base"
          style={{
            padding: 'var(--space-md)',
            borderLeft: '4px solid var(--color-accent-500)' // The single attention highlight
          }}
        >
          <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Active Matters
          </div>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--text-display)',
              fontWeight: 600,
              color: 'var(--color-text-primary)',
              lineHeight: 1.1
            }}
          >
            {activeCasesCount}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-case-urgent-text)', marginTop: '4px', fontWeight: 500 }}>
            1 marked urgent priority
          </div>
        </div>

        {/* Stat 2: Upcoming Hearings */}
        <div className="card-base" style={{ padding: 'var(--space-md)' }}>
          <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Upcoming Hearings
          </div>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--text-display)',
              fontWeight: 600,
              color: 'var(--color-text-primary)',
              lineHeight: 1.1
            }}
          >
            {upcomingHearingsCount}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Next: Sep 17 (Commercial Bench IV)
          </div>
        </div>

        {/* Stat 3: Pending Documents */}
        <div className="card-base" style={{ padding: 'var(--space-md)' }}>
          <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Documents Ingesting
          </div>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--text-display)',
              fontWeight: 600,
              color: 'var(--color-text-primary)',
              lineHeight: 1.1
            }}
          >
            {pendingDocsCount}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-information-text)', marginTop: '4px' }}>
            Port authority strike note indexing
          </div>
        </div>

        {/* Stat 4: AI Citations */}
        <div className="card-base" style={{ padding: 'var(--space-md)' }}>
          <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Citations Verified
          </div>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--text-display)',
              fontWeight: 600,
              color: 'var(--color-text-primary)',
              lineHeight: 1.1
            }}
          >
            14
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-success-text)', marginTop: '4px' }}>
            100% statutory concordance
          </div>
        </div>
      </div>

      {/* 3. Two-Column Area (§9.1): 65% Left (Hearings & Schedule), 35% Right (AI Shortcut & Activity) */}
      <div className="dashboard-grid" style={{ display: 'grid', gridTemplateColumns: '65% 35%', gap: 'var(--space-lg)' }}>
        
        {/* Left Column: Upcoming Hearings & Priority Matters */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          
          {/* Hearings Section */}
          <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
              <div>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)' }}>
                  Upcoming Hearings & Deadlines
                </h2>
                <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                  Chronological schedule across benches and arbitral tribunals
                </p>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => onNavigate('calendar')}
                icon={ArrowUpRight}
                iconPosition="right"
              >
                Full Calendar
              </Button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
              {events.slice(0, 4).map((evt) => {
                const isUrgent = evt.priority === 'urgent';
                return (
                  <div
                    key={evt.id}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      padding: 'var(--space-sm)',
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      borderRadius: 'var(--radius-md)',
                      borderLeft: isUrgent ? '3px solid var(--color-case-urgent-text)' : '1px solid var(--color-border-subtle)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-sm)' }}>
                      {/* Marker shape per §13.1 */}
                      <span
                        style={{
                          width: '10px',
                          height: '10px',
                          backgroundColor: evt.eventType === 'hearing' ? 'var(--color-ink-700)' : 'var(--color-ai-500)',
                          borderRadius: evt.eventType === 'hearing' ? '0px' : '50%',
                          marginTop: '5px',
                          flexShrink: 0
                        }}
                        title={evt.eventType}
                      />
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                          {evt.title}
                        </div>
                        <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                          {evt.court || evt.location}
                        </div>
                        {evt.caseNumber && (
                          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                            Matter #{evt.caseNumber}
                          </div>
                        )}
                      </div>
                    </div>

                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-caption)', fontWeight: 500, color: 'var(--color-ink-700)' }}>
                        {evt.date}
                      </div>
                      <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)' }}>
                        {evt.time}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Active Matters Section */}
          <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
              <div>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)' }}>
                  Active Matters
                </h2>
                <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                  Current matters being handled in chambers
                </p>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => onNavigate('cases')}
                icon={ArrowUpRight}
                iconPosition="right"
              >
                All Matters
              </Button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
              {cases.slice(0, 3).map((c) => (
                <div
                  key={c.id}
                  onClick={() => onSelectCase(c)}
                  className="card-interactive"
                  style={{
                    padding: 'var(--space-sm) var(--space-md)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', marginBottom: '3px' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--color-text-muted)' }}>
                        {c.caseNumber}
                      </span>
                      <CaseStatusBadge status={c.status} />
                    </div>
                    <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                      {c.title}
                    </div>
                    <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                      {c.court}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-link)' }}>
                      Open matter &rarr;
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: AI Assistant Shortcut Card (§9.1) & Activity Feed */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          
          {/* AI Assistant Shortcut Card (§9.1) — Tinted in AI Slate-Indigo Wash */}
          <div
            style={{
              backgroundColor: 'var(--color-ai-100)',
              border: '1px solid var(--color-ai-border)',
              borderRadius: 'var(--radius-lg)',
              padding: 'var(--space-lg)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-sm)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
              {/* Minimal 3-stroke AI Badge per §3.5 */}
              <div
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-ai-500)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF'
                }}
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M3 5H13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M3 8H10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M3 11H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              <span style={{ fontWeight: 600, fontSize: 'var(--text-h3)', color: 'var(--color-ink-700)' }}>
                Legal AI Assistant
              </span>
            </div>

            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
              Ask about any case, statutory interpretation (BNS/BNSS/BSA), or contract dispute.
            </p>

            <form onSubmit={handleQuickAISubmit} style={{ marginTop: 'var(--space-xs)' }}>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  value={quickAIInput}
                  onChange={(e) => setQuickAIInput(e.target.value)}
                  placeholder="Ask a legal or case query…"
                  className="input-base"
                  style={{
                    paddingRight: '36px',
                    backgroundColor: 'var(--color-bg-surface)',
                    fontSize: 'var(--text-caption)'
                  }}
                />
                <button
                  type="submit"
                  aria-label="Submit query to AI Assistant"
                  style={{
                    position: 'absolute',
                    right: '6px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'var(--color-ink-700)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '26px',
                    height: '26px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--color-text-on-ink)',
                    cursor: 'pointer'
                  }}
                >
                  <Send size={13} />
                </button>
              </div>
            </form>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: 'var(--space-2xs)' }}>
              <button
                onClick={() => onStartAIChat("Summarize the injunction grounds for Martinez v. Coastal Holdings")}
                style={{
                  background: 'none',
                  border: '1px solid var(--color-ai-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '2px 6px',
                  fontSize: '11px',
                  color: 'var(--color-text-secondary)',
                  cursor: 'pointer'
                }}
              >
                Injunction grounds?
              </button>
              <button
                onClick={() => onStartAIChat("What is the difference between BSA Section 63 and old 65B?")}
                style={{
                  background: 'none',
                  border: '1px solid var(--color-ai-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '2px 6px',
                  fontSize: '11px',
                  color: 'var(--color-text-secondary)',
                  cursor: 'pointer'
                }}
              >
                BSA s.63 electronic proof?
              </button>
            </div>
          </div>

          {/* Recent Chambers Activity Feed */}
          <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
            <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', color: 'var(--color-text-primary)', marginBottom: 'var(--space-md)' }}>
              Recent Chambers Activity
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              <div style={{ fontSize: 'var(--text-caption)', borderBottom: '1px solid var(--color-border-subtle)', paddingBottom: 'var(--space-xs)' }}>
                <div style={{ fontWeight: 500, color: 'var(--color-text-primary)' }}>
                  Interim Order filed for #2024-CV-1187
                </div>
                <div style={{ color: 'var(--color-text-muted)', fontSize: '11px', marginTop: '2px' }}>
                  2 hours ago &bull; Injunction granted by Commercial Bench
                </div>
              </div>

              <div style={{ fontSize: 'var(--text-caption)', borderBottom: '1px solid var(--color-border-subtle)', paddingBottom: 'var(--space-xs)' }}>
                <div style={{ fontWeight: 500, color: 'var(--color-text-primary)' }}>
                  CFSL Hash Certificate verified
                </div>
                <div style={{ color: 'var(--color-text-muted)', fontSize: '11px', marginTop: '2px' }}>
                  Yesterday &bull; State v. Whitfield electronic drive
                </div>
              </div>

              <div style={{ fontSize: 'var(--text-caption)' }}>
                <div style={{ fontWeight: 500, color: 'var(--color-text-primary)' }}>
                  Testamentary Caveat rejoinder draft
                </div>
                <div style={{ color: 'var(--color-text-muted)', fontSize: '11px', marginTop: '2px' }}>
                  3 days ago &bull; Nguyen Estate Probate
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

      <style>{`
        @media (max-width: 900px) {
          .dashboard-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};
