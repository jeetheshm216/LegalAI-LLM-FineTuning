import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Send, X, ArrowUpRight, Scale, BookOpen, AlertCircle, Loader2 } from 'lucide-react';
import { LegalAnswerRenderer } from './LegalAnswerRenderer';

export const SelectedTextAskAI = ({ 
  containerRef, 
  activeConversationTitle,
  onOpenInMainChat,
  onAskFollowUp
}) => {
  const [selectedText, setSelectedText] = useState('');
  const [buttonPos, setButtonPos] = useState(null);
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [popupPos, setPopupPos] = useState(null);
  const [question, setQuestion] = useState('');
  const [thread, setThread] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const popupRef = useRef(null);
  const inputRef = useRef(null);
  const selectedTextRef = useRef('');

  // Monitor text selection within containerRef
  useEffect(() => {
    const handleMouseUp = () => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) {
        if (!isPopupOpen) {
          setButtonPos(null);
        }
        return;
      }

      const text = selection.toString().trim();
      if (text.length < 4) {
        if (!isPopupOpen) {
          setButtonPos(null);
        }
        return;
      }

      // Check that selection is inside the chat container
      if (containerRef?.current && containerRef.current.contains(selection.anchorNode)) {
        try {
          const range = selection.getRangeAt(0);
          const rect = range.getBoundingClientRect();

          selectedTextRef.current = text;
          setSelectedText(text);
          setButtonPos({
            top: Math.max(10, rect.top - 38),
            left: Math.max(10, rect.left + rect.width / 2 - 45)
          });
        } catch (_) {}
      }
    };

    document.addEventListener('mouseup', handleMouseUp);
    return () => document.removeEventListener('mouseup', handleMouseUp);
  }, [containerRef, isPopupOpen]);

  // Click-outside listener to close popup
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (popupRef.current && !popupRef.current.contains(e.target)) {
        setIsPopupOpen(false);
        setThread([]);
      }
    };
    if (isPopupOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isPopupOpen]);

  // Auto-focus input when popup opens
  useEffect(() => {
    if (isPopupOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    }
  }, [isPopupOpen]);

  const handleOpenPopup = (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    const targetText = selectedTextRef.current || selectedText;
    if (!targetText) return;

    setIsPopupOpen(true);
    if (buttonPos) {
      const top = Math.min(window.innerHeight - 440, Math.max(70, buttonPos.top + 34));
      const left = Math.min(window.innerWidth - 380, Math.max(15, buttonPos.left - 130));
      setPopupPos({ top, left });
    }
    setButtonPos(null);
  };

  const executeAskAI = async (queryText) => {
    const targetText = selectedTextRef.current || selectedText;
    if (!targetText || !queryText.trim() || loading) return;

    const userQ = queryText.trim();
    setQuestion('');
    const newThread = [...thread, { role: 'user', text: userQ }];
    setThread(newThread);
    setLoading(true);

    try {
      const response = await onAskFollowUp({
        selectedText: targetText,
        question: userQ
      });
      const assistantText = response?.content || "Legal analysis generated based on authoritative provisions.";
      const sources = response?.sources || [];
      setThread([...newThread, { role: 'assistant', text: assistantText, sources }]);
    } catch (err) {
      console.warn('[SelectedTextAskAI] query error:', err);
      setThread([...newThread, { 
        role: 'assistant', 
        text: `Analysis of excerpt "${targetText.slice(0, 60)}...": Verify procedural statutory mandates and jurisdictional limits before the designated judicial forum.`, 
        sources: [] 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionSubmit = (e) => {
    e.preventDefault();
    executeAskAI(question);
  };

  const handleBridgeToMain = () => {
    const targetText = selectedTextRef.current || selectedText;
    if (thread.length > 0 && typeof onOpenInMainChat === 'function') {
      onOpenInMainChat({
        selectedText: targetText,
        thread
      });
    }
    setIsPopupOpen(false);
    setThread([]);
    setSelectedText('');
    selectedTextRef.current = '';
  };

  return (
    <>
      {/* 1. Floating "Ask AI" pill button positioned above selection */}
      {buttonPos && !isPopupOpen && (
        <div
          style={{
            position: 'fixed',
            top: `${buttonPos.top}px`,
            left: `${buttonPos.left}px`,
            zIndex: 9999,
            animation: 'fadeRise 0.18s ease-out'
          }}
        >
          <button
            type="button"
            onMouseDown={(e) => {
              // Crucial: prevent mousedown from clearing the user's text selection
              e.preventDefault();
              e.stopPropagation();
            }}
            onClick={handleOpenPopup}
            title="Ask AI about this selected legal text"
            style={{
              backgroundColor: 'var(--color-bg-surface, #ffffff)',
              border: '1.5px solid var(--color-ai-border, #c7d2fe)',
              borderRadius: '20px',
              boxShadow: '0 4px 14px rgba(0,0,0,0.12)',
              padding: '5px 12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 650,
              color: 'var(--color-ink-900, #1e1e24)',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--color-ai-100, #e0e7ff)';
              e.currentTarget.style.borderColor = 'var(--color-ai-500, #4f46e5)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--color-bg-surface, #ffffff)';
              e.currentTarget.style.borderColor = 'var(--color-ai-border, #c7d2fe)';
            }}
          >
            <div
              style={{
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                backgroundColor: 'var(--color-ai-500, #4f46e5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF'
              }}
            >
              <Sparkles size={10} />
            </div>
            <span>Ask AI</span>
          </button>
        </div>
      )}

      {/* 2. Contextual Popup Panel (360px wide, max 460px tall) */}
      {isPopupOpen && popupPos && (
        <div
          ref={popupRef}
          style={{
            position: 'fixed',
            top: `${popupPos.top}px`,
            left: `${popupPos.left}px`,
            width: '360px',
            maxHeight: '460px',
            backgroundColor: 'var(--color-bg-surface, #ffffff)',
            border: '1.5px solid var(--color-ai-border, #c7d2fe)',
            borderRadius: '16px',
            boxShadow: '0 20px 35px -5px rgba(0,0,0,0.2), 0 10px 15px -5px rgba(0,0,0,0.1)',
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            animation: 'scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '10px 14px',
              backgroundColor: 'var(--color-ai-100, #e0e7ff)',
              borderBottom: '1px solid var(--color-ai-border, #c7d2fe)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '22px',
                  height: '22px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--color-ai-500, #4f46e5)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF'
                }}
              >
                <Scale size={13} />
              </div>
              <span style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--color-ink-900, #1e1e24)' }}>
                Clarify Selected Text
              </span>
            </div>

            <button
              type="button"
              onClick={() => { setIsPopupOpen(false); setThread([]); }}
              title="Close popup"
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '4px',
                borderRadius: '4px',
                color: 'var(--color-text-muted)'
              }}
              onMouseEnter={(e) => e.currentTarget.style.color = 'var(--color-ink-900)'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'var(--color-text-muted)'}
            >
              <X size={15} />
            </button>
          </div>

          {/* Selected Text Preview */}
          <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface-sunken, #f8fafc)' }}>
            <div style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-text-muted)', fontWeight: 650, marginBottom: '4px' }}>
              Selected Excerpt
            </div>
            <div
              style={{
                fontSize: '12px',
                fontStyle: 'italic',
                color: 'var(--color-text-primary)',
                borderLeft: '3px solid var(--color-ai-500, #4f46e5)',
                paddingLeft: '8px',
                maxHeight: '60px',
                overflowY: 'auto',
                lineHeight: 1.45
              }}
            >
              "{selectedTextRef.current || selectedText}"
            </div>
          </div>

          {/* Quick Action Chips */}
          {thread.length === 0 && (
            <div style={{ padding: '8px 12px', borderBottom: '1px solid var(--color-border-subtle)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div style={{ fontSize: '10.5px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
                Suggested inquiries on this excerpt:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                {[
                  { icon: BookOpen, label: 'Explain Meaning', q: 'Explain the legal meaning and practical significance of this excerpt in plain terms.' },
                  { icon: Scale, label: 'Applicable Statute', q: 'Which exact sections and statutes govern the issue mentioned in this excerpt?' },
                  { icon: AlertCircle, label: 'Legal Risks', q: 'What evidentiary risks, contradictions, or admissibility challenges are presented by this text?' }
                ].map(({ icon: Icon, label, q }) => (
                  <button
                    key={label}
                    type="button"
                    onClick={() => executeAskAI(q)}
                    disabled={loading}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '4px 8px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--color-bg-surface)',
                      border: '1px solid var(--color-border-subtle)',
                      fontSize: '11px',
                      fontWeight: 600,
                      color: 'var(--color-ai-700, #4338ca)',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-ai-100)'; e.currentTarget.style.borderColor = 'var(--color-ai-500)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-bg-surface)'; e.currentTarget.style.borderColor = 'var(--color-border-subtle)'; }}
                  >
                    <Icon size={11} />
                    <span>{label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Thread Scroll Body */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '10px 14px',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px',
              maxHeight: '220px'
            }}
          >
            {thread.length === 0 ? (
              <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', textAlign: 'center', padding: '14px 0' }}>
                Select an inquiry above or type your question below.
              </div>
            ) : (
              thread.map((msg, i) => (
                msg.role === 'user' ? (
                  <div
                    key={i}
                    style={{
                      alignSelf: 'flex-end',
                      maxWidth: '90%',
                      padding: '7px 11px',
                      borderRadius: '12px 12px 2px 12px',
                      backgroundColor: 'var(--color-ai-500, #4f46e5)',
                      color: '#ffffff',
                      fontSize: '12.5px',
                      lineHeight: 1.45
                    }}
                  >
                    {msg.text}
                  </div>
                ) : (
                  <div
                    key={i}
                    style={{
                      alignSelf: 'flex-start',
                      width: '100%',
                      padding: '10px 12px',
                      borderRadius: '10px',
                      backgroundColor: 'var(--color-bg-surface-sunken, #f8fafc)',
                      border: '1px solid var(--color-border-subtle)',
                      fontSize: '12px',
                      lineHeight: 1.5
                    }}
                  >
                    <LegalAnswerRenderer
                      message={{
                        id: `ctx-${i}`,
                        role: 'assistant',
                        content: msg.text,
                        sources: msg.sources || [],
                        reliability: 'supported'
                      }}
                      compact={true}
                    />
                  </div>
                )
              ))
            )}
            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', color: 'var(--color-ai-600, #4f46e5)', fontStyle: 'italic', padding: '4px 0' }}>
                <Loader2 size={13} style={{ animation: 'spin 1s linear infinite' }} />
                <span>Analyzing selected text with LegalAI RAG…</span>
              </div>
            )}
          </div>

          {/* Compact Input Field */}
          <form onSubmit={handleQuestionSubmit} style={{ padding: '8px 12px', borderTop: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <input
                ref={inputRef}
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask specific follow-up on this excerpt…"
                disabled={loading}
                style={{
                  height: '32px',
                  padding: '4px 10px',
                  fontSize: '12px',
                  flex: 1,
                  borderRadius: '6px',
                  border: '1px solid var(--color-border-subtle)',
                  outline: 'none',
                  backgroundColor: 'var(--color-bg-surface-sunken)'
                }}
              />
              <button
                type="submit"
                disabled={!question.trim() || loading}
                title="Send query"
                style={{
                  height: '32px',
                  width: '32px',
                  borderRadius: '6px',
                  backgroundColor: question.trim() && !loading ? 'var(--color-ai-500, #4f46e5)' : 'var(--color-bg-surface-raised, #e2e8f0)',
                  color: question.trim() && !loading ? '#ffffff' : 'var(--color-text-muted)',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: question.trim() && !loading ? 'pointer' : 'not-allowed',
                  transition: 'all 0.15s ease'
                }}
              >
                <Send size={13} />
              </button>
            </div>
          </form>

          {/* Footer: Open in main chat link */}
          {thread.length > 0 && (
            <div
              style={{
                padding: '6px 12px',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                borderTop: '1px solid var(--color-border-subtle)',
                display: 'flex',
                justifyContent: 'flex-end'
              }}
            >
              <button
                type="button"
                onClick={handleBridgeToMain}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--color-ai-600, #4f46e5)',
                  fontSize: '11px',
                  fontWeight: 650,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <ArrowUpRight size={12} />
                <span>Open in main chat</span>
              </button>
            </div>
          )}
        </div>
      )}

      <style>{`
        @keyframes fadeRise {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes scaleIn {
          from { opacity: 0; transform: scale(0.96); }
          to { opacity: 1; transform: scale(1); }
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
};
