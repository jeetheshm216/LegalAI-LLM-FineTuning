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
  MessageSquare,
  Shield,
  Briefcase,
  Gavel,
  Tag,
  DollarSign,
  CheckCircle2,
  AlertCircle,
  Receipt,
  CreditCard,
  Layers,
  HelpCircle,
  FileCheck,
  ChevronRight
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
  allCases = [],
  documents = [], 
  timelineEvents = [], 
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
    `Notes for ${currentCase?.title || 'Matter'}:\n\n` +
    `1. 2026-09-08: Reviewed preliminary filings. Procedural compliance verified before next listing.\n` +
    `2. Key legal vulnerability: Ensure evidentiary chain-of-custody and certificate requirements are met.\n` +
    `3. Senior Counsel advised preparing alternate draft seeking interim relief or conservatory orders if opposing party fails to produce records.`
  );

  if (!currentCase) {
    return (
      <div className="container" style={{ padding: 'var(--space-xl) var(--space-md)', textAlign: 'center' }}>
        <p style={{ color: 'var(--color-text-secondary)' }}>No case selected.</p>
        <Button variant="secondary" onClick={onBack} icon={ArrowLeft}>
          Back to Cases
        </Button>
      </div>
    );
  }

  const caseDocs = documents.filter(d => d.caseId === currentCase.id || d.caseNumber === currentCase.caseNumber);
  const caseTimeline = timelineEvents.filter(t => t.caseId === currentCase.id || t.caseNumber === currentCase.caseNumber);
  const caseDrafts = drafts.filter(d => d.caseId === currentCase.id || d.caseNumber === currentCase.caseNumber);
  const isHearingSoon = currentCase.hearingCountdownDays && currentCase.hearingCountdownDays <= 7;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Layers, count: null },
    { id: 'documents', label: 'Documents', icon: FileText, count: caseDocs.length },
    { id: 'timeline', label: 'Timeline', icon: CalendarIcon, count: caseTimeline.length },
    { id: 'drafts', label: 'Drafts', icon: FileCheck, count: caseDrafts.length },
    { id: 'billing', label: 'Billing & Ledger', icon: Receipt, count: null },
    { id: 'notes', label: 'Case Notes', icon: Edit3Icon, count: null },
    { id: 'ai', label: 'Case AI Assistant', icon: Sparkles, count: null, highlight: true }
  ];

  function Edit3Icon(props) {
    return <FileText {...props} />;
  }

  return (
    <div className="container" style={{ padding: 'var(--space-lg) var(--space-md)' }}>
      {/* 1. Breadcrumbs Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-md)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
          <button
            onClick={onBack}
            aria-label="Back to Cases"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--color-text-secondary)',
              display: 'flex',
              alignItems: 'center',
              transition: 'background-color 0.15s ease'
            }}
          >
            <ArrowLeft size={16} />
          </button>
          <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)' }}>
            Matters & Cases
          </span>
          <span style={{ color: 'var(--color-text-muted)', fontSize: '12px' }}>/</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-caption)', fontWeight: 600, color: 'var(--color-ink-700)' }}>
            {currentCase.caseNumber}
          </span>
          <span style={{ color: 'var(--color-text-muted)', fontSize: '12px' }}>&bull;</span>
          <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {currentCase.title}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
          <CaseStatusBadge status={currentCase.status} />
          {currentCase.priority === 'urgent' && (
            <span
              style={{
                backgroundColor: 'var(--color-error-wash)',
                color: 'var(--color-error-text)',
                border: '1px solid var(--color-error-border)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                fontSize: '11px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.04em'
              }}
            >
              Urgent Priority
            </span>
          )}
        </div>
      </div>

      {/* 2. Structured Hero Case Card (§11.1) */}
      <div 
        className="card-base"
        style={{
          padding: 'var(--space-lg) var(--space-xl)',
          marginBottom: 'var(--space-lg)',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border-subtle)',
          borderRadius: 'var(--radius-xl)',
          boxShadow: 'var(--elevation-1)'
        }}
      >
        {/* Hero Top Bar: Identifier & Quick Action Buttons */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-sm)', marginBottom: 'var(--space-xs)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '13px',
                fontWeight: 600,
                color: 'var(--color-ink-700)',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                border: '1px solid var(--color-border-subtle)',
                padding: '3px 8px',
                borderRadius: 'var(--radius-sm)'
              }}
            >
              {currentCase.caseNumber}
            </span>
            <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)' }}>
              Instituted {currentCase.filedDate}
            </span>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 'var(--space-xs)' }}>
            <Button
              variant="secondary"
              size="sm"
              icon={Upload}
              onClick={() => setActiveTab('documents')}
            >
              Upload Doc
            </Button>
            <Button
              variant="secondary"
              size="sm"
              icon={Plus}
              onClick={() => onOpenNewDraft?.(currentCase)}
            >
              New Draft
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={Sparkles}
              onClick={() => setActiveTab('ai')}
            >
              Ask Case AI
            </Button>
          </div>
        </div>

        {/* Case Title */}
        <h1 
          style={{ 
            fontFamily: 'var(--font-serif)', 
            fontSize: '24px', 
            fontWeight: 600, 
            color: 'var(--color-text-primary)',
            margin: 'var(--space-3xs) 0 var(--space-xs) 0',
            letterSpacing: '-0.01em'
          }}
        >
          {currentCase.title}
        </h1>

        {/* Matter Summary One-liner */}
        {currentCase.description && (
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', margin: '0 0 var(--space-md) 0', lineHeight: 1.5 }}>
            {currentCase.description}
          </p>
        )}

        {/* Structured 6-Cell Metadata Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 'var(--space-sm)',
            backgroundColor: 'var(--color-bg-surface-sunken)',
            padding: 'var(--space-sm) var(--space-md)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-border-subtle)',
            marginBottom: currentCase.nextHearing ? 'var(--space-sm)' : 0
          }}
        >
          {/* Court & Bench */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <Gavel size={15} color="var(--color-ink-500)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Court & Bench</div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>{currentCase.court || 'Court Unassigned'}</div>
            </div>
          </div>

          {/* Client */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <User size={15} color="var(--color-ink-500)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Client</div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>{currentCase.client || 'Client N/A'}</div>
            </div>
          </div>

          {/* Opposing Party */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <Building2 size={15} color="var(--color-ink-500)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Opposing Party</div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>{currentCase.opposingParty || 'Ex-Parte'}</div>
            </div>
          </div>

          {/* Practice Area / Type */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <Briefcase size={15} color="var(--color-ink-500)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Matter Category</div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>{currentCase.caseType || 'General Civil'}</div>
            </div>
          </div>

          {/* Assigned Counsel */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <Shield size={15} color="var(--color-ink-500)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Lead Counsel</div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>{currentCase.assignedLawyer || 'Chambers Counsel'}</div>
            </div>
          </div>
        </div>

        {/* Integrated Hearing Notice Banner */}
        {currentCase.nextHearing && (
          <div
            style={{
              padding: 'var(--space-xs) var(--space-md)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: isHearingSoon ? 'var(--color-warning-wash)' : 'var(--color-bg-surface-sunken)',
              border: isHearingSoon ? '1px solid var(--color-warning-border)' : '1px solid var(--color-border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 'var(--space-xs)',
              fontSize: 'var(--text-caption)',
              color: isHearingSoon ? 'var(--color-warning-text)' : 'var(--color-text-secondary)',
              fontWeight: 500
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={16} color={isHearingSoon ? 'var(--color-warning-text)' : 'var(--color-accent-500)'} />
              <span>
                {isHearingSoon ? `Notice: Hearing scheduled in ${currentCase.hearingCountdownDays} days` : 'Next scheduled proceeding'}:
                {' '}
                <strong style={{ fontFamily: 'var(--font-mono)' }}>{currentCase.nextHearing}</strong>
              </span>
            </div>
            <button
              onClick={() => setActiveTab('timeline')}
              style={{
                background: 'none',
                border: 'none',
                color: isHearingSoon ? 'var(--color-warning-text)' : 'var(--color-text-link)',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
                textDecoration: 'underline'
              }}
            >
              View Procedural Timeline &rarr;
            </button>
          </div>
        )}
      </div>

      {/* 3. Structured Segmented Tabs Navigation (§11.2) */}
      <div
        style={{
          display: 'flex',
          gap: 'var(--space-2xs)',
          backgroundColor: 'var(--color-bg-surface)',
          padding: '4px',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--color-border-subtle)',
          marginBottom: 'var(--space-lg)',
          overflowX: 'auto',
          boxShadow: 'var(--elevation-1)'
        }}
      >
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          const TabIcon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                borderRadius: 'var(--radius-md)',
                border: 'none',
                background: isActive 
                  ? (tab.highlight ? 'var(--color-ai-500)' : 'var(--color-ink-700)') 
                  : 'transparent',
                color: isActive ? '#FFFFFF' : 'var(--color-text-secondary)',
                fontFamily: 'var(--font-sans)',
                fontSize: '13px',
                fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease'
              }}
            >
              <TabIcon size={15} color={isActive ? '#FFFFFF' : (tab.highlight ? 'var(--color-ai-500)' : 'var(--color-text-secondary)')} />
              <span>{tab.label}</span>
              {tab.count !== null && (
                <span
                  style={{
                    backgroundColor: isActive ? 'rgba(255, 255, 255, 0.25)' : 'var(--color-bg-surface-sunken)',
                    color: isActive ? '#FFFFFF' : 'var(--color-text-muted)',
                    borderRadius: '10px',
                    padding: '1px 6px',
                    fontSize: '11px',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 600
                  }}
                >
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* 4. Tab Content Areas */}

      {/* TAB: OVERVIEW */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: '65% 35%', gap: 'var(--space-lg)' }} className="case-overview-grid">
          {/* Left Column: Synopsis & Recent Matter Documents */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            
            {/* Matter Summary Card */}
            <div className="card-base" style={{ padding: 'var(--space-lg)', borderRadius: 'var(--radius-lg)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-xs)' }}>
                <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)', margin: 0 }}>
                  Matter Summary & Procedural Posture
                </h3>
                <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                  Filed under {currentCase.caseType}
                </span>
              </div>
              <p style={{ fontSize: 'var(--text-body)', color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: 'var(--space-md)' }}>
                {currentCase.matterSummary || currentCase.description}
              </p>

              {currentCase.tags && currentCase.tags.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', alignItems: 'center' }}>
                  <Tag size={13} color="var(--color-text-muted)" />
                  {currentCase.tags.map((t, idx) => (
                    <span
                      key={idx}
                      style={{
                        backgroundColor: 'var(--color-bg-surface-sunken)',
                        border: '1px solid var(--color-border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '2px 8px',
                        fontSize: '11px',
                        color: 'var(--color-text-secondary)',
                        fontWeight: 500
                      }}
                    >
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Ingested Documents Preview Card */}
            <div className="card-base" style={{ padding: 'var(--space-lg)', borderRadius: 'var(--radius-lg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FileText size={18} color="var(--color-ink-500)" />
                  <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', color: 'var(--color-text-primary)', margin: 0 }}>
                    Matter Record Documents ({caseDocs.length})
                  </h3>
                </div>
                <button
                  onClick={() => setActiveTab('documents')}
                  style={{ background: 'none', border: 'none', color: 'var(--color-text-link)', fontSize: 'var(--text-caption)', cursor: 'pointer', fontWeight: 500 }}
                >
                  Open Document Manager &rarr;
                </button>
              </div>

              {caseDocs.length === 0 ? (
                <div style={{ padding: 'var(--space-md)', textAlign: 'center', backgroundColor: 'var(--color-bg-surface-sunken)', borderRadius: 'var(--radius-md)', color: 'var(--color-text-muted)', fontSize: 'var(--text-caption)' }}>
                  No case documents ingested yet. Click 'Upload Doc' to index pleadings and transcripts.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
                  {caseDocs.slice(0, 4).map((doc) => (
                    <div
                      key={doc.id}
                      style={{
                        padding: 'var(--space-xs) var(--space-sm)',
                        backgroundColor: 'var(--color-bg-surface-sunken)',
                        borderRadius: 'var(--radius-md)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        border: '1px solid var(--color-border-subtle)'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                        <FileText size={16} color="var(--color-ink-500)" />
                        <div>
                          <div style={{ fontWeight: 500, fontSize: 'var(--text-caption)', color: 'var(--color-text-primary)' }}>
                            {doc.filename}
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                            {doc.category} &bull; {doc.fileSize} &bull; <span style={{ color: 'var(--color-success-text)' }}>✓ Ready for AI RAG search</span>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => setActiveTab('documents')}
                        style={{
                          padding: '3px 8px',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--color-border-default)',
                          backgroundColor: 'var(--color-bg-surface)',
                          fontSize: '11px',
                          color: 'var(--color-text-secondary)',
                          cursor: 'pointer'
                        }}
                      >
                        Inspect
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Upcoming Procedural Milestones */}
            <div className="card-base" style={{ padding: 'var(--space-lg)', borderRadius: 'var(--radius-lg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CalendarIcon size={18} color="var(--color-ink-500)" />
                  <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', color: 'var(--color-text-primary)', margin: 0 }}>
                    Procedural Milestones & Hearings ({caseTimeline.length})
                  </h3>
                </div>
                <button
                  onClick={() => setActiveTab('timeline')}
                  style={{ background: 'none', border: 'none', color: 'var(--color-text-link)', fontSize: 'var(--text-caption)', cursor: 'pointer', fontWeight: 500 }}
                >
                  View Full Timeline &rarr;
                </button>
              </div>

              {caseTimeline.length === 0 ? (
                <div style={{ padding: 'var(--space-md)', textAlign: 'center', backgroundColor: 'var(--color-bg-surface-sunken)', borderRadius: 'var(--radius-md)', color: 'var(--color-text-muted)', fontSize: 'var(--text-caption)' }}>
                  No timeline milestones scheduled. Click 'Timeline' tab to add court orders or filings.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
                  {caseTimeline.slice(0, 3).map((evt) => (
                    <div
                      key={evt.id}
                      style={{
                        padding: 'var(--space-xs) var(--space-sm)',
                        backgroundColor: 'var(--color-bg-surface-sunken)',
                        borderRadius: 'var(--radius-md)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        border: '1px solid var(--color-border-subtle)'
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 'var(--text-caption)', color: 'var(--color-text-primary)' }}>
                          {evt.title}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                          {evt.description || evt.summary}
                        </div>
                      </div>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-ink-700)', fontWeight: 600 }}>
                        {evt.date}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>

          {/* Right Column: Case Intelligence Shortcut & File Ledger */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            
            {/* Ask AI About This Case Shortcut Card (§11.3) */}
            <div
              style={{
                backgroundColor: 'var(--color-ai-100)',
                border: '1px solid var(--color-ai-border)',
                borderRadius: 'var(--radius-xl)',
                padding: 'var(--space-lg)',
                boxShadow: 'var(--elevation-1)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-xs)' }}>
                <div
                  style={{
                    width: '26px',
                    height: '26px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--color-ai-500)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#FFFFFF'
                  }}
                >
                  <Sparkles size={14} />
                </div>
                <span style={{ fontWeight: 600, fontSize: 'var(--text-h3)', color: 'var(--color-ink-700)' }}>
                  Matter Intelligence AI
                </span>
              </div>

              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)', lineHeight: 1.5 }}>
                Examine this case with all {caseDocs.length} record documents, timeline milestones, and statutory precedents locked in context.
              </p>

              {/* Pre-configured One-Click Prompt Suggestions */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: 'var(--space-md)' }}>
                <button
                  onClick={() => setActiveTab('ai')}
                  style={{
                    textAlign: 'left',
                    padding: '8px 10px',
                    backgroundColor: 'var(--color-bg-surface)',
                    border: '1px solid var(--color-ai-border)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '11px',
                    fontWeight: 500,
                    color: 'var(--color-ink-700)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <span>⚡ Analyze Injunction Merits & Legal Grounds</span>
                  <ChevronRight size={13} color="var(--color-ai-500)" />
                </button>
                <button
                  onClick={() => setActiveTab('ai')}
                  style={{
                    textAlign: 'left',
                    padding: '8px 10px',
                    backgroundColor: 'var(--color-bg-surface)',
                    border: '1px solid var(--color-ai-border)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '11px',
                    fontWeight: 500,
                    color: 'var(--color-ink-700)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <span>📜 Check Electronic Evidence Admissibility (BSA s.63)</span>
                  <ChevronRight size={13} color="var(--color-ai-500)" />
                </button>
                <button
                  onClick={() => setActiveTab('ai')}
                  style={{
                    textAlign: 'left',
                    padding: '8px 10px',
                    backgroundColor: 'var(--color-bg-surface)',
                    border: '1px solid var(--color-ai-border)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '11px',
                    fontWeight: 500,
                    color: 'var(--color-ink-700)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <span>📑 Cross-Examine Cargo Lien vs Notice of Dispute</span>
                  <ChevronRight size={13} color="var(--color-ai-500)" />
                </button>
              </div>

              <Button
                variant="primary"
                size="sm"
                fullWidth
                onClick={() => setActiveTab('ai')}
                icon={MessageSquare}
              >
                Launch Matter AI Workspace
              </Button>
            </div>

            {/* File Particulars & Chamber Details Card */}
            <div className="card-base" style={{ padding: 'var(--space-lg)', borderRadius: 'var(--radius-lg)' }}>
              <h4 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', marginBottom: 'var(--space-sm)', margin: '0 0 var(--space-sm) 0' }}>
                Chambers File Ledger
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)', fontSize: 'var(--text-caption)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>Case Number:</span>
                  <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-ink-700)' }}>{currentCase.caseNumber}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>Opposing Party:</span>
                  <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.opposingParty}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>Date Instituted:</span>
                  <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.filedDate}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>Case Priority:</span>
                  <strong style={{ color: currentCase.priority === 'urgent' ? 'var(--color-error-text)' : 'var(--color-text-primary)', textTransform: 'uppercase' }}>
                    {currentCase.priority || 'Normal'}
                  </strong>
                </div>
              </div>
            </div>

            {/* Quick Financial Snapshot Card */}
            <div className="card-base" style={{ padding: 'var(--space-lg)', borderRadius: 'var(--radius-lg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
                <h4 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', margin: 0 }}>
                  Financial & Retainer Status
                </h4>
                <button
                  onClick={() => setActiveTab('billing')}
                  style={{ background: 'none', border: 'none', color: 'var(--color-text-link)', fontSize: '11px', cursor: 'pointer', fontWeight: 500 }}
                >
                  Ledger &rarr;
                </button>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 'var(--space-xs) 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>Pending Invoices:</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: '12px' }}>
                  {caseFinances?.invoices?.length || 1} Active
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 'var(--space-xs) 0' }}>
                <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>Trust Retainer:</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: '12px', color: 'var(--color-success-text)' }}>
                  Adequate
                </span>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* TAB: DOCUMENTS */}
      {activeTab === 'documents' && (
        <DocumentManagerView
          caseId={currentCase.id}
          caseNumber={currentCase.caseNumber}
          documents={caseDocs}
          onUploadDocument={onUploadDocument}
        />
      )}

      {/* TAB: TIMELINE */}
      {activeTab === 'timeline' && (
        <TimelineView
          caseId={currentCase.id}
          timelineEvents={caseTimeline}
          onAddTimelineEvent={onAddTimelineEvent}
        />
      )}

      {/* TAB: DRAFTS */}
      {activeTab === 'drafts' && (
        <CaseDraftsTab
          currentCase={currentCase}
          drafts={caseDrafts}
          onOpenNewDraft={() => onOpenNewDraft?.(currentCase)}
          onSelectDraft={onSelectDraft}
        />
      )}

      {/* TAB: BILLING */}
      {activeTab === 'billing' && (
        <CaseBillingTab
          currentCase={currentCase}
          caseFinances={caseFinances}
          onOpenCreateInvoice={() => onOpenCreateInvoice?.(currentCase)}
          onOpenRecordPayment={() => onOpenRecordPayment?.(currentCase)}
          onOpenAddExpense={() => onOpenAddExpense?.(currentCase)}
        />
      )}

      {/* TAB: NOTES */}
      {activeTab === 'notes' && (
        <div className="card-base" style={{ padding: 'var(--space-xl)', borderRadius: 'var(--radius-xl)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
            <div>
              <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)', margin: '0 0 4px 0' }}>
                Internal Advocate Work Notes — {currentCase.caseNumber}
              </h3>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', margin: 0 }}>
                Privileged client impressions, hearing transcripts, and strategy memos.
              </p>
            </div>
            <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-success-text)', fontWeight: 500 }}>
              ✓ Auto-saved
            </span>
          </div>

          <textarea
            rows={14}
            value={caseNotes}
            onChange={(e) => setCaseNotes(e.target.value)}
            className="input-base"
            style={{
              fontFamily: 'var(--font-sans)',
              fontSize: 'var(--text-body)',
              lineHeight: 1.6,
              resize: 'vertical',
              width: '100%',
              boxSizing: 'border-box'
            }}
          />
        </div>
      )}

      {/* TAB: AI ASSISTANT EMBEDDED IN CASE CONTEXT */}
      {activeTab === 'ai' && (
        <div
          style={{
            height: '740px',
            minHeight: '620px',
            maxHeight: '85vh',
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: 'var(--color-bg-surface)',
            border: '1px solid var(--color-border-subtle)',
            borderRadius: 'var(--radius-xl)',
            overflow: 'hidden',
            boxShadow: 'var(--elevation-2)'
          }}
        >
          {/* Top Context Breadcrumb inside AI Workspace */}
          <div
            style={{
              backgroundColor: 'var(--color-ai-100)',
              borderBottom: '1px solid var(--color-ai-border)',
              padding: '8px 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '12px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-ai-500)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF'
                }}
              >
                <Sparkles size={11} />
              </div>
              <span style={{ fontWeight: 600, color: 'var(--color-ink-700)' }}>
                Matter AI Intelligence Workspace
              </span>
              <span style={{ color: 'var(--color-text-muted)' }}>&bull;</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{currentCase.caseNumber}</span>
              <span style={{ color: 'var(--color-text-muted)' }}>&bull;</span>
              <span style={{ color: 'var(--color-text-secondary)' }}>{currentCase.title}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.7)',
                  border: '1px solid var(--color-ai-border)',
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '11px',
                  color: 'var(--color-text-secondary)',
                  fontWeight: 500
                }}
              >
                🔒 {caseDocs.length} Case Docs Locked
              </span>
            </div>
          </div>

          {/* Embedded AIAssistantView with bounded height */}
          <div style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
            <AIAssistantView
              initialMode="SINGLE_CASE"
              lockedCase={currentCase}
              allCases={[currentCase, ...(allCases || []).filter(c => c.id !== currentCase.id)]}
            />
          </div>
        </div>
      )}

      <style>{`
        @media (max-width: 960px) {
          .case-overview-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};
