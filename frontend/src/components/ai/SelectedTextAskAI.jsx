import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Send, X, ArrowUpRight } from 'lucide-react';
import { Button } from '../common/Button';

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

  // Monitor text selection within AI bubbles inside containerRef
  useEffect(() => {
    const handleMouseUp = () => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) {
        if (!isPopupOpen) {
          setButtonPos(null);
          setSelectedText('');
        }
        return;
      }

      const text = selection.toString().trim();
      if (text.length < 5) {
        setButtonPos(null);
        return;
      }

      // Verify that selection is inside the AI chat container
      if (containerRef.current && containerRef.current.contains(selection.anchorNode)) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        setSelectedText(text);
        setButtonPos({
          top: Math.max(10, rect.top - 36),
          left: Math.max(10, rect.left + rect.width / 2 - 45)
        });
      }
    };

    document.addEventListener('mouseup', handleMouseUp);
    return () => document.removeEventListener('mouseup', handleMouseUp);
  }, [containerRef, isPopupOpen]);

  const handleOpenPopup = () => {
    if (!buttonPos) return;
    setIsPopupOpen(true);
    setPopupPos({
      top: Math.min(window.innerHeight - 420, Math.max(70, buttonPos.top + 34)),
      left: Math.min(window.innerWidth - 340, Math.max(10, buttonPos.left - 120))
    });
    setButtonPos(null);
  };

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userQ = question.trim();
    setQuestion('');
    const newThread = [...thread, { role: 'user', text: userQ }];
    setThread(newThread);
    setLoading(true);

    try {
      const response = await onAskFollowUp({ selectedText, question: userQ });
      setThread([...newThread, { role: 'assistant', text: response.content }]);
    } catch (err) {
      setThread([...newThread, { role: 'assistant', text: "Verification note: Unable to retrieve supplementary citations." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleBridgeToMain = () => {
    if (thread.length > 0) {
      onOpenInMainChat({
        selectedText,
        thread
      });
    }
    setIsPopupOpen(false);
    setThread([]);
    setSelectedText('');
  };

  return (
    <>
      {/* 1. Floating "Ask AI" pill button (§15.7) positioned 8px above selection midpoint */}
      {buttonPos && !isPopupOpen && (
        <div
          style={{
            position: 'fixed',
            top: `${buttonPos.top}px`,
            left: `${buttonPos.left}px`,
            zIndex: 'var(--z-selected-text-popup)',
            animation: 'fadeRise var(--duration-fast) var(--easing-decelerate)'
          }}
        >
          <button
            onClick={handleOpenPopup}
            style={{
              backgroundColor: 'var(--color-bg-surface)',
              border: '1px solid var(--color-ai-border)',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--elevation-2)',
              padding: '4px 10px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer',
              fontSize: 'var(--text-caption)',
              fontWeight: 500,
              color: 'var(--color-ink-700)'
            }}
          >
            <div
              style={{
                width: '14px',
                height: '14px',
                borderRadius: '50%',
                backgroundColor: 'var(--color-ai-500)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF'
              }}
            >
              <Sparkles size={9} />
            </div>
            <span>Ask AI</span>
          </button>
        </div>
      )}

      {/* 2. Contextual Popup Panel (§15.7: 320px wide, max 400px tall) */}
      {isPopupOpen && popupPos && (
        <div
          ref={popupRef}
          style={{
            position: 'fixed',
            top: `${popupPos.top}px`,
            left: `${popupPos.left}px`,
            width: '320px',
            maxHeight: '400px',
            backgroundColor: 'var(--color-bg-surface-raised)',
            border: '1px solid var(--color-ai-border)',
            borderRadius: 'var(--radius-xl)',
            boxShadow: 'var(--elevation-3)',
            zIndex: 'var(--z-selected-text-popup)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            animation: 'scaleIn var(--duration-fast) var(--easing-decelerate)'
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '8px 12px',
              backgroundColor: 'var(--color-ai-100)',
              borderBottom: '1px solid var(--color-ai-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div
                style={{
                  width: '18px',
                  height: '18px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-ai-500)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF'
                }}
              >
                <Sparkles size={10} />
              </div>
              <span style={{ fontSize: 'var(--text-caption)', fontWeight: 600, color: 'var(--color-ink-700)' }}>
                Contextual Follow-up
              </span>
            </div>

            <button
              onClick={() => { setIsPopupOpen(false); setThread([]); }}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '2px',
                color: 'var(--color-text-muted)'
              }}
            >
              <X size={14} />
            </button>
          </div>

          {/* Selected Text Preview + Context Indicator (§15.7) */}
          <div style={{ padding: '8px 12px', borderBottom: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface)' }}>
            <div
              style={{
                fontSize: '11px',
                fontStyle: 'italic',
                color: 'var(--color-text-secondary)',
                borderLeft: '2px solid var(--color-ai-border)',
                paddingLeft: '6px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                lineHeight: 1.4
              }}
            >
              "{selectedText}"
            </div>
            <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
              Continuing from {activeConversationTitle || "Case Conversation"}
            </div>
          </div>

          {/* Thread Scroll Body */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '8px 12px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
              maxHeight: '190px'
            }}
          >
            {thread.length === 0 ? (
              <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)', textAlign: 'center', padding: '16px 0' }}>
                Ask a specific clarifying question on this selected text.
              </div>
            ) : (
              thread.map((msg, i) => (
                <div
                  key={i}
                  style={{
                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '88%',
                    padding: '6px 8px',
                    borderRadius: msg.role === 'user' ? '8px 8px 2px 8px' : '8px 8px 8px 2px',
                    backgroundColor: msg.role === 'user' ? 'var(--color-bg-surface-sunken)' : 'var(--color-ai-100)',
                    border: msg.role === 'user' ? '1px solid var(--color-border-subtle)' : '1px solid var(--color-ai-border)',
                    fontSize: '12px',
                    lineHeight: 1.4,
                    color: 'var(--color-text-primary)'
                  }}
                >
                  {msg.text}
                </div>
              ))
            )}
            {loading && (
              <div style={{ fontSize: '11px', color: 'var(--color-ai-500)', fontStyle: 'italic' }}>
                Analyzing selected context…
              </div>
            )}
          </div>

          {/* Compact Input Field (28px height per §15.7) */}
          <form onSubmit={handleQuestionSubmit} style={{ padding: '6px 10px', borderTop: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask follow-up…"
                className="input-base"
                style={{
                  height: '28px',
                  padding: '2px 8px',
                  fontSize: '12px',
                  flex: 1
                }}
              />
              <button
                type="submit"
                disabled={!question.trim() || loading}
                style={{
                  height: '26px',
                  width: '26px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--color-ink-700)',
                  color: 'var(--color-text-on-ink)',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: !question.trim() ? 'not-allowed' : 'pointer',
                  opacity: !question.trim() ? 0.4 : 1
                }}
              >
                <Send size={11} />
              </button>
            </div>
          </form>

          {/* Footer: Open in main chat link (§15.7) */}
          <div
            style={{
              padding: '4px 10px',
              backgroundColor: 'var(--color-bg-surface-sunken)',
              borderTop: '1px solid var(--color-border-subtle)',
              display: 'flex',
              justifyContent: 'flex-end'
            }}
          >
            <button
              onClick={handleBridgeToMain}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--color-text-link)',
                fontSize: '11px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '3px'
              }}
            >
              <ArrowUpRight size={11} />
              <span>Open in main chat</span>
            </button>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeRise {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes scaleIn {
          from { opacity: 0; transform: scale(0.98); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </>
  );
};
