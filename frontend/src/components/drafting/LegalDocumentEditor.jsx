import React, { useState, useRef, useEffect } from 'react';
import { 
  Save, 
  Download, 
  Printer, 
  History, 
  Sparkles, 
  ArrowLeft, 
  Check, 
  Copy, 
  Bold, 
  Italic, 
  Underline, 
  List, 
  ListOrdered, 
  AlignLeft, 
  AlignCenter, 
  AlignRight, 
  Undo, 
  Redo, 
  X, 
  Send, 
  FileText,
  Clock,
  RotateCcw,
  Scale,
  Zap,
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  ChevronDown,
  Layers,
  Wand2
} from 'lucide-react';
import { Button } from '../common/Button';
import { draftingService } from '../../services/draftingService';

export const LegalDocumentEditor = ({ 
  draft, 
  onBack, 
  onSave 
}) => {
  const [content, setContent] = useState(draft.content || '');
  const [title, setTitle] = useState(draft.title || '');
  const [saveStatus, setSaveStatus] = useState('Saved'); // 'Saved' | 'Saving...' | 'Unsaved changes'
  const [showHistory, setShowHistory] = useState(false);
  const [showAIAssistant, setShowAIAssistant] = useState(true);
  const [versions, setVersions] = useState(draft.versions || []);
  const [selectedText, setSelectedText] = useState('');
  
  // AI Copilot State
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiGenerating, setAiGenerating] = useState(false);
  const [historyStack, setHistoryStack] = useState([]); // Array of { content, summary, timestamp }
  const [notification, setNotification] = useState(null); // { type, message, summary }

  const [aiSuggestions, setAiSuggestions] = useState([
    {
      id: 'sug-initial-1',
      title: 'Statutory Direct Writing Active',
      text: 'Direct Draft Writing is active: You can ask the AI to "fill the address as XYZ", "replace client with ABC", or "draft a petition under BNSS 482 with these facts..." and it will directly write into this draft.',
      explanation: 'Statutory AI Copilot connected to Qwen-32B Indian Legal Engine.',
      applied: true
    }
  ]);

  const editorRef = useRef(null);

  // Monitor text selection within the textarea
  const handleSelectText = () => {
    const textarea = editorRef.current;
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    if (start !== end) {
      const text = textarea.value.substring(start, end);
      if (text.trim().length > 3) {
        setSelectedText(text);
      }
    } else {
      setSelectedText('');
    }
  };

  const handleContentChange = (e) => {
    setContent(e.target.value);
    setSaveStatus('Unsaved changes');
  };

  const handleManualSave = async () => {
    setSaveStatus('Saving...');
    const updated = await draftingService.saveDraft(draft.id, content);
    if (updated) {
      setVersions(updated.versions || []);
    }
    setTimeout(() => {
      setSaveStatus('Saved');
      onSave && onSave(updated || { ...draft, content });
    }, 350);
  };

  // Quick formatting insertion
  const applyFormatting = (prefix, suffix = '') => {
    const textarea = editorRef.current;
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = textarea.value.substring(start, end) || 'text';
    const replacement = `${prefix}${selected}${suffix}`;

    const newContent = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
    setContent(newContent);
    setSaveStatus('Unsaved changes');
  };

  // --- Core Statutory AI Copilot Action: Direct Writing & Editing ---
  const handleAISubmitPrompt = async (promptOverride = null) => {
    const textToSubmit = (typeof promptOverride === 'string' ? promptOverride : aiPrompt).trim();
    if (!textToSubmit) return;

    setAiGenerating(true);
    if (typeof promptOverride !== 'string') {
      setAiPrompt('');
    }

    try {
      const res = await draftingService.aiDraftingCopilot({
        instruction: textToSubmit,
        currentDocument: content,
        documentType: draft?.documentType || 'Legal Notice',
        documentTitle: title,
        selectedText: selectedText,
        caseId: draft?.caseId
      });

      if (res && res.updated_document) {
        // 1. Record in undo stack for 1-click revert
        setHistoryStack(prev => [{ content, summary: res.summary, timestamp: Date.now() }, ...prev]);

        // 2. Direct writing into the draft editor!
        setContent(res.updated_document);
        setSaveStatus('Unsaved changes');

        // 3. Set toast notification
        setNotification({
          type: 'success',
          summary: res.summary,
          action: res.action,
          timestamp: Date.now()
        });

        // 4. Prepend to contextual suggestions drawer
        const newSug = {
          id: `sug-${Date.now()}`,
          title: res.summary || `AI Action: ${textToSubmit.substring(0, 30)}...`,
          text: res.suggested_clause || res.updated_document.substring(0, 240) + '...',
          explanation: res.explanation || `Direct synthesis addressing: "${textToSubmit}"`,
          applied: true,
          action: res.action,
          fullDocument: res.updated_document,
          previousDocument: content
        };
        setAiSuggestions(prev => [newSug, ...prev]);
      }
    } catch (err) {
      console.error('Statutory AI Drafting Copilot failed:', err);
      setNotification({
        type: 'error',
        summary: `Drafting error: ${err.message || 'Failed to update draft'}`
      });
    } finally {
      setAiGenerating(false);
    }
  };

  // 1-Click Undo last AI action
  const handleUndoAIAction = () => {
    if (historyStack.length === 0) return;
    const [previous, ...rest] = historyStack;
    setContent(previous.content);
    setHistoryStack(rest);
    setSaveStatus('Unsaved changes');
    setNotification({
      type: 'info',
      summary: `Reverted AI change: "${previous.summary}"`
    });
  };

  // Re-apply a specific full document from suggestions
  const handleReapplyDocument = (docText) => {
    setHistoryStack(prev => [{ content, summary: 'Manual re-apply', timestamp: Date.now() }, ...prev]);
    setContent(docText);
    setSaveStatus('Unsaved changes');
  };

  // Insert a clause at cursor or append
  const handleInsertClauseAtCursor = (clauseText) => {
    const textarea = editorRef.current;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newContent = textarea.value.substring(0, start) + '\n\n' + clauseText + '\n\n' + textarea.value.substring(end);
      setContent(newContent);
    } else {
      setContent(prev => prev + '\n\n' + clauseText);
    }
    setSaveStatus('Unsaved changes');
  };

  // AI Litigator Actions - now powered by direct statutory drafting!
  const handleStrengthenGrounds = () => {
    handleAISubmitPrompt("Strengthen the legal grounds of this document with authoritative Indian statutory provisions and landmark Supreme Court jurisprudence.");
  };

  const handleInsertPrayer = () => {
    handleAISubmitPrompt("Insert a formal, comprehensive prayer clause seeking appropriate ad-interim and final reliefs tailored to this draft.");
  };

  const handleVerifyCitations = () => {
    handleAISubmitPrompt("Audit and verify all statutory citations in this document, updating any legacy IPC/CrPC/IEA sections to Bharatiya Nyaya Sanhita 2023, Bharatiya Nagarik Suraksha Sanhita 2023, and Bharatiya Sakshya Adhiniyam 2023.");
  };

  const handleApplyCourtFormat = () => {
    const headerBlock = `BEFORE THE HON'BLE COURT OF COMPETENT JURISDICTION\nMEMORANDUM OF PARTIES & FORMAL PLEADING\n============================================================\n\n`;
    const footerBlock = `\n\nVERIFICATION AFFIDAVIT:\nI, the deponent abovenamed, do hereby solemnly declare and verify that the contents of paragraphs 1 to ___ of the accompanying petition are true and correct to my knowledge derived from record, and no part of it is false and nothing material has been concealed therefrom.\n\nVerified at New Delhi on this ${new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}.\n\nDEPONENT`;
    if (!content.includes('VERIFICATION AFFIDAVIT')) {
      setHistoryStack(prev => [{ content, summary: 'Court pleading format added', timestamp: Date.now() }, ...prev]);
      setContent(headerBlock + content + footerBlock);
      setSaveStatus('Unsaved changes');
      setNotification({
        type: 'success',
        summary: 'Court Pleading Header & Verification Affidavit added.'
      });
    }
  };

  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 64px)', backgroundColor: 'var(--color-bg-canvas)' }}>
      {/* 1. Header Toolbar */}
      <div style={{
        padding: '10px 18px',
        backgroundColor: 'var(--color-bg-surface)',
        borderBottom: '1px solid var(--color-border-subtle)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={onBack}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '12.5px',
              fontWeight: 500
            }}
          >
            <ArrowLeft size={16} /> Back to Studio
          </button>

          <span style={{ color: 'var(--color-border-default)' }}>|</span>

          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{
              fontFamily: 'var(--font-serif)',
              fontSize: '16px',
              fontWeight: 700,
              color: 'var(--color-text-primary)',
              backgroundColor: 'transparent',
              border: 'none',
              borderBottom: '1px dashed var(--color-border-default)',
              padding: '2px 4px',
              minWidth: '320px'
            }}
          />

          <span style={{
            fontSize: '11px',
            fontWeight: 650,
            padding: '2px 8px',
            borderRadius: '4px',
            backgroundColor: 'var(--color-bg-surface-sunken)',
            color: 'var(--color-ink-700)',
            fontFamily: 'var(--font-mono)'
          }}>
            {draft.caseNumber || 'General Draft'}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {historyStack.length > 0 && (
            <button
              onClick={handleUndoAIAction}
              title="Undo last AI modification"
              style={{
                padding: '4px 10px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border-default)',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                color: 'var(--color-text-secondary)',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <RotateCcw size={12} /> Undo AI Edit
            </button>
          )}

          <span style={{
            fontSize: '11px',
            color: saveStatus === 'Saved' ? '#10B981' : 'var(--color-text-muted)',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            {saveStatus === 'Saved' ? <Check size={13} color="#10B981" /> : <Clock size={13} />}
            {saveStatus}
          </span>

          <Button
            variant="secondary"
            size="sm"
            icon={Printer}
            onClick={() => window.print()}
          >
            Print
          </Button>

          <Button
            variant="secondary"
            size="sm"
            icon={History}
            onClick={() => setShowHistory(!showHistory)}
          >
            Versions ({versions.length})
          </Button>

          <Button
            variant="primary"
            size="sm"
            icon={Save}
            onClick={handleManualSave}
          >
            Save Draft
          </Button>

          <button
            onClick={() => setShowAIAssistant(!showAIAssistant)}
            style={{
              padding: '6px 12px',
              borderRadius: 'var(--radius-sm)',
              border: showAIAssistant ? '1px solid #14B8A6' : '1px solid var(--color-border-default)',
              backgroundColor: showAIAssistant ? 'rgba(20, 184, 166, 0.15)' : 'var(--color-bg-surface-sunken)',
              color: showAIAssistant ? '#2DD4BF' : 'var(--color-text-secondary)',
              fontSize: '12px',
              fontWeight: 650,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Sparkles size={14} /> AI Assistant
          </button>
        </div>
      </div>

      {/* 2. Formatting & AI Litigator Toolbar */}
      <div style={{
        padding: '6px 18px',
        backgroundColor: 'var(--color-bg-surface-sunken)',
        borderBottom: '1px solid var(--color-border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '8px',
        flexShrink: 0
      }}>
        {/* Basic Text Formatting */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button
            type="button"
            onClick={() => applyFormatting('**', '**')}
            title="Bold (Ctrl+B)"
            style={{ padding: '5px 8px', borderRadius: '4px', border: 'none', background: 'none', color: 'var(--color-text-primary)', cursor: 'pointer' }}
          >
            <Bold size={14} />
          </button>
          <button
            type="button"
            onClick={() => applyFormatting('*', '*')}
            title="Italic (Ctrl+I)"
            style={{ padding: '5px 8px', borderRadius: '4px', border: 'none', background: 'none', color: 'var(--color-text-primary)', cursor: 'pointer' }}
          >
            <Italic size={14} />
          </button>
          <button
            type="button"
            onClick={() => applyFormatting('\n- ')}
            title="Bullet List"
            style={{ padding: '5px 8px', borderRadius: '4px', border: 'none', background: 'none', color: 'var(--color-text-primary)', cursor: 'pointer' }}
          >
            <List size={14} />
          </button>
          <button
            type="button"
            onClick={() => applyFormatting('\n1. ')}
            title="Numbered List"
            style={{ padding: '5px 8px', borderRadius: '4px', border: 'none', background: 'none', color: 'var(--color-text-primary)', cursor: 'pointer' }}
          >
            <ListOrdered size={14} />
          </button>

          <span style={{ color: 'var(--color-border-default)', margin: '0 4px' }}>|</span>

          {/* AI Direct Litigation Actions */}
          <button
            type="button"
            onClick={handleStrengthenGrounds}
            disabled={aiGenerating}
            style={{
              padding: '4px 10px',
              borderRadius: '6px',
              backgroundColor: 'rgba(245, 158, 11, 0.15)',
              border: '1px solid rgba(245, 158, 11, 0.35)',
              color: '#FBBF24',
              fontSize: '11px',
              fontWeight: 650,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              opacity: aiGenerating ? 0.6 : 1
            }}
          >
            <Zap size={12} /> + Strengthen Grounds
          </button>

          <button
            type="button"
            onClick={handleInsertPrayer}
            disabled={aiGenerating}
            style={{
              padding: '4px 10px',
              borderRadius: '6px',
              backgroundColor: 'rgba(14, 165, 233, 0.15)',
              border: '1px solid rgba(14, 165, 233, 0.35)',
              color: '#38BDF8',
              fontSize: '11px',
              fontWeight: 650,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              opacity: aiGenerating ? 0.6 : 1
            }}
          >
            <Scale size={12} /> + Insert Prayer Clause
          </button>

          <button
            type="button"
            onClick={handleVerifyCitations}
            disabled={aiGenerating}
            style={{
              padding: '4px 10px',
              borderRadius: '6px',
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.35)',
              color: '#34D399',
              fontSize: '11px',
              fontWeight: 650,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              opacity: aiGenerating ? 0.6 : 1
            }}
          >
            <CheckCircle2 size={12} /> Verify BNS/BNSS Citations
          </button>

          <button
            type="button"
            onClick={handleApplyCourtFormat}
            style={{
              padding: '4px 10px',
              borderRadius: '6px',
              backgroundColor: 'var(--color-bg-surface)',
              border: '1px solid var(--color-border-default)',
              color: 'var(--color-text-secondary)',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <Layers size={12} /> Court Pleading Format
          </button>
        </div>

        {/* Word Count */}
        <div style={{ fontSize: '11.5px', color: 'var(--color-text-muted)' }}>
          {wordCount} words &bull; {content.length} chars
        </div>
      </div>

      {/* Direct AI Action Notification Banner */}
      {notification && (
        <div style={{
          padding: '8px 18px',
          backgroundColor: notification.type === 'error' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
          borderBottom: `1px solid ${notification.type === 'error' ? '#EF4444' : '#10B981'}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '12px',
          color: 'var(--color-text-primary)',
          flexShrink: 0
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={14} color={notification.type === 'error' ? '#EF4444' : '#10B981'} />
            <strong>Direct AI Writing:</strong> {notification.summary}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {historyStack.length > 0 && (
              <button
                type="button"
                onClick={handleUndoAIAction}
                style={{
                  background: 'var(--color-bg-surface)',
                  border: '1px solid var(--color-border-default)',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '11px',
                  fontWeight: 650,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  color: 'var(--color-text-secondary)'
                }}
              >
                <RotateCcw size={11} /> Undo
              </button>
            )}
            <button
              type="button"
              onClick={() => setNotification(null)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}
            >
              <X size={13} />
            </button>
          </div>
        </div>
      )}

      {/* 3. Main Workspace: Canvas + AI Dock */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        
        {/* Editor Area (Legal Paper Style) */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '24px',
          display: 'flex',
          justifyContent: 'center',
          backgroundColor: 'var(--color-bg-canvas)'
        }}>
          <div style={{
            width: '100%',
            maxWidth: '820px',
            minHeight: '750px',
            backgroundColor: 'var(--color-bg-surface)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--color-border-subtle)',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
            padding: '36px 44px',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <textarea
              ref={editorRef}
              value={content}
              onChange={handleContentChange}
              onSelect={handleSelectText}
              placeholder="Begin typing your legal pleading, application grounds, or notice..."
              style={{
                width: '100%',
                flex: 1,
                minHeight: '650px',
                border: 'none',
                outline: 'none',
                resize: 'none',
                backgroundColor: 'transparent',
                color: 'var(--color-text-primary)',
                fontFamily: 'Georgia, Cambria, serif',
                fontSize: '15px',
                lineHeight: 1.7,
                letterSpacing: '0.01em',
                whiteSpace: 'pre-wrap'
              }}
            />
          </div>
        </div>

        {/* 4. Docked AI Assistant (Right Drawer) */}
        {showAIAssistant && (
          <div style={{
            width: '380px',
            backgroundColor: 'var(--color-bg-surface)',
            borderLeft: '1px solid var(--color-border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            flexShrink: 0
          }}>
            {/* AI Dock Header */}
            <div style={{
              padding: '12px 16px',
              borderBottom: '1px solid var(--color-border-subtle)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              backgroundColor: 'var(--color-bg-surface-sunken)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={14} color="#14B8A6" />
                <strong style={{ fontSize: '13px', color: 'var(--color-text-primary)' }}>
                  Statutory AI Drafting Copilot
                </strong>
              </div>
              <button
                type="button"
                onClick={() => setShowAIAssistant(false)}
                style={{ background: 'none', border: 'none', color: 'var(--color-text-muted)', cursor: 'pointer' }}
              >
                <X size={15} />
              </button>
            </div>

            {/* Quick Action Chips */}
            <div style={{ padding: '12px', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <span style={{ fontSize: '11px', fontWeight: 650, color: 'var(--color-text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
                Quick Litigator Prompts (Direct Write)
              </span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {[
                  "Draft Parity & Bail Grounds under BNSS §480",
                  "Insert Notice of Motion Injunction Prayer",
                  "Add Demurrage Suspension Force Majeure Clause",
                  "Add Section 63 BSA Electronic Certificate Objection"
                ].map((chip, idx) => (
                  <button
                    key={idx}
                    type="button"
                    disabled={aiGenerating}
                    onClick={() => handleAISubmitPrompt(chip)}
                    style={{
                      padding: '6px 10px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      border: '1px solid var(--color-border-subtle)',
                      color: 'var(--color-text-secondary)',
                      fontSize: '11px',
                      textAlign: 'left',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      opacity: aiGenerating ? 0.6 : 1
                    }}
                  >
                    + {chip}
                  </button>
                ))}
              </div>
            </div>

            {/* AI Prompt Input */}
            <div style={{ padding: '12px', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <div style={{ display: 'flex', gap: '6px' }}>
                <input
                  type="text"
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !aiGenerating && handleAISubmitPrompt()}
                  placeholder="Ask AI to fill, replace, draft, or refine…"
                  className="input-base"
                  disabled={aiGenerating}
                  style={{ fontSize: '12px', padding: '6px 10px' }}
                />
                <Button
                  variant="primary"
                  size="sm"
                  loading={aiGenerating}
                  onClick={() => handleAISubmitPrompt()}
                >
                  <Send size={13} />
                </Button>
              </div>
              <span style={{ fontSize: '10.5px', color: 'var(--color-text-muted)', display: 'block', marginTop: '4px' }}>
                💡 Direct editing active: "fill address as XYZ", "replace client...", "draft a petition with..."
              </span>
            </div>

            {/* AI Generated Suggestions List */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '12px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '11px', fontWeight: 650, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                  Draft Actions & Syntheses ({aiSuggestions.length})
                </span>
                {historyStack.length > 0 && (
                  <button
                    type="button"
                    onClick={handleUndoAIAction}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#F59E0B',
                      fontSize: '11px',
                      fontWeight: 650,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '3px'
                    }}
                  >
                    <RotateCcw size={10} /> Undo Last ({historyStack.length})
                  </button>
                )}
              </div>

              {aiSuggestions.map(sug => (
                <div
                  key={sug.id}
                  style={{
                    padding: '12px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'var(--color-bg-surface-sunken)',
                    border: '1px solid var(--color-border-subtle)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ fontSize: '12px', color: 'var(--color-text-primary)' }}>
                      {sug.title}
                    </strong>
                    <span style={{
                      fontSize: '9.5px',
                      color: sug.applied ? '#10B981' : '#3B82F6',
                      fontWeight: 700,
                      backgroundColor: sug.applied ? 'rgba(16, 185, 129, 0.12)' : 'rgba(59, 130, 246, 0.12)',
                      padding: '2px 6px',
                      borderRadius: '4px'
                    }}>
                      {sug.applied ? 'APPLIED TO DRAFT' : 'VERIFIED'}
                    </span>
                  </div>

                  <p style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.4, fontFamily: 'Georgia, serif' }}>
                    "{sug.text}"
                  </p>

                  <span style={{ fontSize: '10.5px', color: 'var(--color-text-muted)' }}>
                    {sug.explanation}
                  </span>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '6px', marginTop: '4px' }}>
                    {sug.fullDocument && sug.fullDocument !== content && (
                      <button
                        type="button"
                        onClick={() => handleReapplyDocument(sug.fullDocument)}
                        style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: 'var(--color-bg-surface)',
                          border: '1px solid var(--color-border-default)',
                          color: 'var(--color-text-link)',
                          fontSize: '11px',
                          fontWeight: 650,
                          cursor: 'pointer'
                        }}
                      >
                        Re-apply Full Draft
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={() => handleInsertClauseAtCursor(sug.text)}
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: 'var(--color-bg-surface)',
                        border: '1px solid var(--color-border-default)',
                        color: 'var(--color-text-secondary)',
                        fontSize: '11px',
                        fontWeight: 650,
                        cursor: 'pointer'
                      }}
                    >
                      Insert at Cursor
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
