import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Square, 
  Copy, 
  RotateCw, 
  ThumbsUp, 
  ThumbsDown, 
  Sparkles, 
  ChevronDown, 
  ChevronUp, 
  FileText, 
  Plus, 
  Search, 
  Check, 
  BookOpen, 
  CheckSquare, 
  Square as SquareOutline,
  Sliders,
  ExternalLink,
  Layers
} from 'lucide-react';
import { Button } from '../common/Button';
import { ReliabilityBadge } from '../common/Badge';
import { SelectedTextAskAI } from './SelectedTextAskAI';
import { INITIAL_CONVERSATIONS } from '../../mock/mockAI';
import { INITIAL_CASES } from '../../mock/mockCases';
import { aiService } from '../../services/aiService';

export const AIAssistantView = ({ 
  initialMode = 'GENERAL', 
  lockedCase = null, 
  allCases = INITIAL_CASES 
}) => {
  const [conversations, setConversations] = useState(INITIAL_CONVERSATIONS);
  const [activeConvId, setActiveConvId] = useState(() => {
    if (lockedCase) {
      const found = INITIAL_CONVERSATIONS.find(c => c.caseId === lockedCase.id);
      return found ? found.id : INITIAL_CONVERSATIONS[0].id;
    }
    return INITIAL_CONVERSATIONS[0].id;
  });

  const [inputQuery, setInputQuery] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [expandedSources, setExpandedSources] = useState({});
  const [showPersonalization, setShowPersonalization] = useState(false);
  const [showCaseDropdown, setShowCaseDropdown] = useState(false);
  const [historySearch, setHistorySearch] = useState('');

  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const stopGenerationRef = useRef(null);

  const activeConv = conversations.find(c => c.id === activeConvId) || conversations[0];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeConv.messages, streamingText]);

  // Context mode selection helper
  const handleModeChange = (newMode) => {
    setConversations(prev => prev.map(c => {
      if (c.id === activeConvId) {
        return {
          ...c,
          mode: newMode,
          caseId: newMode === 'SINGLE_CASE' ? (c.caseId || allCases[0].id) : null,
          caseNumber: newMode === 'SINGLE_CASE' ? (c.caseNumber || allCases[0].caseNumber) : null,
          selectedCases: newMode === 'MULTI_CASE' ? [allCases[0].id, allCases[1].id] : []
        };
      }
      return c;
    }));
  };

  // Case Switcher (§11: prominent selector, does not destroy conversation)
  const handleSwitchCase = (caseItem) => {
    setConversations(prev => prev.map(c => {
      if (c.id === activeConvId) {
        return {
          ...c,
          caseId: caseItem.id,
          caseNumber: caseItem.caseNumber,
          mode: 'SINGLE_CASE'
        };
      }
      return c;
    }));
    setShowCaseDropdown(false);
  };

  // Multi-case checkbox toggle
  const handleToggleMultiCase = (caseId) => {
    const currentList = activeConv.selectedCases || [];
    const updated = currentList.includes(caseId)
      ? currentList.filter(id => id !== caseId)
      : [...currentList, caseId];

    setConversations(prev => prev.map(c => {
      if (c.id === activeConvId) {
        return { ...c, selectedCases: updated };
      }
      return c;
    }));
  };

  // Personalization settings toggle (§15.6)
  const handleToggleContextSetting = (key) => {
    setConversations(prev => prev.map(c => {
      if (c.id === activeConvId) {
        const currentSettings = c.contextSettings || {};
        return {
          ...c,
          contextSettings: {
            ...currentSettings,
            [key]: !currentSettings[key]
          }
        };
      }
      return c;
    }));
  };

  // Toggle supporting case
  const handleToggleSupportingCase = (cId) => {
    setConversations(prev => prev.map(c => {
      if (c.id === activeConvId) {
        const curSupp = c.contextSettings?.supportingCases || [];
        const updated = curSupp.includes(cId)
          ? curSupp.filter(id => id !== cId)
          : [...curSupp, cId];

        return {
          ...c,
          contextSettings: {
            ...c.contextSettings,
            supportingCases: updated
          }
        };
      }
      return c;
    }));
  };

  // Send message flow
  const handleSendMessage = (e) => {
    e?.preventDefault();
    if (!inputQuery.trim() || isGenerating) return;

    const userText = inputQuery.trim();
    setInputQuery('');

    const userMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      content: userText
    };

    // Add user message to conversation
    setConversations(prev => prev.map(c => {
      if (c.id === activeConvId) {
        return {
          ...c,
          messages: [...c.messages, userMessage]
        };
      }
      return c;
    }));

    setIsGenerating(true);
    setStreamingText('');

    // Launch streaming token simulation
    const stopFn = aiService.sendMessageStream({
      convId: activeConvId,
      content: userText,
      onToken: (tokenString) => {
        setStreamingText(tokenString);
      },
      onComplete: (aiMessage) => {
        setStreamingText('');
        setIsGenerating(false);
        setConversations(prev => prev.map(c => {
          if (c.id === activeConvId) {
            return {
              ...c,
              messages: [...c.messages, aiMessage]
            };
          }
          return c;
        }));
      }
    });

    stopGenerationRef.current = stopFn;
  };

  const handleStopGeneration = () => {
    if (stopGenerationRef.current) {
      stopGenerationRef.current();
    }
    setIsGenerating(false);
    if (streamingText) {
      const interruptedMsg = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        content: streamingText + " [Generation halted by counsel]",
        reliability: 'limited',
        reliabilityLabel: 'Partial response (interrupted)',
        sources: []
      };
      setConversations(prev => prev.map(c => {
        if (c.id === activeConvId) {
          return { ...c, messages: [...c.messages, interruptedMsg] };
        }
        return c;
      }));
      setStreamingText('');
    }
  };

  // Create new conversation
  const handleNewConversation = () => {
    const newConv = {
      id: `conv-${Date.now()}`,
      title: "New Legal Inquiry",
      mode: "GENERAL",
      caseId: null,
      caseNumber: null,
      selectedCases: [],
      contextSettings: {
        includeDocuments: true,
        includeNotes: true,
        includeTimeline: true,
        includeHistory: true,
        supportingCases: []
      },
      updatedAt: "Just now",
      messages: []
    };
    setConversations([newConv, ...conversations]);
    setActiveConvId(newConv.id);
  };

  // Bridge from Selected-text popup to main chat (§15.7)
  const handleBridgeSelectedTextToMain = ({ selectedText, thread }) => {
    const threadFormatted = thread.map(t => `${t.role === 'user' ? 'Follow-up' : 'Analysis'}: ${t.text}`).join('\n\n');
    const newHumanMsg = {
      id: `msg-${Date.now()}-q`,
      role: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      content: `[Contextual query on: "${selectedText.slice(0, 100)}..."]\n\n${thread[0]?.text || ""}`
    };
    const newAIMsg = {
      id: `msg-${Date.now()}-a`,
      role: 'assistant',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      content: thread[1]?.text || "Contextual follow-up integrated into the legal brief transcript.",
      reliability: 'supported',
      reliabilityLabel: 'Supported by sources',
      sources: []
    };

    setConversations(prev => prev.map(c => {
      if (c.id === activeConvId) {
        return {
          ...c,
          messages: [...c.messages, newHumanMsg, newAIMsg]
        };
      }
      return c;
    }));
  };

  const filteredConversations = conversations.filter(c => 
    c.title.toLowerCase().includes(historySearch.toLowerCase())
  );

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '260px 1fr',
        height: 'calc(100vh - var(--header-height) - 40px)',
        minHeight: '620px',
        backgroundColor: 'var(--color-bg-surface)',
        border: '1px solid var(--color-border-subtle)',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden'
      }}
      className="ai-workspace-container"
    >
      {/* 1. Left Rail: Conversation History (§15.11) */}
      <div
        style={{
          backgroundColor: 'var(--color-bg-surface-sunken)',
          borderRight: '1px solid var(--color-border-subtle)',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Rail Top Action */}
        <div style={{ padding: 'var(--space-sm)', borderBottom: '1px solid var(--color-border-subtle)' }}>
          <Button
            variant="secondary"
            size="sm"
            fullWidth
            icon={Plus}
            onClick={handleNewConversation}
          >
            New Inquiry
          </Button>

          {/* Search history */}
          <div style={{ position: 'relative', marginTop: 'var(--space-xs)' }}>
            <Search size={13} color="var(--color-text-muted)" style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              value={historySearch}
              onChange={(e) => setHistorySearch(e.target.value)}
              placeholder="Search conversations…"
              className="input-base"
              style={{
                paddingLeft: '26px',
                paddingTop: '3px',
                paddingBottom: '3px',
                fontSize: '11px',
                backgroundColor: 'var(--color-bg-surface)'
              }}
            />
          </div>
        </div>

        {/* History List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-xs)' }}>
          <div style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)', padding: '6px 8px 4px 8px', fontWeight: 600 }}>
            Recent Legal Inquiries
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            {filteredConversations.map((conv) => {
              const isActive = conv.id === activeConvId;
              return (
                <button
                  key={conv.id}
                  onClick={() => setActiveConvId(conv.id)}
                  style={{
                    width: '100%',
                    background: isActive ? 'var(--color-bg-surface)' : 'transparent',
                    border: isActive ? '1px solid var(--color-border-subtle)' : '1px solid transparent',
                    borderRadius: 'var(--radius-md)',
                    padding: '8px 10px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '2px',
                    boxShadow: isActive ? 'var(--elevation-1)' : 'none'
                  }}
                >
                  <span
                    style={{
                      fontSize: '12px',
                      fontWeight: isActive ? 600 : 500,
                      color: isActive ? 'var(--color-ink-700)' : 'var(--color-text-primary)',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {conv.title}
                  </span>
                  
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '10px', color: 'var(--color-text-muted)' }}>
                    <span>{conv.mode.replace('_', ' ')}</span>
                    <span>{conv.updatedAt}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* 2. Main AI Panel */}
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
        
        {/* Context Header Strip (§15.2: persistent, --color-ai-100 bg, 1px --color-ai-border bottom edge) */}
        <div
          style={{
            backgroundColor: 'var(--color-ai-100)',
            borderBottom: '1px solid var(--color-ai-border)',
            padding: 'var(--space-xs) var(--space-md)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 'var(--space-xs)',
            zIndex: 10
          }}
        >
          {/* Left: Mode Title and Prominent Case Switcher (§11: "AI Assistant [ Case 01 v ]") */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
            <span style={{ fontSize: 'var(--text-caption)', fontWeight: 600, color: 'var(--color-ink-700)' }}>
              AI Context:
            </span>

            {/* Mode Selector Toggle Chips */}
            <div style={{ display: 'inline-flex', backgroundColor: 'var(--color-bg-surface)', padding: '2px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-ai-border)' }}>
              <button
                onClick={() => handleModeChange('GENERAL')}
                style={{
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  background: activeConv.mode === 'GENERAL' ? 'var(--color-ai-500)' : 'transparent',
                  color: activeConv.mode === 'GENERAL' ? '#FFFFFF' : 'var(--color-text-secondary)',
                  fontSize: '11px',
                  fontWeight: 500,
                  cursor: 'pointer'
                }}
              >
                General
              </button>
              <button
                onClick={() => handleModeChange('SINGLE_CASE')}
                style={{
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  background: activeConv.mode === 'SINGLE_CASE' ? 'var(--color-ai-500)' : 'transparent',
                  color: activeConv.mode === 'SINGLE_CASE' ? '#FFFFFF' : 'var(--color-text-secondary)',
                  fontSize: '11px',
                  fontWeight: 500,
                  cursor: 'pointer'
                }}
              >
                Single Matter
              </button>
              <button
                onClick={() => handleModeChange('MULTI_CASE')}
                style={{
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  background: activeConv.mode === 'MULTI_CASE' ? 'var(--color-ai-500)' : 'transparent',
                  color: activeConv.mode === 'MULTI_CASE' ? '#FFFFFF' : 'var(--color-text-secondary)',
                  fontSize: '11px',
                  fontWeight: 500,
                  cursor: 'pointer'
                }}
              >
                Multi-Matter
              </button>
            </div>

            {/* Prominent Case Selector Dropdown (§11) when in Single Case mode */}
            {activeConv.mode === 'SINGLE_CASE' && (
              <div style={{ position: 'relative' }}>
                <button
                  onClick={() => setShowCaseDropdown(!showCaseDropdown)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-ai-border)',
                    backgroundColor: 'var(--color-bg-surface)',
                    fontSize: '12px',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--color-ink-700)',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  <span>{activeConv.caseNumber || allCases[0].caseNumber}</span>
                  <ChevronDown size={13} />
                </button>

                {showCaseDropdown && (
                  <div
                    style={{
                      position: 'absolute',
                      top: 'calc(100% + 4px)',
                      left: 0,
                      width: '260px',
                      backgroundColor: 'var(--color-bg-surface)',
                      border: '1px solid var(--color-border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      boxShadow: 'var(--elevation-2)',
                      zIndex: 'var(--z-dropdown)',
                      padding: '4px'
                    }}
                  >
                    {allCases.map((c) => (
                      <button
                        key={c.id}
                        onClick={() => handleSwitchCase(c)}
                        style={{
                          width: '100%',
                          textAlign: 'left',
                          padding: '6px 8px',
                          background: (activeConv.caseId === c.id) ? 'var(--color-accent-100)' : 'transparent',
                          border: 'none',
                          borderRadius: 'var(--radius-sm)',
                          cursor: 'pointer',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '2px'
                        }}
                      >
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: 600, color: 'var(--color-ink-700)' }}>
                          {c.caseNumber}
                        </span>
                        <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {c.title}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right: Personalization / Context Control Trigger */}
          <button
            onClick={() => setShowPersonalization(!showPersonalization)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-text-link)',
              fontSize: '12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontWeight: 500
            }}
          >
            <Sliders size={13} />
            <span>Context Controls</span>
            {showPersonalization ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>
        </div>

        {/* Collapsible Personalization / Context Drawer (§15.6) */}
        {showPersonalization && (
          <div
            style={{
              backgroundColor: 'var(--color-bg-surface-sunken)',
              borderBottom: '1px solid var(--color-border-subtle)',
              padding: 'var(--space-sm) var(--space-md)',
              fontSize: '12px',
              animation: 'fadeIn 0.15s ease-out'
            }}
          >
            {activeConv.mode === 'SINGLE_CASE' ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span style={{ width: '8px', height: '8px', backgroundColor: 'var(--color-ink-700)', display: 'inline-block' }} />
                  <strong>Current Matter: {activeConv.caseNumber || "Case 01"}</strong>
                  <span style={{ color: 'var(--color-text-muted)', fontSize: '11px' }}>(Locked, primary scope)</span>
                </div>

                <div style={{ marginBottom: '8px' }}>
                  <span style={{ color: 'var(--color-text-secondary)', marginRight: '12px' }}>Include facets:</span>
                  <label style={{ marginRight: '12px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={activeConv.contextSettings?.includeDocuments ?? true}
                      onChange={() => handleToggleContextSetting('includeDocuments')}
                      style={{ accentColor: 'var(--color-accent-500)', marginRight: '4px' }}
                    />
                    Documents
                  </label>
                  <label style={{ marginRight: '12px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={activeConv.contextSettings?.includeTimeline ?? true}
                      onChange={() => handleToggleContextSetting('includeTimeline')}
                      style={{ accentColor: 'var(--color-accent-500)', marginRight: '4px' }}
                    />
                    Timeline
                  </label>
                  <label style={{ marginRight: '12px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={activeConv.contextSettings?.includeNotes ?? true}
                      onChange={() => handleToggleContextSetting('includeNotes')}
                      style={{ accentColor: 'var(--color-accent-500)', marginRight: '4px' }}
                    />
                    Advocate Notes
                  </label>
                </div>

                {/* Supporting Cases (additive context §15.6) */}
                <div>
                  <span style={{ color: 'var(--color-text-secondary)', marginRight: '8px' }}>Supporting matters:</span>
                  {allCases.filter(c => c.id !== activeConv.caseId).map(sc => {
                    const isChecked = activeConv.contextSettings?.supportingCases?.includes(sc.id);
                    return (
                      <label key={sc.id} style={{ marginRight: '10px', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => handleToggleSupportingCase(sc.id)}
                          style={{ accentColor: 'var(--color-accent-500)', marginRight: '3px' }}
                        />
                        {sc.caseNumber}
                      </label>
                    );
                  })}
                </div>
              </div>
            ) : activeConv.mode === 'MULTI_CASE' ? (
              <div>
                <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '6px' }}>
                  Select Matters for Cross-Synthesis:
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {allCases.map(c => {
                    const isSelected = activeConv.selectedCases?.includes(c.id);
                    return (
                      <button
                        key={c.id}
                        onClick={() => handleToggleMultiCase(c.id)}
                        style={{
                          padding: '4px 8px',
                          borderRadius: 'var(--radius-sm)',
                          border: isSelected ? '1px solid var(--color-accent-500)' : '1px solid var(--color-border-default)',
                          backgroundColor: isSelected ? 'var(--color-accent-100)' : 'var(--color-bg-surface)',
                          color: isSelected ? 'var(--color-accent-700)' : 'var(--color-text-primary)',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          fontSize: '11px'
                        }}
                      >
                        {isSelected ? <CheckSquare size={13} /> : <SquareOutline size={13} />}
                        <span style={{ fontFamily: 'var(--font-mono)' }}>{c.caseNumber}</span>
                        <span>{c.client}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div style={{ color: 'var(--color-text-secondary)' }}>
                <strong>General Legal AI Mode:</strong> No case context is automatically selected. Queries reference standard statutory corpuses and published case law.
              </div>
            )}
          </div>
        )}

        {/* Message Stream Area */}
        <div
          ref={chatContainerRef}
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: 'var(--space-lg)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-md)'
          }}
        >
          {activeConv.messages.length === 0 && (
            <div style={{ margin: 'auto', textAlign: 'center', maxWidth: '420px', color: 'var(--color-text-secondary)' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-ai-500)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF',
                  margin: '0 auto var(--space-sm) auto'
                }}
              >
                <Sparkles size={18} />
              </div>
              <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', color: 'var(--color-text-primary)', marginBottom: '4px' }}>
                Legal AI Consultation Ready
              </h3>
              <p style={{ fontSize: 'var(--text-caption)', lineHeight: 1.5 }}>
                Submit queries regarding statutory interpretations (BNS/BNSS/BSA), contractual liabilities, or evidentiary rules.
              </p>
            </div>
          )}

          {activeConv.messages.map((msg) => {
            const isLawyer = msg.role === 'user';

            return (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignSelf: isLawyer ? 'flex-end' : 'flex-start',
                  maxWidth: isLawyer ? '75%' : '85%'
                }}
              >
                {/* Bubble Container */}
                <div
                  style={{
                    backgroundColor: isLawyer ? 'var(--color-bg-surface-sunken)' : 'var(--color-ai-100)',
                    border: isLawyer ? '1px solid var(--color-border-subtle)' : '1px solid var(--color-ai-border)',
                    borderRadius: isLawyer ? 'var(--radius-chat-bubble-lawyer)' : 'var(--radius-chat-bubble-ai)',
                    padding: 'var(--space-md)',
                    boxShadow: 'var(--elevation-0)',
                    position: 'relative'
                  }}
                >
                  {/* AI Message Avatar Badge (§3.5: 3 strokes) */}
                  {!isLawyer && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <div
                        style={{
                          width: '22px',
                          height: '22px',
                          borderRadius: '50%',
                          backgroundColor: 'var(--color-ai-500)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#FFFFFF',
                          flexShrink: 0
                        }}
                      >
                        <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                          <path d="M3 5H13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                          <path d="M3 8H10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                          <path d="M3 11H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                        </svg>
                      </div>
                      <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-ai-500)', letterSpacing: '0.02em' }}>
                        Legal AI Synthesizer
                      </span>
                    </div>
                  )}

                  {/* Message Body Content (§4.3: --text-body-lg for AI, line length capped) */}
                  <div
                    style={{
                      fontFamily: 'var(--font-sans)',
                      fontSize: isLawyer ? 'var(--text-body)' : 'var(--text-body-lg)',
                      color: 'var(--color-text-primary)',
                      lineHeight: 1.6,
                      whiteSpace: 'pre-line'
                    }}
                  >
                    {msg.content}
                  </div>

                  {/* Sources Used Strip (§15.8) */}
                  {!isLawyer && msg.sources && msg.sources.length > 0 && (
                    <div style={{ marginTop: 'var(--space-md)', paddingTop: 'var(--space-xs)', borderTop: '1px solid var(--color-ai-border)' }}>
                      <button
                        onClick={() => setExpandedSources(prev => ({ ...prev, [msg.id]: !prev[msg.id] }))}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: 'var(--color-text-link)',
                          fontSize: 'var(--text-caption)',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontWeight: 500,
                          padding: 0
                        }}
                      >
                        <span>{msg.sources.length} sources used</span>
                        {expandedSources[msg.id] ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                      </button>

                      {/* Expandable Citation Cards Stack */}
                      {expandedSources[msg.id] && (
                        <div style={{ marginTop: 'var(--space-xs)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {msg.sources.map((src) => (
                            <div
                              key={src.id}
                              style={{
                                padding: '8px 10px',
                                backgroundColor: 'var(--color-bg-surface)',
                                borderRadius: 'var(--radius-sm)',
                                borderLeft: '3px solid var(--color-success-text)', // colored by confidence (§15.8)
                                borderTop: '1px solid var(--color-border-subtle)',
                                borderRight: '1px solid var(--color-border-subtle)',
                                borderBottom: '1px solid var(--color-border-subtle)',
                                fontSize: 'var(--text-caption)'
                              }}
                            >
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
                                  {src.title}
                                </div>
                                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                                  {src.reference}
                                </span>
                              </div>
                              <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontStyle: 'italic', marginTop: '2px' }}>
                                "{src.excerpt}"
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* AI Reliability Indicator Line (§15.9) */}
                      <div style={{ marginTop: 'var(--space-xs)' }}>
                        <ReliabilityBadge
                          reliability={msg.reliability || 'supported'}
                          label={msg.reliabilityLabel}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Message Actions Row (visible on hover or static, low emphasis per §15.4) */}
                {!isLawyer && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', marginTop: '4px', paddingLeft: '4px' }}>
                    <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                      {msg.timestamp}
                    </span>
                    <button
                      onClick={() => navigator.clipboard.writeText(msg.content)}
                      title="Copy response"
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: '2px' }}
                    >
                      <Copy size={13} />
                    </button>
                    <button
                      onClick={() => alert("Simulating re-synthesis with alternate legal precedents…")}
                      title="Regenerate"
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: '2px' }}
                    >
                      <RotateCw size={13} />
                    </button>
                    <button
                      title="Helpful citation"
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: '2px' }}
                    >
                      <ThumbsUp size={13} />
                    </button>
                  </div>
                )}
              </div>
            );
          })}

          {/* Active Streaming Token Render with Blinking Cursor Block (§15.4) */}
          {isGenerating && streamingText && (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignSelf: 'flex-start',
                maxWidth: '85%'
              }}
            >
              <div
                style={{
                  backgroundColor: 'var(--color-ai-100)',
                  border: '1px solid var(--color-ai-border)',
                  borderRadius: 'var(--radius-chat-bubble-ai)',
                  padding: 'var(--space-md)',
                  fontFamily: 'var(--font-sans)',
                  fontSize: 'var(--text-body-lg)',
                  color: 'var(--color-text-primary)',
                  lineHeight: 1.6,
                  whiteSpace: 'pre-line'
                }}
              >
                {streamingText}
                {/* 2px x 16px blinking block cursor per §15.4 */}
                <span
                  style={{
                    display: 'inline-block',
                    width: '2px',
                    height: '16px',
                    backgroundColor: 'var(--color-ai-500)',
                    verticalAlign: 'text-bottom',
                    marginLeft: '2px',
                    animation: 'blink 1s step-end infinite'
                  }}
                />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Selected-Text Contextual Ask AI Floating Popup Hook (§15.7) */}
        <SelectedTextAskAI
          containerRef={chatContainerRef}
          activeConversationTitle={activeConv.title}
          onOpenInMainChat={handleBridgeSelectedTextToMain}
          onAskFollowUp={aiService.askContextualAI}
        />

        {/* 3. Input Area (§15.3: auto-growing textarea, circular send / stop button) */}
        <form
          onSubmit={handleSendMessage}
          style={{
            padding: 'var(--space-md)',
            backgroundColor: 'var(--color-bg-surface)',
            borderTop: '1px solid var(--color-border-subtle)',
            display: 'flex',
            alignItems: 'flex-end',
            gap: 'var(--space-sm)'
          }}
        >
          <div style={{ flex: 1, position: 'relative' }}>
            <textarea
              rows={2}
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Ask about this matter, or research a legal statute… (Enter to send, Shift+Enter for newline)"
              className="input-base"
              style={{
                borderRadius: 'var(--radius-lg)',
                resize: 'none',
                maxHeight: '120px',
                fontSize: 'var(--text-body)'
              }}
            />
          </div>

          {/* Send / Stop Button per §15.3 (never both visible at once) */}
          {isGenerating ? (
            <button
              type="button"
              onClick={handleStopGeneration}
              title="Stop generation"
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                border: '1.5px solid var(--color-error-text)',
                backgroundColor: 'var(--color-bg-surface)',
                color: 'var(--color-error-text)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                flexShrink: 0
              }}
            >
              <Square size={13} />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!inputQuery.trim()}
              title="Send prompt"
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                border: 'none',
                backgroundColor: inputQuery.trim() ? 'var(--color-ink-700)' : 'var(--color-border-default)',
                color: 'var(--color-text-on-ink)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: inputQuery.trim() ? 'pointer' : 'not-allowed',
                flexShrink: 0,
                transition: 'background-color var(--duration-fast) var(--easing-standard)'
              }}
            >
              <Send size={15} />
            </button>
          )}
        </form>

      </div>

      <style>{`
        @keyframes blink {
          50% { opacity: 0; }
        }
        @media (max-width: 800px) {
          .ai-workspace-container {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};
