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
import { LegalAnswerRenderer } from './LegalAnswerRenderer';
import { INITIAL_CONVERSATIONS } from '../../mock/mockAI';
import { INITIAL_CASES } from '../../mock/mockCases';
import { aiService } from '../../services/aiService';

const createFreshConversation = (mode = 'GENERAL', lockedCase = null) => ({
  id: `conv-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
  title: lockedCase ? `Analysis — ${lockedCase.caseNumber}` : "New Legal Inquiry",
  mode: lockedCase ? 'SINGLE_CASE' : mode,
  caseId: lockedCase ? (lockedCase.caseNumber || lockedCase.id) : null,
  caseNumber: lockedCase ? lockedCase.caseNumber : null,
  selectedCases: lockedCase ? [lockedCase.caseNumber || lockedCase.id] : [],
  contextSettings: {
    includeDocuments: true,
    includeNotes: true,
    includeTimeline: true,
    includeHistory: true,
    supportingCases: []
  },
  updatedAt: "Just now",
  messages: []
});

export const AIAssistantView = ({ 
  initialMode = 'GENERAL', 
  lockedCase = null, 
  allCases = INITIAL_CASES 
}) => {
  const [conversations, setConversations] = useState(() => {
    const fresh = createFreshConversation(initialMode, lockedCase);
    return [fresh, ...INITIAL_CONVERSATIONS];
  });
  const [activeConvId, setActiveConvId] = useState(() => conversations[0]?.id || `conv-${Date.now()}`);

  // Dynamic context update if lockedCase changes
  useEffect(() => {
    if (lockedCase) {
      setConversations(prev => {
        const targetId = lockedCase.caseNumber || lockedCase.id;
        const existing = prev.find(c => c.caseId === targetId || c.caseNumber === lockedCase.caseNumber || c.caseId === lockedCase.id);
        if (existing) {
          setActiveConvId(existing.id);
          return prev;
        }
        const fresh = createFreshConversation('SINGLE_CASE', lockedCase);
        setActiveConvId(fresh.id);
        return [fresh, ...prev];
      });
    }
  }, [lockedCase?.id, lockedCase?.caseNumber]);

  const [inputQuery, setInputQuery] = useState('');
  const [generationState, setGenerationState] = useState('IDLE'); // 'IDLE' | 'GENERATING' | 'COMPLETED' | 'CANCELLED' | 'ERROR'
  const isGenerating = generationState === 'GENERATING';
  const [streamingText, setStreamingText] = useState('');
  const [thinkingStageIndex, setThinkingStageIndex] = useState(0);
  const [currentStages, setCurrentStages] = useState([
    "Thinking…",
    "Mulling this over…",
    "Analyzing the matter…"
  ]);
  const [expandedSources, setExpandedSources] = useState({});
  const [showPersonalization, setShowPersonalization] = useState(false);
  const [showCaseDropdown, setShowCaseDropdown] = useState(false);
  const [historySearch, setHistorySearch] = useState('');

  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const stopGenerationRef = useRef(null);

  const activeConv = conversations.find(c => c.id === activeConvId) || conversations[0];

  const scrollToBottom = (smooth = true) => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto'
      });
    }
  };

  useEffect(() => {
    scrollToBottom(false);
  }, [activeConv.messages, streamingText]);

  // Stage rotation timer for thinking indicator
  useEffect(() => {
    if (generationState !== 'GENERATING') {
      setThinkingStageIndex(0);
      return;
    }
    const timer = setInterval(() => {
      setThinkingStageIndex(prev => (prev < currentStages.length - 1 ? prev + 1 : prev));
    }, 2200);
    return () => clearInterval(timer);
  }, [generationState, currentStages]);

  const getThinkingStagesForQuery = (text, mode) => {
    const t = (text || '').toLowerCase();
    const isLegal = mode === 'GENERAL' && (
      /\b(bns|bnss|bsa|ipc|crpc|iea|section|act|statute|offence|punishment|bail|cognizable|bailable|high court|supreme court)\b/i.test(t)
    );
    const isCase = mode === 'SINGLE_CASE' || mode === 'MULTI_CASE' || /\b(my case|our case|client|evidence|charge sheet|hearing|witness)\b/i.test(t);

    if (isCase) {
      return [
        "Reviewing the case materials… 📁",
        "Checking the available evidence… ⚖️",
        "Preparing the case analysis…"
      ];
    }
    if (isLegal) {
      return [
        "Understanding your question…",
        "Reviewing relevant legal sources… ⚖️",
        "Preparing a grounded response…"
      ];
    }
    return [
      "Thinking…",
      "Analyzing the matter…"
    ];
  };

  // Context mode selection helper
  const handleModeChange = (newMode) => {
    setConversations(prev => prev.map(c => {
      if (c.id === activeConvId) {
        const defaultCase = (allCases && allCases.length > 0) ? allCases[0] : null;
        const defaultIdent = defaultCase ? (defaultCase.caseNumber || defaultCase.id) : null;
        return {
          ...c,
          mode: newMode,
          caseId: newMode === 'SINGLE_CASE' ? (c.caseId || defaultIdent) : null,
          caseNumber: newMode === 'SINGLE_CASE' ? (c.caseNumber || defaultCase?.caseNumber) : null,
          selectedCases: newMode === 'MULTI_CASE' ? (allCases.slice(0, 2).map(cs => cs.caseNumber || cs.id)) : (newMode === 'SINGLE_CASE' ? [c.caseId || defaultIdent] : [])
        };
      }
      return c;
    }));
  };

  // Case Switcher (§11: prominent selector, does not destroy conversation)
  const handleSwitchCase = (caseItem) => {
    const chosenIdent = caseItem.caseNumber || caseItem.id;
    setConversations(prev => prev.map(c => {
      if (c.id === activeConvId) {
        return {
          ...c,
          caseId: chosenIdent,
          caseNumber: caseItem.caseNumber,
          selectedCases: [chosenIdent],
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

    const targetConvId = activeConvId;
    const currentConv = conversations.find(c => c.id === targetConvId) || activeConv;
    const prevHistory = (currentConv.messages || []).map(m => ({
      role: m.role,
      content: m.content || '',
      query_type: m.query_type || null
    }));

    const userMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      content: userText
    };

    // Update conversation title if this is the first message
    const shouldUpdateTitle = (currentConv.messages.length === 0);
    const newTitle = shouldUpdateTitle 
      ? (userText.slice(0, 32) + (userText.length > 32 ? '…' : ''))
      : currentConv.title;

    // Add user message to conversation
    setConversations(prev => prev.map(c => {
      if (c.id === targetConvId) {
        return {
          ...c,
          title: newTitle,
          updatedAt: 'Just now',
          messages: [...c.messages, userMessage]
        };
      }
      return c;
    }));

    // Setup thinking stages
    const stages = getThinkingStagesForQuery(userText, currentConv.mode);
    setCurrentStages(stages);
    setThinkingStageIndex(0);

    setGenerationState('GENERATING');
    setStreamingText('');

    const effectiveMode = currentConv?.mode || (lockedCase ? 'SINGLE_CASE' : 'GENERAL');
    const effectiveCaseId = currentConv?.caseId || (lockedCase ? (lockedCase.caseNumber || lockedCase.id) : null);
    const effectiveCaseNumber = currentConv?.caseNumber || (lockedCase ? lockedCase.caseNumber : null);
    const effectiveSelectedCases = (currentConv?.selectedCases && currentConv.selectedCases.length > 0)
      ? currentConv.selectedCases
      : (effectiveCaseId ? [effectiveCaseId] : []);

    const stopFn = aiService.sendMessageStream({
      convId: targetConvId,
      content: userText,
      history: prevHistory,
      mode: effectiveMode,
      caseId: effectiveCaseId,
      caseNumber: effectiveCaseNumber,
      selectedCases: effectiveSelectedCases,
      contextSettings: currentConv?.contextSettings || null,
      onToken: (tokenString) => {
        setStreamingText(tokenString);
      },
      onComplete: (aiMessage) => {
        stopGenerationRef.current = null;
        setStreamingText('');
        setGenerationState('COMPLETED');
        setTimeout(() => setGenerationState('IDLE'), 50);

        setConversations(prev => prev.map(c => {
          if (c.id === targetConvId) {
            return {
              ...c,
              updatedAt: 'Just now',
              messages: [...c.messages, aiMessage]
            };
          }
          return c;
        }));
      },
      onError: (err) => {
        stopGenerationRef.current = null;
        setStreamingText('');
        setGenerationState('ERROR');
        setTimeout(() => setGenerationState('IDLE'), 50);

        const errorMsg = {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          content: `### Service Advisory\n\nUnable to complete inquiry: ${err?.message || 'Connection error'}.`,
          reliability: 'verify',
          reliabilityLabel: 'Service Advisory',
          sources: []
        };
        setConversations(prev => prev.map(c => {
          if (c.id === targetConvId) {
            return { ...c, messages: [...c.messages, errorMsg] };
          }
          return c;
        }));
      }
    });

    stopGenerationRef.current = stopFn;
  };

  const handleStopGeneration = () => {
    if (stopGenerationRef.current) {
      try {
        stopGenerationRef.current();
      } catch (err) {
        console.warn('Error during generation abort:', err);
      }
      stopGenerationRef.current = null;
    }
    setGenerationState('CANCELLED');
    setTimeout(() => setGenerationState('IDLE'), 50);

    if (streamingText) {
      const interruptedMsg = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        content: streamingText,
        reliability: 'limited',
        reliabilityLabel: 'Generation stopped by user',
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

  // Create new clean conversation
  const handleNewConversation = () => {
    if (stopGenerationRef.current) {
      try {
        stopGenerationRef.current();
      } catch (err) {}
      stopGenerationRef.current = null;
    }
    setGenerationState('IDLE');
    setStreamingText('');
    setInputQuery('');
    setThinkingStageIndex(0);

    const freshConv = createFreshConversation('GENERAL', null);
    setConversations(prev => [freshConv, ...prev]);
    setActiveConvId(freshConv.id);
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
        gridTemplateColumns: '260px minmax(0, 1fr)',
        gridTemplateRows: '100%',
        flex: 1,
        height: '100%',
        minHeight: 0,
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
          flexDirection: 'column',
          height: '100%',
          minHeight: 0,
          overflow: 'hidden'
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
        <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: 'var(--space-xs)' }}>
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
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          minHeight: 0,
          maxHeight: '100%',
          overflow: 'hidden',
          position: 'relative'
        }}
      >
        
        {/* Context Header Strip (§15.2: persistent, --color-ai-100 bg, 1px --color-ai-border bottom edge) */}
        <div
          style={{
            flexShrink: 0,
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
              flexShrink: 0,
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
            flex: '1 1 0',
            minHeight: 0,
            overflowY: 'auto',
            padding: 'var(--space-lg)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-md)'
          }}
        >
          {activeConv.messages.length === 0 && (
            <div style={{ margin: 'auto', textAlign: 'center', maxWidth: '560px', color: 'var(--color-text-secondary)', padding: 'var(--space-md) 0' }}>
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-ai-500)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF',
                  margin: '0 auto var(--space-sm) auto'
                }}
              >
                <Sparkles size={20} />
              </div>
              <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', color: 'var(--color-text-primary)', marginBottom: '6px' }}>
                Legal AI Consultation Ready
              </h3>
              <p style={{ fontSize: 'var(--text-caption)', lineHeight: 1.5, marginBottom: 'var(--space-lg)' }}>
                Professional intelligence for lawyers: statutory interpretations (BNS/BNSS/BSA), case analysis, evidence evaluation, and hearing preparation.
              </p>

              <div style={{ textAlign: 'left', marginBottom: '8px' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)' }}>
                  What can I help with?
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', textAlign: 'left' }}>
                {[
                  { icon: '🔎', title: 'Research a legal provision', query: 'What does BNS Section 103 provide?' },
                  { icon: '📁', title: 'Analyze a case', query: 'Summarize this case and outline the key facts.' },
                  { icon: '📄', title: 'Review a document', query: 'What documents or evidence are missing in my case?' },
                  { icon: '⚖️', title: 'Evaluate evidence', query: 'Analyze the evidence and check for contradictions in witness statements.' },
                  { icon: '📝', title: 'Draft a legal document', query: 'How should a legal notice be structured?' },
                  { icon: '📅', title: 'Prepare for a hearing', query: 'Prepare me for the upcoming hearing and outline key arguments.' },
                ].map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      setInputQuery(item.query);
                    }}
                    style={{
                      padding: '10px 12px',
                      backgroundColor: 'var(--color-bg-surface)',
                      border: '1px solid var(--color-border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      textAlign: 'left'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = 'var(--color-ai-300)';
                      e.currentTarget.style.backgroundColor = 'var(--color-ai-50)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = 'var(--color-border-subtle)';
                      e.currentTarget.style.backgroundColor = 'var(--color-bg-surface)';
                    }}
                  >
                    <span style={{ fontSize: '16px' }}>{item.icon}</span>
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                      {item.title}
                    </span>
                  </button>
                ))}
              </div>
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
                {isLawyer ? (
                  <div
                    style={{
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      border: '1px solid var(--color-border-subtle)',
                      borderRadius: 'var(--radius-chat-bubble-lawyer)',
                      padding: 'var(--space-md)',
                      boxShadow: 'var(--elevation-0)',
                      position: 'relative'
                    }}
                  >
                    <div
                      style={{
                        fontFamily: 'var(--font-sans)',
                        fontSize: 'var(--text-body)',
                        color: 'var(--color-text-primary)',
                        lineHeight: 1.6,
                        whiteSpace: 'pre-line'
                      }}
                    >
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  <div
                    style={{
                      backgroundColor: 'var(--color-bg-surface)',
                      border: '1px solid var(--color-ai-border)',
                      borderRadius: 'var(--radius-chat-bubble-ai)',
                      padding: 'var(--space-md) var(--space-lg)',
                      boxShadow: 'var(--elevation-1)',
                      position: 'relative',
                      width: '100%'
                    }}
                  >
                    <LegalAnswerRenderer message={msg} isStreaming={false} />
                  </div>
                )}
              </div>
            );
          })}

          {/* Thinking / Generation Stage Indicator before tokens arrive */}
          {isGenerating && !streamingText && (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignSelf: 'flex-start',
                maxWidth: '85%',
                width: '100%',
                animation: 'fadeIn 0.2s ease-in-out'
              }}
            >
              <div
                style={{
                  backgroundColor: 'var(--color-bg-surface)',
                  border: '1px solid var(--color-ai-border)',
                  borderRadius: 'var(--radius-chat-bubble-ai)',
                  padding: '12px 18px',
                  boxShadow: 'var(--elevation-1)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '10px',
                  width: 'fit-content'
                }}
              >
                <div
                  style={{
                    width: '14px',
                    height: '14px',
                    borderRadius: '50%',
                    border: '2px solid var(--color-ai-200)',
                    borderTopColor: 'var(--color-ai-600)',
                    animation: 'spin 0.9s linear infinite',
                    flexShrink: 0
                  }}
                />
                <span style={{ fontSize: '13px', color: 'var(--color-ink-700)', fontWeight: 500, fontFamily: 'var(--font-sans)' }}>
                  {currentStages[thinkingStageIndex] || currentStages[0]}
                </span>
              </div>
            </div>
          )}

          {/* Active Streaming Token Render with LegalAnswerRenderer and stage header */}
          {isGenerating && streamingText && (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignSelf: 'flex-start',
                maxWidth: '85%',
                width: '100%'
              }}
            >
              <div
                style={{
                  backgroundColor: 'var(--color-bg-surface)',
                  border: '1px solid var(--color-ai-border)',
                  borderRadius: 'var(--radius-chat-bubble-ai)',
                  padding: 'var(--space-md) var(--space-lg)',
                  boxShadow: 'var(--elevation-1)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px', opacity: 0.85, fontSize: '11px', color: 'var(--color-ai-600)', fontWeight: 500 }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', border: '1.5px solid var(--color-ai-300)', borderTopColor: 'var(--color-ai-600)', animation: 'spin 0.9s linear infinite', flexShrink: 0 }} />
                  <span>{currentStages[thinkingStageIndex] || "Preparing grounded response…"}</span>
                </div>
                <LegalAnswerRenderer
                  message={{
                    id: 'streaming-active',
                    role: 'assistant',
                    content: streamingText
                  }}
                  isStreaming={true}
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
            flexShrink: 0,
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
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
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
