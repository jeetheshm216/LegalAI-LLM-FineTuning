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
  RotateCcw
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
  
  // Selected-text floating actions state
  const [selectedText, setSelectedText] = useState('');
  const [floatingActionPos, setFloatingActionPos] = useState(null);
  const [isFloatingPopupOpen, setIsFloatingPopupOpen] = useState(false);

  // AI Assistant Dock State
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState([
    {
      id: 'sug-1',
      title: 'Preliminary Injunction Reference',
      text: 'Pursuant to the Ad-Interim Injunction Order passed by Commercial Bench IV on September 2, 2026, status quo has been directed over the catalytic cargo.',
      explanation: 'Replaces passive phrasing with precise judicial bench order citation.'
    }
  ]);

  const editorRef = useRef(null);

  // Autosave simulation
  const handleContentChange = (e) => {
    setContent(e.target.value);
    setSaveStatus('Unsaved changes');
  };

  const handleManualSave = async () => {
    setSaveStatus('Saving...');
    const updated = await draftingService.saveDraft(draft.id, content);
    if (updated) {
      setVersions(updated.versions);
    }
    setTimeout(() => {
      setSaveStatus('Saved');
      onSave && onSave(updated || { ...draft, content });
    }, 400);
  };

  // Monitor text selection within the textarea
  const handleSelectText = () => {
    const textarea = editorRef.current;
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    if (start !== end) {
      const text = textarea.value.substring(start, end);
      if (text.trim().length > 4) {
        setSelectedText(text);
        setFloatingActionPos({ top: 120, left: 320 });
        return;
      }
    }
    if (!isFloatingPopupOpen) {
      setFloatingActionPos(null);
      setSelectedText('');
    }
  };

  // Quick formatting insertion
  const applyFormatting = (prefix, suffix = '') => {
    const textarea = editorRef.current;
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const sel = text.substring(start, end);

    const newText = text.substring(0, start) + prefix + sel + suffix + text.substring(end);
    setContent(newText);
    setSaveStatus('Unsaved changes');
  };

  // Execute AI action
  const handleAIAction = async (actionType, customText) => {
    setAiGenerating(true);
    const result = await draftingService.aiDraftingAction({
      actionType,
      selectedText,
      fullDocumentText: content,
      customInstruction: customText || aiPrompt
    });

    setAiSuggestions(prev => [
      {
        id: `sug-${Date.now()}`,
        title: actionType.toUpperCase(),
        text: result.suggestion,
        explanation: result.explanation
      },
      ...prev
    ]);
    setAiGenerating(false);
    setAiPrompt('');
  };

  // Insert suggestion into document
  const handleInsertSuggestion = (sugText) => {
    setContent(prev => prev + '\n\n' + sugText);
    setSaveStatus('Unsaved changes');
  };

  // Replace selection with suggestion
  const handleReplaceSelection = (sugText) => {
    if (selectedText) {
      setContent(prev => prev.replace(selectedText, sugText));
    } else {
      setContent(prev => prev + '\n\n' + sugText);
    }
    setSaveStatus('Unsaved changes');
    setSelectedText('');
    setIsFloatingPopupOpen(false);
  };

  // Restore previous version
  const handleRestoreVersion = (ver) => {
    setContent(draft.content); // Or version specific content
    alert(`Restored document to ${ver.versionNumber}.`);
    setShowHistory(false);
  };

  const wordCount = content.split(/\s+/).filter(Boolean).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - var(--header-height) - 10px)', minHeight: '680px' }}>
      
      {/* 1. Editor Master Header */}
      <div
        style={{
          padding: 'var(--space-sm) var(--space-md)',
          backgroundColor: 'var(--color-bg-surface)',
          borderBottom: '1px solid var(--color-border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 'var(--space-md)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
          <button
            onClick={onBack}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--color-text-secondary)',
              display: 'flex',
              alignItems: 'center'
            }}
            aria-label="Back to Drafts"
          >
            <ArrowLeft size={18} />
          </button>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
              <input
                type="text"
                value={title}
                onChange={(e) => { setTitle(e.target.value); setSaveStatus('Unsaved changes'); }}
                style={{
                  fontFamily: 'var(--font-serif)',
                  fontSize: '18px',
                  fontWeight: 600,
                  color: 'var(--color-text-primary)',
                  border: 'none',
                  background: 'transparent',
                  outline: 'none',
                  minWidth: '280px'
                }}
              />
              <span
                style={{
                  fontSize: '11px',
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--color-bg-surface-sunken)',
                  color: 'var(--color-text-secondary)',
                  fontFamily: 'var(--font-mono)'
                }}
              >
                {draft.caseNumber || "General Matter"}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: 'var(--color-text-muted)' }}>
              <span>{draft.documentType}</span>
              <span>&bull;</span>
              <span>{draft.version}</span>
              <span>&bull;</span>
              <span style={{ color: saveStatus === 'Saved' ? 'var(--color-success-text)' : 'var(--color-case-urgent-text)' }}>
                {saveStatus}
              </span>
            </div>
          </div>
        </div>

        {/* Right Header Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
          <Button
            variant="secondary"
            size="sm"
            icon={History}
            onClick={() => setShowHistory(!showHistory)}
          >
            History
          </Button>

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
            icon={Download}
            onClick={() => alert(`Exporting ${title} as PDF / DOCX...`)}
          >
            Export
          </Button>

          <Button
            variant="primary"
            size="sm"
            icon={Save}
            onClick={handleManualSave}
          >
            Save Draft
          </Button>

          <Button
            variant={showAIAssistant ? "accent" : "secondary"}
            size="sm"
            icon={Sparkles}
            onClick={() => setShowAIAssistant(!showAIAssistant)}
          >
            AI Assistant
          </Button>
        </div>
      </div>

      {/* 2. Formatting Toolbar */}
      <div
        style={{
          padding: '4px var(--space-md)',
          backgroundColor: 'var(--color-bg-surface-sunken)',
          borderBottom: '1px solid var(--color-border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 'var(--space-xs)',
          fontSize: '12px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button
            type="button"
            onClick={() => applyFormatting('**', '**')}
            title="Bold"
            style={{ padding: '4px 6px', background: 'none', border: '1px solid transparent', cursor: 'pointer', borderRadius: 'var(--radius-sm)' }}
          >
            <Bold size={14} />
          </button>
          <button
            type="button"
            onClick={() => applyFormatting('*', '*')}
            title="Italic"
            style={{ padding: '4px 6px', background: 'none', border: '1px solid transparent', cursor: 'pointer', borderRadius: 'var(--radius-sm)' }}
          >
            <Italic size={14} />
          </button>
          <button
            type="button"
            onClick={() => applyFormatting('<u>', '</u>')}
            title="Underline"
            style={{ padding: '4px 6px', background: 'none', border: '1px solid transparent', cursor: 'pointer', borderRadius: 'var(--radius-sm)' }}
          >
            <Underline size={14} />
          </button>

          <span style={{ width: '1px', height: '16px', backgroundColor: 'var(--color-border-default)', margin: '0 4px' }} />

          <button
            type="button"
            onClick={() => applyFormatting('\n### ')}
            title="Section Heading"
            style={{ padding: '2px 6px', background: 'none', border: '1px solid var(--color-border-default)', cursor: 'pointer', borderRadius: 'var(--radius-sm)', fontSize: '11px', fontWeight: 600 }}
          >
            H3
          </button>
          <button
            type="button"
            onClick={() => applyFormatting('\n1. ')}
            title="Numbered list"
            style={{ padding: '4px 6px', background: 'none', border: '1px solid transparent', cursor: 'pointer', borderRadius: 'var(--radius-sm)' }}
          >
            <ListOrdered size={14} />
          </button>
          <button
            type="button"
            onClick={() => applyFormatting('\n- ')}
            title="Bullet list"
            style={{ padding: '4px 6px', background: 'none', border: '1px solid transparent', cursor: 'pointer', borderRadius: 'var(--radius-sm)' }}
          >
            <List size={14} />
          </button>
        </div>

        <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
          {wordCount} words &bull; UTF-8 Legal Text
        </div>
      </div>

      {/* 3. Main Workspace Area: Document Canvas (Left) + AI Drafting Dock (Right) */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden', position: 'relative' }}>
        
        {/* Document Editor Paper Canvas (§2.8: Paper stays clean light even in dark mode) */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: 'var(--space-xl) var(--space-md)',
            backgroundColor: 'var(--color-bg-canvas)',
            display: 'flex',
            justifyContent: 'center'
          }}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '680px',
              minHeight: '800px',
              backgroundColor: 'var(--color-doc-page)',
              color: '#171E26',
              boxShadow: 'var(--elevation-2)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border-subtle)',
              padding: 'var(--space-2xl) var(--space-xl)',
              display: 'flex',
              flexDirection: 'column',
              position: 'relative'
            }}
          >
            <textarea
              ref={editorRef}
              value={content}
              onChange={handleContentChange}
              onSelect={handleSelectText}
              placeholder="Begin drafting legal submission, affidavit, or notice…"
              style={{
                width: '100%',
                flex: 1,
                minHeight: '720px',
                border: 'none',
                outline: 'none',
                backgroundColor: 'transparent',
                color: '#171E26',
                fontFamily: 'var(--font-serif)',
                fontSize: '15px',
                lineHeight: 1.7,
                resize: 'none',
                letterSpacing: '0.01em'
              }}
            />
          </div>
        </div>

        {/* Selected-Text Floating Drafting Action Toolbar (§12) */}
        {selectedText && (
          <div
            style={{
              position: 'fixed',
              top: '180px',
              left: '50%',
              transform: 'translateX(-50%)',
              zIndex: 'var(--z-selected-text-popup)',
              backgroundColor: 'var(--color-bg-surface-raised)',
              border: '1px solid var(--color-ai-border)',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--elevation-3)',
              padding: '4px 8px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              animation: 'fadeIn 0.15s ease-out'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--color-ai-500)', fontWeight: 600, paddingRight: '6px', borderRight: '1px solid var(--color-border-subtle)' }}>
              <Sparkles size={12} />
              <span>Drafting AI:</span>
            </div>

            <button
              onClick={() => handleAIAction('formal')}
              style={{ padding: '3px 8px', background: 'none', border: 'none', fontSize: '11px', cursor: 'pointer', color: 'var(--color-text-primary)' }}
            >
              Make More Formal
            </button>
            <button
              onClick={() => handleAIAction('simplify')}
              style={{ padding: '3px 8px', background: 'none', border: 'none', fontSize: '11px', cursor: 'pointer', color: 'var(--color-text-primary)' }}
            >
              Simplify
            </button>
            <button
              onClick={() => handleAIAction('expand')}
              style={{ padding: '3px 8px', background: 'none', border: 'none', fontSize: '11px', cursor: 'pointer', color: 'var(--color-text-primary)' }}
            >
              Expand
            </button>
            <button
              onClick={() => handleAIAction('explain')}
              style={{ padding: '3px 8px', background: 'none', border: 'none', fontSize: '11px', cursor: 'pointer', color: 'var(--color-text-primary)' }}
            >
              Explain Clause
            </button>
            <button
              onClick={() => setSelectedText('')}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: '2px' }}
            >
              <X size={13} />
            </button>
          </div>
        )}

        {/* 4. Right-Side AI Drafting Assistant Dock (§ Feature 2) */}
        {showAIAssistant && (
          <div
            style={{
              width: '380px',
              maxWidth: '100%',
              backgroundColor: 'var(--color-bg-surface)',
              borderLeft: '1px solid var(--color-ai-border)',
              display: 'flex',
              flexDirection: 'column',
              zIndex: 20
            }}
          >
            {/* Dock Header */}
            <div
              style={{
                padding: 'var(--space-sm) var(--space-md)',
                backgroundColor: 'var(--color-ai-100)',
                borderBottom: '1px solid var(--color-ai-border)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
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
                <span style={{ fontWeight: 600, fontSize: 'var(--text-caption)', color: 'var(--color-ink-700)' }}>
                  AI Drafting Assistant
                </span>
              </div>

              <button
                onClick={() => setShowAIAssistant(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}
              >
                <X size={15} />
              </button>
            </div>

            {/* Quick Action Chips per Prompt (§ DRAFTING AI ASSISTANT) */}
            <div style={{ padding: 'var(--space-sm)', borderBottom: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface-sunken)' }}>
              <div style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)', marginBottom: '6px', fontWeight: 600 }}>
                Drafting Assistants
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                <button
                  onClick={() => handleAIAction('formal')}
                  style={{ padding: '3px 8px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-ai-border)', backgroundColor: 'var(--color-bg-surface)', fontSize: '11px', cursor: 'pointer', color: 'var(--color-text-primary)' }}
                >
                  Make More Formal
                </button>
                <button
                  onClick={() => handleAIAction('expand')}
                  style={{ padding: '3px 8px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-ai-border)', backgroundColor: 'var(--color-bg-surface)', fontSize: '11px', cursor: 'pointer', color: 'var(--color-text-primary)' }}
                >
                  Expand Citing Precedents
                </button>
                <button
                  onClick={() => handleAIAction('consistency')}
                  style={{ padding: '3px 8px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-ai-border)', backgroundColor: 'var(--color-bg-surface)', fontSize: '11px', cursor: 'pointer', color: 'var(--color-text-primary)' }}
                >
                  Check Consistency
                </button>
                <button
                  onClick={() => handleAIAction('simplify')}
                  style={{ padding: '3px 8px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-ai-border)', backgroundColor: 'var(--color-bg-surface)', fontSize: '11px', cursor: 'pointer', color: 'var(--color-text-primary)' }}
                >
                  Simplify for Client
                </button>
              </div>
            </div>

            {/* Suggestions Stream */}
            <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-sm)', display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              {aiGenerating && (
                <div style={{ padding: 'var(--space-md)', textAlign: 'center', color: 'var(--color-ai-500)', fontSize: '12px' }}>
                  Synthesizing legal clause suggestions…
                </div>
              )}

              {aiSuggestions.map(sug => (
                <div
                  key={sug.id}
                  style={{
                    padding: 'var(--space-sm)',
                    backgroundColor: 'var(--color-ai-100)',
                    border: '1px solid var(--color-ai-border)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '12px'
                  }}
                >
                  <div style={{ fontWeight: 600, color: 'var(--color-ai-500)', marginBottom: '4px', fontSize: '11px', textTransform: 'uppercase' }}>
                    {sug.title}
                  </div>
                  <p style={{ lineHeight: 1.5, color: 'var(--color-text-primary)', marginBottom: '6px' }}>
                    "{sug.text}"
                  </p>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-secondary)', fontStyle: 'italic', marginBottom: '8px' }}>
                    {sug.explanation}
                  </div>

                  <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleReplaceSelection(sug.text)}
                    >
                      Replace Selection
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleInsertSuggestion(sug.text)}
                    >
                      Insert into Draft
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            {/* Prompt Input Area */}
            <form
              onSubmit={(e) => { e.preventDefault(); if (aiPrompt.trim()) handleAIAction('custom', aiPrompt); }}
              style={{
                padding: 'var(--space-sm)',
                borderTop: '1px solid var(--color-border-subtle)',
                backgroundColor: 'var(--color-bg-surface)'
              }}
            >
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  placeholder="Ask AI drafting assistant…"
                  className="input-base"
                  style={{ paddingRight: '32px', fontSize: '12px', height: '34px' }}
                />
                <button
                  type="submit"
                  disabled={!aiPrompt.trim()}
                  style={{
                    position: 'absolute',
                    right: '6px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'var(--color-ink-700)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '24px',
                    height: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--color-text-on-ink)',
                    cursor: aiPrompt.trim() ? 'pointer' : 'not-allowed',
                    opacity: aiPrompt.trim() ? 1 : 0.4
                  }}
                >
                  <Send size={11} />
                </button>
              </div>
            </form>
          </div>
        )}

        {/* 5. Version History Slide-Out Panel (§ DRAFTING VERSION HISTORY) */}
        {showHistory && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              right: 0,
              bottom: 0,
              width: '320px',
              backgroundColor: 'var(--color-bg-surface-raised)',
              borderLeft: '1px solid var(--color-border-subtle)',
              boxShadow: 'var(--elevation-2)',
              zIndex: 30,
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <div style={{ padding: 'var(--space-md)', borderBottom: '1px solid var(--color-border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontWeight: 600, fontSize: 'var(--text-h3)' }}>Version History</div>
              <button onClick={() => setShowHistory(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}>
                <X size={16} />
              </button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-sm)', display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
              {versions.map(ver => (
                <div
                  key={ver.id}
                  style={{
                    padding: 'var(--space-sm)',
                    backgroundColor: 'var(--color-bg-surface-sunken)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--color-border-subtle)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                    <strong style={{ fontSize: '12px', color: 'var(--color-ink-700)' }}>{ver.versionNumber}</strong>
                    <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>{ver.timestamp}</span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                    {ver.author}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-primary)', marginTop: '4px', lineHeight: 1.4 }}>
                    {ver.summary}
                  </div>

                  <div style={{ marginTop: 'var(--space-xs)', textAlign: 'right' }}>
                    <button
                      onClick={() => handleRestoreVersion(ver)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--color-text-link)',
                        fontSize: '11px',
                        cursor: 'pointer',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '3px'
                      }}
                    >
                      <RotateCcw size={11} />
                      Restore
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
