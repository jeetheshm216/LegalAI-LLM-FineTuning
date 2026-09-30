import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  Clock, 
  Calendar as CalendarIcon, 
  Gavel, 
  Tag, 
  Plus, 
  Upload, 
  MessageSquare, 
  Sparkles, 
  FileText, 
  FileCheck, 
  Receipt, 
  LayoutDashboard,
  Trash2,
  Edit2,
  Search,
  StickyNote,
  Check,
  X,
  AlertCircle
} from 'lucide-react';
import { Button } from '../common/Button';
import { CaseStatusBadge } from '../common/Badge';
import { DocumentManagerView } from '../documents/DocumentManagerView';
import { TimelineView } from '../timeline/TimelineView';
import { CaseDraftsTab } from '../drafting/CaseDraftsTab';
import { CaseBillingTab } from '../billing/CaseBillingTab';
import { AIAssistantView } from '../ai/AIAssistantView';

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
  const [activeTab, setActiveTab] = useState('overview');

  // Filter case-specific records
  const caseDocs = documents.filter(d => d.caseId === currentCase?.id || d.caseNumber === currentCase?.caseNumber);
  const caseTimeline = timelineEvents.filter(e => e.caseId === currentCase?.id);
  const caseDrafts = drafts.filter(d => d.caseId === currentCase?.id || d.caseNumber === currentCase?.caseNumber);

  // Multi-Notes State per case with persistence
  const notesStorageKey = `legalai_notes_${currentCase?.id || currentCase?.caseNumber || 'default'}`;
  const [notes, setNotes] = useState(() => {
    try {
      const saved = localStorage.getItem(notesStorageKey);
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.warn('Failed to load notes from storage', e);
    }
    // Default high-quality initial notes based on case
    return [
      {
        id: 'note-1',
        title: 'Initial Case Strategy & Jurisdictional Grounds',
        category: 'Strategy Memo',
        content: `Preliminary review of matter ${currentCase?.caseNumber || ''}. Focus on evidentiary chain of custody and immediate pre-trial motions before ${currentCase?.court || 'the Bench'}. Verify statutory compliance under relevant procedural provisions.`,
        createdAt: '12 Sep 2026, 10:15 AM',
        author: 'Adv. Elena Vance'
      },
      {
        id: 'note-2',
        title: 'Hearing Arguments & Key Contradictions',
        category: 'Hearing Prep',
        content: `Examine opposing party claims regarding timeline notices. Prepare cross-examination pointers on witness deposition and verify digital certificate admissibility under BSA Section 63.`,
        createdAt: '14 Sep 2026, 04:30 PM',
        author: 'Adv. Elena Vance'
      }
    ];
  });

  // Save notes to localStorage on change
  useEffect(() => {
    try {
      localStorage.setItem(notesStorageKey, JSON.stringify(notes));
    } catch (e) {
      console.warn('Failed to save notes to storage', e);
    }
  }, [notes, notesStorageKey]);

  // Note composer modal state
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [newNoteTitle, setNewNoteTitle] = useState('');
  const [newNoteCategory, setNewNoteCategory] = useState('Hearing Prep');
  const [newNoteContent, setNewNoteContent] = useState('');
  const [noteSearchQuery, setNoteSearchQuery] = useState('');
  const [editingNoteId, setEditingNoteId] = useState(null);

  const handleSaveNote = (e) => {
    e.preventDefault();
    if (!newNoteTitle.trim() || !newNoteContent.trim()) return;

    if (editingNoteId) {
      setNotes(prev => prev.map(n => n.id === editingNoteId ? {
        ...n,
        title: newNoteTitle.trim(),
        category: newNoteCategory,
        content: newNoteContent.trim(),
        updatedAt: 'Just now'
      } : n));
      setEditingNoteId(null);
    } else {
      const newNote = {
        id: `note-${Date.now()}`,
        title: newNoteTitle.trim(),
        category: newNoteCategory,
        content: newNoteContent.trim(),
        createdAt: 'Just now',
        author: 'Adv. Elena Vance'
      };
      setNotes(prev => [newNote, ...prev]);
    }

    setNewNoteTitle('');
    setNewNoteContent('');
    setIsAddingNote(false);
  };

  const handleDeleteNote = (noteId) => {
    setNotes(prev => prev.filter(n => n.id !== noteId));
  };

  const handleStartEditNote = (note) => {
    setEditingNoteId(note.id);
    setNewNoteTitle(note.title);
    setNewNoteCategory(note.category || 'General');
    setNewNoteContent(note.content);
    setIsAddingNote(true);
  };

  if (!currentCase) {
    return (
      <div className="container" style={{ paddingTop: 'var(--space-xl)', paddingBottom: 'var(--space-2xl)', textAlign: 'center' }}>
        <p style={{ color: 'var(--color-text-secondary)' }}>No case selected.</p>
        <Button variant="secondary" onClick={onBack} icon={ArrowLeft}>
          Back to Cases
        </Button>
      </div>
    );
  }

  const isHearingSoon = currentCase.hearingCountdownDays !== undefined && currentCase.hearingCountdownDays <= 7;

  // Primary Case Navigation Tabs - PLACED AT THE TOP
  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard, count: null },
    { id: 'documents', label: 'Documents', icon: FileText, count: caseDocs.length },
    { id: 'timeline', label: 'Timeline', icon: CalendarIcon, count: caseTimeline.length },
    { id: 'drafts', label: 'Drafts', icon: FileCheck, count: caseDrafts.length },
    { id: 'billing', label: 'Billing & Ledger', icon: Receipt, count: null },
    { id: 'notes', label: 'Case Notes', icon: StickyNote, count: notes.length },
    { id: 'ai', label: 'Case AI Assistant', icon: Sparkles, count: null, highlight: true }
  ];

  const filteredNotes = notes.filter(n => 
    n.title.toLowerCase().includes(noteSearchQuery.toLowerCase()) ||
    n.content.toLowerCase().includes(noteSearchQuery.toLowerCase()) ||
    (n.category && n.category.toLowerCase().includes(noteSearchQuery.toLowerCase()))
  );

  return (
    <div className="container" style={{ paddingTop: 'var(--space-md)', paddingBottom: 'var(--space-2xl)' }}>
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
          <span style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
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

      {/* 2. TOP PRIMARY CASE NAVIGATION BAR (Moved to top per requirement) */}
      <div
        style={{
          display: 'flex',
          gap: '6px',
          backgroundColor: 'var(--color-bg-surface)',
          padding: '6px',
          borderRadius: 'var(--radius-xl)',
          border: '1px solid var(--color-border-subtle)',
          marginBottom: 'var(--space-md)',
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
                gap: '8px',
                padding: '8px 16px',
                borderRadius: 'var(--radius-lg)',
                backgroundColor: isActive 
                  ? (tab.highlight ? 'var(--color-ai-500)' : 'var(--color-bg-surface-raised)') 
                  : 'transparent',
                color: isActive 
                  ? (tab.highlight ? '#FFFFFF' : 'var(--color-ink-900)') 
                  : 'var(--color-text-secondary)',
                border: isActive ? '1px solid var(--color-border-subtle)' : '1px solid transparent',
                fontFamily: 'var(--font-sans)',
                fontSize: '13.5px',
                fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease',
                boxShadow: isActive ? 'var(--elevation-1)' : 'none'
              }}
            >
              <TabIcon 
                size={16} 
                color={isActive ? (tab.highlight ? '#FFFFFF' : 'var(--color-ink-900)') : (tab.highlight ? 'var(--color-ai-500)' : 'var(--color-ink-300)')} 
              />
              <span>{tab.label}</span>
              {tab.count !== null && (
                <span
                  style={{
                    backgroundColor: isActive ? 'var(--color-accent-100)' : 'var(--color-bg-surface-sunken)',
                    color: isActive ? 'var(--color-accent-700)' : 'var(--color-text-muted)',
                    borderRadius: '10px',
                    padding: '1px 7px',
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

      {/* 3. SIMPLIFIED, NEAT CASE HEADER CARD (Comes UNDER navigation with only essential details) */}
      <div 
        className="card-base"
        style={{
          padding: 'var(--space-md) var(--space-lg)',
          marginBottom: 'var(--space-lg)',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border-subtle)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--elevation-1)',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 'var(--space-md)'
        }}
      >
        {/* Left: Essential Matter Identification */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px' }}>
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '12.5px',
                fontWeight: 700,
                color: 'var(--color-ink-700)',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                border: '1px solid var(--color-border-subtle)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-sm)'
              }}
            >
              {currentCase.caseNumber}
            </span>
            <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
              🏛️ {currentCase.court || 'Court Unassigned'}
            </span>
            {currentCase.nextHearing && (
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '5px',
                  fontSize: '12px',
                  fontWeight: 600,
                  backgroundColor: isHearingSoon ? 'var(--color-warning-wash)' : 'var(--color-bg-surface-sunken)',
                  color: isHearingSoon ? 'var(--color-warning-text)' : 'var(--color-text-secondary)',
                  border: isHearingSoon ? '1px solid var(--color-warning-border)' : '1px solid var(--color-border-subtle)',
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-sm)'
                }}
              >
                <Clock size={13} />
                Hearing: {currentCase.nextHearing}
              </span>
            )}
          </div>

          <h1 
            style={{ 
              fontFamily: 'var(--font-serif)', 
              fontSize: '22px', 
              fontWeight: 700, 
              color: 'var(--color-text-primary)',
              margin: 0,
              letterSpacing: '-0.01em',
              lineHeight: 1.2
            }}
          >
            {currentCase.title}
          </h1>
        </div>

        {/* Right: Quick Action Navigations (Guaranteed Working) */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px' }}>
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
            + New Draft
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

      {/* 4. DEDICATED CASE TAB PAGES (Fitting the webpage size) */}

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
                {currentCase.matterSummary || currentCase.description || "Active legal proceeding with ongoing pleading scrutiny, evidence review, and scheduled chamber appearances."}
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
                        justifyContent: 'space-between'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
                        <FileText size={15} color="var(--color-ink-500)" />
                        <div>
                          <div style={{ fontSize: 'var(--text-caption)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                            {doc.title}
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                            {doc.category} &bull; {doc.size} &bull; <span style={{ color: 'var(--color-success-text)' }}>✓ Ready for AI RAG search</span>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => setActiveTab('documents')}
                        style={{
                          background: 'var(--color-bg-surface)',
                          border: '1px solid var(--color-border-subtle)',
                          borderRadius: 'var(--radius-sm)',
                          padding: '3px 8px',
                          fontSize: '11px',
                          cursor: 'pointer',
                          color: 'var(--color-text-secondary)'
                        }}
                      >
                        Inspect
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Key Procedural Milestones Preview Card */}
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
                  No timeline milestones recorded yet.
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
                        justifyContent: 'space-between'
                      }}
                    >
                      <div>
                        <div style={{ fontSize: 'var(--text-caption)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                          {evt.title}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                          {evt.description}
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
            
            {/* Ask AI About This Case Shortcut Card */}
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
                  <span style={{ color: 'var(--color-ai-500)' }}>&rarr;</span>
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
                  <span style={{ color: 'var(--color-ai-500)' }}>&rarr;</span>
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
                  <span style={{ color: 'var(--color-ai-500)' }}>&rarr;</span>
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
                  <span style={{ color: 'var(--color-text-muted)' }}>Client:</span>
                  <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.client || 'Arthur Whitfield'}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>Opposing Party:</span>
                  <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.opposingParty || 'State Department of Public Prosecutions'}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--color-border-subtle)' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>Lead Counsel:</span>
                  <strong style={{ color: 'var(--color-text-primary)' }}>{currentCase.assignedLawyer || 'Adv. Elena Vance'}</strong>
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

      {/* TAB: DOCUMENTS (Full page experience for this case) */}
      {activeTab === 'documents' && (
        <div style={{ width: '100%' }}>
          <DocumentManagerView
            caseId={currentCase.id}
            caseNumber={currentCase.caseNumber}
            documents={caseDocs}
            onUploadDocument={onUploadDocument}
          />
        </div>
      )}

      {/* TAB: TIMELINE (Full page experience for this case) */}
      {activeTab === 'timeline' && (
        <div style={{ width: '100%' }}>
          <TimelineView
            caseId={currentCase.id}
            timelineEvents={caseTimeline}
            onAddTimelineEvent={onAddTimelineEvent}
          />
        </div>
      )}

      {/* TAB: DRAFTS (Full page experience for this case) */}
      {activeTab === 'drafts' && (
        <div style={{ width: '100%' }}>
          <CaseDraftsTab
            currentCase={currentCase}
            drafts={caseDrafts}
            onOpenNewDraft={() => onOpenNewDraft?.(currentCase)}
            onSelectDraft={onSelectDraft}
          />
        </div>
      )}

      {/* TAB: BILLING (Full page experience for this case) */}
      {activeTab === 'billing' && (
        <div style={{ width: '100%' }}>
          <CaseBillingTab
            currentCase={currentCase}
            caseFinances={caseFinances}
            onOpenCreateInvoice={() => onOpenCreateInvoice?.(currentCase)}
            onOpenRecordPayment={() => onOpenRecordPayment?.(currentCase)}
            onOpenAddExpense={() => onOpenAddExpense?.(currentCase)}
          />
        </div>
      )}

      {/* TAB: CASE NOTES (Multi-note creation and deletion) */}
      {activeTab === 'notes' && (
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          {/* Notes Header Toolbar */}
          <div 
            className="card-base"
            style={{
              padding: 'var(--space-md) var(--space-lg)',
              borderRadius: 'var(--radius-lg)',
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: 'var(--space-md)'
            }}
          >
            <div>
              <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: '20px', color: 'var(--color-text-primary)', margin: 0 }}>
                Case Notes & Privileged Memos
              </h3>
              <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', margin: '2px 0 0 0' }}>
                Create, organize, and manage privileged strategy impressions and hearing notes for {currentCase.caseNumber}.
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
              {/* Search Notes */}
              <div style={{ position: 'relative', width: '220px' }}>
                <Search size={14} color="var(--color-text-muted)" style={{ position: 'absolute', left: '10px', top: '10px' }} />
                <input
                  type="text"
                  placeholder="Search notes..."
                  value={noteSearchQuery}
                  onChange={(e) => setNoteSearchQuery(e.target.value)}
                  className="input-base"
                  style={{ paddingLeft: '32px', paddingTop: '6px', paddingBottom: '6px', fontSize: '13px' }}
                />
              </div>

              <Button
                variant="primary"
                size="sm"
                icon={Plus}
                onClick={() => {
                  setEditingNoteId(null);
                  setNewNoteTitle('');
                  setNewNoteContent('');
                  setNewNoteCategory('Hearing Prep');
                  setIsAddingNote(true);
                }}
              >
                + New Case Note
              </Button>
            </div>
          </div>

          {/* New / Edit Note Modal / Inline Drawer */}
          {isAddingNote && (
            <div 
              className="card-base"
              style={{
                padding: 'var(--space-lg)',
                borderRadius: 'var(--radius-xl)',
                border: '2px solid var(--color-ink-500)',
                backgroundColor: 'var(--color-bg-surface)',
                boxShadow: 'var(--elevation-2)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
                <h4 style={{ fontFamily: 'var(--font-serif)', fontSize: '17px', margin: 0 }}>
                  {editingNoteId ? 'Edit Case Note' : 'Create New Case Note'}
                </h4>
                <button
                  onClick={() => setIsAddingNote(false)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}
                >
                  <X size={18} />
                </button>
              </div>

              <form onSubmit={handleSaveNote} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '70% 30%', gap: 'var(--space-sm)' }}>
                  <div>
                    <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', display: 'block', marginBottom: '4px' }}>
                      Note Title *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Cross-examination outline on forensic chain of custody"
                      value={newNoteTitle}
                      onChange={(e) => setNewNoteTitle(e.target.value)}
                      className="input-base"
                      style={{ fontSize: '13.5px' }}
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', display: 'block', marginBottom: '4px' }}>
                      Category
                    </label>
                    <select
                      value={newNoteCategory}
                      onChange={(e) => setNewNoteCategory(e.target.value)}
                      className="input-base"
                      style={{ fontSize: '13.5px' }}
                    >
                      <option value="Hearing Prep">Hearing Prep</option>
                      <option value="Strategy Memo">Strategy Memo</option>
                      <option value="Client Conference">Client Conference</option>
                      <option value="Evidence Review">Evidence Review</option>
                      <option value="Statutory Research">Statutory Research</option>
                      <option value="General">General</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', display: 'block', marginBottom: '4px' }}>
                    Note Content *
                  </label>
                  <textarea
                    rows={6}
                    required
                    placeholder="Enter confidential notes, key legal precedents, hearing observations, or action items..."
                    value={newNoteContent}
                    onChange={(e) => setNewNoteContent(e.target.value)}
                    className="input-base"
                    style={{ fontSize: '13.5px', lineHeight: 1.6 }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '6px' }}>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => setIsAddingNote(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    size="sm"
                    icon={Check}
                  >
                    {editingNoteId ? 'Update Note' : 'Save Note'}
                  </Button>
                </div>
              </form>
            </div>
          )}

          {/* Notes Grid */}
          {filteredNotes.length === 0 ? (
            <div 
              className="card-base"
              style={{
                padding: 'var(--space-2xl)',
                textAlign: 'center',
                color: 'var(--color-text-muted)'
              }}
            >
              <StickyNote size={36} color="var(--color-border-strong)" style={{ margin: '0 auto 12px auto' }} />
              <h4 style={{ margin: '0 0 6px 0', color: 'var(--color-text-primary)' }}>No notes found</h4>
              <p style={{ fontSize: 'var(--text-caption)', margin: '0 0 16px 0' }}>
                {noteSearchQuery ? 'No notes matched your search query.' : 'You have not created any notes for this case yet.'}
              </p>
              <Button
                variant="secondary"
                size="sm"
                icon={Plus}
                onClick={() => {
                  setEditingNoteId(null);
                  setNewNoteTitle('');
                  setNewNoteContent('');
                  setIsAddingNote(true);
                }}
              >
                Create your first note
              </Button>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 'var(--space-md)' }}>
              {filteredNotes.map((note) => (
                <div
                  key={note.id}
                  className="card-base"
                  style={{
                    padding: 'var(--space-md) var(--space-lg)',
                    borderRadius: 'var(--radius-lg)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: 'var(--space-sm)',
                    boxShadow: 'var(--elevation-1)',
                    transition: 'box-shadow 0.15s ease'
                  }}
                >
                  <div>
                    {/* Note Card Header */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px', marginBottom: '8px' }}>
                      <span
                        style={{
                          fontSize: '11px',
                          fontWeight: 600,
                          padding: '2px 8px',
                          borderRadius: 'var(--radius-sm)',
                          backgroundColor: 'var(--color-bg-surface-sunken)',
                          color: 'var(--color-accent-700)',
                          border: '1px solid var(--color-border-subtle)',
                          textTransform: 'uppercase',
                          letterSpacing: '0.04em'
                        }}
                      >
                        {note.category || 'General'}
                      </span>
                      
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <button
                          onClick={() => handleStartEditNote(note)}
                          title="Edit Note"
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            padding: '4px',
                            borderRadius: 'var(--radius-sm)',
                            color: 'var(--color-text-secondary)',
                            display: 'flex',
                            alignItems: 'center'
                          }}
                        >
                          <Edit2 size={14} />
                        </button>
                        <button
                          onClick={() => handleDeleteNote(note.id)}
                          title="Delete Note"
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            padding: '4px',
                            borderRadius: 'var(--radius-sm)',
                            color: 'var(--color-error-text)',
                            display: 'flex',
                            alignItems: 'center'
                          }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>

                    <h4 style={{ fontFamily: 'var(--font-serif)', fontSize: '16px', color: 'var(--color-text-primary)', margin: '0 0 6px 0', lineHeight: 1.3 }}>
                      {note.title}
                    </h4>

                    <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.6, whiteSpace: 'pre-wrap', margin: 0 }}>
                      {note.content}
                    </p>
                  </div>

                  {/* Note Footer */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '8px', borderTop: '1px solid var(--color-border-subtle)', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                    <span>{note.author || 'Advocate Note'}</span>
                    <span>{note.createdAt || 'Saved'}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB: CASE AI ASSISTANT (Dedicated full-height workspace fitting the webpage) */}
      {activeTab === 'ai' && (
        <div
          style={{
            height: 'calc(100vh - 180px)',
            minHeight: '650px',
            width: '100%',
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
              padding: '10px 18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '12.5px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '22px',
                  height: '22px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-ai-500)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF'
                }}
              >
                <Sparkles size={12} />
              </div>
              <span style={{ fontWeight: 700, color: 'var(--color-ink-700)' }}>
                LegalChat — Case Intelligence Workspace
              </span>
              <span style={{ color: 'var(--color-text-muted)' }}>&bull;</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{currentCase.caseNumber}</span>
              <span style={{ color: 'var(--color-text-muted)' }}>&bull;</span>
              <span style={{ color: 'var(--color-text-secondary)' }}>{currentCase.title}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.85)',
                  border: '1px solid var(--color-ai-border)',
                  padding: '3px 10px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '11.5px',
                  color: 'var(--color-text-secondary)',
                  fontWeight: 600
                }}
              >
                🔒 {caseDocs.length} Case Documents Locked in RAG
              </span>
            </div>
          </div>

          {/* Embedded AIAssistantView taking 100% of workspace */}
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
