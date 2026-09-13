import React, { useState } from 'react';
import { 
  ArrowLeft, 
  Clock, 
  FileText, 
  Calendar as CalendarIcon, 
  User, 
  Building2, 
  Upload, 
  Plus, 
  Sparkles,
  ExternalLink,
  MessageSquare
} from 'lucide-react';
import { Button } from '../common/Button';
import { CaseStatusBadge } from '../common/Badge';
import { DocumentManagerView } from '../documents/DocumentManagerView';
import { TimelineView } from '../timeline/TimelineView';
import { AIAssistantView } from '../ai/AIAssistantView';
import { CaseDraftsTab } from '../drafting/CaseDraftsTab';
import { CaseBillingTab } from '../billing/CaseBillingTab';

export const CaseDetailView = ({ 
  currentCase, 
  documents, 
  timelineEvents, 
  drafts = [],
  caseFinances,
  onBack, 
  onUploadDocument,
  onAddTimelineEvent,
  onLaunchCaseAI,
  onOpenNewDraft,
  onSelectDraft,
  onOpenCreateInvoice,
  onOpenRecordPayment,
  onOpenAddExpense
}) => {
  const [activeTab, setActiveTab] = useState('overview'); // overview, documents, timeline, drafts, billing, notes, ai
  const [caseNotes, setCaseNotes] = useState(
    `Notes for ${currentCase.title}:\n\n` +
    `1. 2026-09-08: Reviewed preliminary injunction order. Bench IV requires submission of verified port authority notification before next listing.\n` +
    `2. Key legal vulnerability: Ensure cargo inspection report does not predate the strike declaration.\n` +
    `3. Senior Counsel advised preparing alternate draft seeking Court Receiver appointment if terminal blocks gate access.`
  );

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'documents', label: `Documents (${documents.filter(d => d.caseId === currentCase.id).length})` },
    { id: 'timeline', label: 'Timeline' },
    { id: 'drafts', label: `Drafts (${drafts.filter(d => d.caseId === currentCase.id).length})` },
    { id: 'billing', label: 'Billing' },
    { id: 'notes', label: 'Notes' },
    { id: 'ai', label: 'AI Assistant' }
  ];

  const caseDocs = documents.filter(d => d.caseId === currentCase.id);
  const caseTimeline = timelineEvents.filter(t => t.caseId === currentCase.id);
  const isHearingSoon = currentCase.hearingCountdownDays && currentCase.hearingCountdownDays <= 7;

  return (
    <div className="container" style={{ padding: 'var(--space-xl) var(--space-md)' }}>
      {/* Top Back Nav & Breadcrumb (§11.1) */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', marginBottom: 'var(--space-md)' }}>
        <button
          onClick={onBack}
          aria-label="Back to Cases"
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '4px',
            color: 'var(--color-text-secondary)',
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <ArrowLeft size={18} />
        </button>
        <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)' }}>
          Matters & Cases / <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-text-secondary)' }}>{currentCase.caseNumber}</strong>
        </span>
      </div>

      {/* Case Header Block (§11.1) */}
      <div style={{ marginBottom: 'var(--space-lg)' }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-h3)', color: 'var(--color-ink-500)', fontWeight: 500, marginBottom: '2px' }}>
          {currentCase.caseNumber}
        </div>
        
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 'var(--space-md)', marginBottom: 'var(--space-sm)' }}>
          <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-display)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
            {currentCase.title}
          </h1>
          <CaseStatusBadge status={currentCase.status} />
        </div>

        {/* Metadata Row: Court · Filed date · Case type · Assigned lawyer (Separated by whitespace gaps per §11.1) */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 'var(--space-lg)',
            fontSize: 'var(--text-caption)',
            color: 'var(--color-text-secondary)',
            marginBottom: 'var(--space-md)'
          }}
        >
          <div>
            <span style={{ color: 'var(--color-text-muted)' }}>Court: </span>
            <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.court}</strong>
          </div>
          <div>
            <span style={{ color: 'var(--color-text-muted)' }}>Client: </span>
            <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.client}</strong>
          </div>
          <div>
            <span style={{ color: 'var(--color-text-muted)' }}>Type: </span>
            <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.caseType}</strong>
          </div>
          <div>
            <span style={{ color: 'var(--color-text-muted)' }}>Counsel: </span>
            <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.assignedLawyer}</strong>
          </div>
        </div>

        {/* Highlighted Hearing Strip (§11.1) */}
        {currentCase.nextHearing && (
          <div
            style={{
              padding: 'var(--space-xs) var(--space-md)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: isHearingSoon ? 'var(--color-warning-wash)' : 'var(--color-bg-surface-sunken)',
              border: isHearingSoon ? '1px solid var(--color-warning-border)' : '1px solid var(--color-border-subtle)',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-xs)',
              fontSize: 'var(--text-caption)',
              color: isHearingSoon ? 'var(--color-warning-text)' : 'var(--color-text-secondary)',
              fontWeight: 500
            }}
          >
            <Clock size={15} />
            <span>
              {isHearingSoon ? `Hearing approaching in ${currentCase.hearingCountdownDays} days` : "Next scheduled hearing"}:
              {' '}
              <strong style={{ fontFamily: 'var(--font-mono)' }}>{currentCase.nextHearing}</strong>
            </span>
          </div>
        )}
      </div>

      {/* Underline Tabs Navigation (§11.2) */}
      <div
        style={{
          display: 'flex',
          gap: 'var(--space-lg)',
          borderBottom: '1px solid var(--color-border-subtle)',
          marginBottom: 'var(--space-lg)',
          overflowX: 'auto'
        }}
      >
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: 'none',
                border: 'none',
                padding: 'var(--space-sm) 0',
                cursor: 'pointer',
                fontFamily: 'var(--font-sans)',
                fontSize: 'var(--text-h3)',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? 'var(--color-ink-700)' : 'var(--color-text-secondary)',
                position: 'relative',
                whiteSpace: 'nowrap'
              }}
            >
              {tab.label}
              {isActive && (
                <span
                  style={{
                    position: 'absolute',
                    bottom: '-1px',
                    left: 0,
                    right: 0,
                    height: '2px',
                    backgroundColor: 'var(--color-ink-700)'
                  }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content Areas */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: '65% 35%', gap: 'var(--space-lg)' }} className="case-overview-grid">
          
          {/* Left Column: Synopsis & Recent Matter Documents */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            
            {/* Matter Summary Card */}
            <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
              <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)', marginBottom: 'var(--space-xs)' }}>
                Matter Summary & Procedural Posture
              </h3>
              <p style={{ fontSize: 'var(--text-body)', color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: 'var(--space-md)' }}>
                {currentCase.matterSummary}
              </p>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {currentCase.tags?.map((t, idx) => (
                  <span
                    key={idx}
                    style={{
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      border: '1px solid var(--color-border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '2px 8px',
                      fontSize: 'var(--text-caption)',
                      color: 'var(--color-text-secondary)'
                    }}
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Ingested Documents Preview */}
            <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
                <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', color: 'var(--color-text-primary)' }}>
                  Matter Record Documents ({caseDocs.length})
                </h3>
                <button
                  onClick={() => setActiveTab('documents')}
                  style={{ background: 'none', border: 'none', color: 'var(--color-text-link)', fontSize: 'var(--text-caption)', cursor: 'pointer' }}
                >
                  View all in Document Manager &rarr;
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
                {caseDocs.map((doc) => (
                  <div
                    key={doc.id}
                    style={{
                      padding: 'var(--space-sm)',
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      borderRadius: 'var(--radius-md)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                      <FileText size={16} color="var(--color-ink-500)" />
                      <div>
                        <div style={{ fontWeight: 500, fontSize: 'var(--text-caption)', color: 'var(--color-text-primary)' }}>
                          {doc.filename}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                          {doc.category} &bull; {doc.fileSize} &bull; {doc.statusLabel}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Right Column: AI Assistant Shortcut Card (§11.3) & Actions */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            
            {/* Ask AI about this Case Shortcut */}
            <div
              style={{
                backgroundColor: 'var(--color-ai-100)',
                border: '1px solid var(--color-ai-border)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-lg)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-xs)' }}>
                <div
                  style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--color-ai-500)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#FFFFFF'
                  }}
                >
                  <Sparkles size={13} />
                </div>
                <span style={{ fontWeight: 600, fontSize: 'var(--text-h3)', color: 'var(--color-ink-700)' }}>
                  Ask AI About This Matter
                </span>
              </div>

              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)' }}>
                Directly cross-examine this case file with all documents, timeline entries, and statutory precedents locked in context.
              </p>

              <Button
                variant="primary"
                size="sm"
                fullWidth
                onClick={() => setActiveTab('ai')}
                icon={MessageSquare}
              >
                Launch Single-Case AI
              </Button>
            </div>

            {/* Matter Information Card */}
            <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
              <h4 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', marginBottom: 'var(--space-sm)' }}>
                Chambers File Details
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)', fontSize: 'var(--text-caption)' }}>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Opposing Party: </span>
                  <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.opposingParty}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Date Instituted: </span>
                  <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.filedDate}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Case Priority: </span>
                  <strong style={{ color: currentCase.priority === 'urgent' ? 'var(--color-case-urgent-text)' : 'var(--color-text-primary)' }}>
                    {currentCase.priority.toUpperCase()}
                  </strong>
                </div>
              </div>
            </div>

          </div>

        </div>
      )}

      {/* Tab: Documents */}
      {activeTab === 'documents' && (
        <DocumentManagerView
          caseId={currentCase.id}
          caseNumber={currentCase.caseNumber}
          documents={caseDocs}
          onUploadDocument={onUploadDocument}
        />
      )}

      {/* Tab: Timeline */}
      {activeTab === 'timeline' && (
        <TimelineView
          caseId={currentCase.id}
          timelineEvents={caseTimeline}
          onAddTimelineEvent={onAddTimelineEvent}
        />
      )}

      {/* Tab: Drafts */}
      {activeTab === 'drafts' && (
        <CaseDraftsTab
          currentCase={currentCase}
          drafts={drafts}
          onOpenNewDraft={() => onOpenNewDraft?.(currentCase)}
          onSelectDraft={onSelectDraft}
        />
      )}

      {/* Tab: Billing */}
      {activeTab === 'billing' && (
        <CaseBillingTab
          currentCase={currentCase}
          caseFinances={caseFinances}
          onOpenCreateInvoice={() => onOpenCreateInvoice?.(currentCase)}
          onOpenRecordPayment={() => onOpenRecordPayment?.(currentCase)}
          onOpenAddExpense={() => onOpenAddExpense?.(currentCase)}
        />
      )}

      {/* Tab: Notes */}
      {activeTab === 'notes' && (
        <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
            <div>
              <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)' }}>
                Internal Advocate Work Notes
              </h3>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                Confidential impressions, hearing transcripts, and strategy memos.
              </p>
            </div>
            <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)' }}>
              Auto-saved
            </span>
          </div>

          <textarea
            rows={12}
            value={caseNotes}
            onChange={(e) => setCaseNotes(e.target.value)}
            className="input-base"
            style={{
              fontFamily: 'var(--font-sans)',
              fontSize: 'var(--text-body)',
              lineHeight: 1.6,
              resize: 'vertical'
            }}
          />
        </div>
      )}

      {/* Tab: AI Assistant Embedded in Case Context */}
      {activeTab === 'ai' && (
        <AIAssistantView
          initialMode="SINGLE_CASE"
          lockedCase={currentCase}
          allCases={[currentCase]}
        />
      )}

      <style>{`
        @media (max-width: 900px) {
          .case-overview-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};
