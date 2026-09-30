import React, { useState, useRef, useEffect, useMemo } from 'react';
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
  Layers,
  Edit2,
  Trash2,
  X,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  Scale
} from 'lucide-react';
import { Button } from '../common/Button';
import { ReliabilityBadge } from '../common/Badge';
import { SelectedTextAskAI } from './SelectedTextAskAI';
import { LegalAnswerRenderer } from './LegalAnswerRenderer';
import { INITIAL_CONVERSATIONS } from '../../mock/mockAI';
import { INITIAL_CASES } from '../../mock/mockCases';
import { aiService } from '../../services/aiService';


export function formatConversationTime(dateStrOrTimestamp) {
  if (!dateStrOrTimestamp) return 'Recently';
  let date;
  if (typeof dateStrOrTimestamp === 'number') {
    date = new Date(dateStrOrTimestamp);
  } else if (typeof dateStrOrTimestamp === 'string') {
    if (dateStrOrTimestamp === 'Just now' || dateStrOrTimestamp === 'Recently') {
      return dateStrOrTimestamp;
    }
    date = new Date(dateStrOrTimestamp);
    if (isNaN(date.getTime())) {
      return dateStrOrTimestamp;
    }
  } else {
    return 'Recently';
  }

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const isToday = now.toDateString() === date.toDateString();
  if (isToday) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  if (yesterday.toDateString() === date.toDateString()) {
    return `Yesterday, ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  }

  if (diffMs < 7 * 24 * 3600 * 1000) {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return `${days[date.getDay()]}, ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  }

  return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

export function groupConversationsByDate(convList) {
  const groups = {
    today: [],
    yesterday: [],
    last7Days: [],
    older: []
  };

  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const startOfYesterday = startOfToday - 24 * 3600 * 1000;
  const startOf7Days = startOfToday - 6 * 24 * 3600 * 1000;

  (convList || []).forEach(conv => {
    let convTime = 0;
    if (conv.updatedAt) {
      if (typeof conv.updatedAt === 'number') {
        convTime = conv.updatedAt;
      } else {
        const parsed = new Date(conv.updatedAt).getTime();
        if (!isNaN(parsed)) {
          convTime = parsed;
        } else if (conv.updatedAt.toLowerCase().includes('yesterday')) {
          convTime = startOfYesterday + 12 * 3600 * 1000;
        } else if (conv.updatedAt.toLowerCase().includes('just now')) {
          convTime = now.getTime();
        } else {
          const match = conv.id && conv.id.match(/conv-(\d+)/);
          if (match) convTime = parseInt(match[1], 10);
        }
      }
    } else {
      const match = conv.id && conv.id.match(/conv-(\d+)/);
      if (match) convTime = parseInt(match[1], 10);
    }

    if (convTime >= startOfToday) {
      groups.today.push(conv);
    } else if (convTime >= startOfYesterday) {
      groups.yesterday.push(conv);
    } else if (convTime >= startOf7Days) {
      groups.last7Days.push(conv);
    } else {
      groups.older.push(conv);
    }
  });

  return groups;
}

export function deriveDynamicSuggestions(msg) {
  if (!msg || !msg.content) return [];
  const text = msg.content;
  const lower = text.toLowerCase();
  const suggestions = [];

  // 1. Evidence / Bharatiya Sakshya Adhiniyam (BSA) / Section 161 BSA / Section 63 BSA
  if (lower.includes('sakshya') || lower.includes('bsa') || lower.includes('evidence act') || lower.includes('refreshing memory') || lower.includes('section 161') || lower.includes('section 63')) {
    if (lower.includes('161') || lower.includes('refreshing memory') || lower.includes('production of document')) {
      suggestions.push(
        { label: "Refreshing witness memory rules", query: "What are the legal conditions under BSA Section 161 for an adverse party to inspect and cross-examine on a writing used to refresh memory?" },
        { label: "IEA s.159 vs BSA s.161", query: "Compare Indian Evidence Act Section 159-161 with Bharatiya Sakshya Adhiniyam Section 161." },
        { label: "Leading Supreme Court rulings", query: "What are the landmark Supreme Court judgments interpreting the right of inspection of documents used to refresh memory?" }
      );
    } else if (lower.includes('63') || lower.includes('electronic record') || lower.includes('hash')) {
      suggestions.push(
        { label: "Mandatory Certificate under BSA s.63", query: "What are the exact statutory requirements for an electronic evidence certificate under BSA Section 63(4)?" },
        { label: "Arjun Panditrao applicability", query: "How does the Supreme Court ruling in Arjun Panditrao apply to electronic evidence under the Bharatiya Sakshya Adhiniyam, 2023?" },
        { label: "Hash digest verification at trial", query: "What is the procedure for proving cryptographic hash digest integrity during trial cross-examination?" }
      );
    } else {
      suggestions.push(
        { label: "Admissibility requirements", query: "What are the statutory prerequisites to make this evidence admissible under the Bharatiya Sakshya Adhiniyam?" },
        { label: "Burden of proof & presumptions", query: "What statutory presumptions apply to these documents under the Bharatiya Sakshya Adhiniyam?" },
        { label: "Cross-examination strategy", query: "How can the opposing counsel cross-examine the witness regarding the authenticity of these records?" }
      );
    }
  }
  // 2. Contract Act / Specific Relief Act
  else if (lower.includes('contract act') || lower.includes('specific relief') || lower.includes('breach') || lower.includes('section 23') || lower.includes('section 32') || lower.includes('injunction')) {
    if (lower.includes('section 23') || lower.includes('unlawful') || lower.includes('public policy')) {
      suggestions.push(
        { label: "Void agreements under Section 23", query: "What are the judicial tests for agreements opposed to public policy or forbidden by law under Section 23 Contract Act?" },
        { label: "Restitution under Section 65", query: "Can a party claim restitution or refund of consideration when an agreement is discovered to be void under Section 65?" },
        { label: "Draft defense on illegality", query: "Draft preliminary objections asserting that the agreement is void and unenforceable under Section 23 Indian Contract Act." }
      );
    } else {
      suggestions.push(
        { label: "Remedies for breach (s.73)", query: "What damages or compensation can be claimed for breach under Section 73 Indian Contract Act?" },
        { label: "Specific performance test", query: "What are the essential requirements for grant of specific performance under the Specific Relief Act?" },
        { label: "Interim injunction under Order 39", query: "Analyze prima facie case, balance of convenience, and irreparable injury for interim injunction." }
      );
    }
  }
  // 3. Criminal / BNS / BNSS / Bail
  else if (lower.includes('bharatiya nyaya sanhita') || lower.includes('bns') || lower.includes('bnss') || lower.includes('bail') || lower.includes('ipc') || lower.includes('section 189') || lower.includes('threat')) {
    if (lower.includes('189') || lower.includes('threat') || lower.includes('public servant')) {
      suggestions.push(
        { label: "Ingredients of Section 189 BNS", query: "What are the essential ingredients required to constitute the offence under Section 189 Bharatiya Nyaya Sanhita?" },
        { label: "Bail schedule & cognizable status", query: "Is Section 189 BNS cognizable, bailable, and compoundable under the First Schedule of BNSS?" },
        { label: "Procedural defenses", query: "What procedural safeguards and preliminary defenses are available to challenge charges under Section 189 BNS?" }
      );
    } else if (lower.includes('bail') || lower.includes('custody')) {
      suggestions.push(
        { label: "Regular bail under BNSS s.480", query: "Draft grounds for regular bail under Section 480 BNSS highlighting absence of flight risk." },
        { label: "Parity with co-accused", query: "How does the principle of parity apply where co-accused have been granted bail?" },
        { label: "Default bail under BNSS s.187", query: "What are the statutory conditions for default bail under Section 187 BNSS?" }
      );
    } else {
      suggestions.push(
        { label: "Cognizability & trial forum", query: "What is the prescribed punishment and which court has jurisdiction to try this offence?" },
        { label: "Essential prosecution proof", query: "What must the prosecution establish beyond reasonable doubt to prove this charge?" },
        { label: "Discharge application under BNSS", query: "What are the grounds to seek discharge before framing of charges under BNSS?" }
      );
    }
  }
  // 4. Commercial / Arbitration / Maritime / Demurrage
  else if (lower.includes('arbitration') || lower.includes('commercial') || lower.includes('lien') || lower.includes('demurrage')) {
    suggestions.push(
      { label: "Section 9 interim relief", query: "Draft an urgent petition under Section 9 of the Arbitration and Conciliation Act for interim preservation of goods." },
      { label: "Challenge to lien", query: "What are the grounds to invalidate an unlawful possessory lien under Indian commercial law?" },
      { label: "Section 11 arbitrator appointment", query: "What is the procedure to approach the High Court under Section 11(6) for appointment of sole arbitrator?" }
    );
  }

  // 5. Section extractor fallback
  if (suggestions.length === 0) {
    const secMatches = [...text.matchAll(/Section\s+(\d+[A-Z]?)/gi)];
    if (secMatches.length > 0) {
      const uniqueSecs = [...new Set(secMatches.map(m => m[0]))].slice(0, 3);
      uniqueSecs.forEach(sec => {
        suggestions.push({
          label: `${sec} interpretation`,
          query: `What is the judicial interpretation and essential ingredients of ${sec}?`
        });
      });
      if (suggestions.length < 3) {
        suggestions.push({
          label: "Procedural defenses & reliefs",
          query: "What procedural defenses or legal remedies are available under these statutory provisions?"
        });
      }
    } else {
      suggestions.push(
        { label: "Judicial precedents", query: "What are the leading Supreme Court judgments interpreting these provisions?" },
        { label: "Procedural next steps", query: "What are the recommended procedural next steps and filing deadlines?" },
        { label: "Drafting template", query: "Provide a structured pleading outline or petition draft for this matter." }
      );
    }
  }

  return suggestions.slice(0, 3);
}

const createFreshConversation = (mode = 'GENERAL', lockedCase = null) => ({
  updatedAt: new Date().toISOString(),
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
  messages: []
});

export const AIAssistantView = ({ 
  initialMode = 'GENERAL', 
  lockedCase = null, 
  allCases = INITIAL_CASES 
}) => {
  const [conversations, setConversations] = useState(() => {
    const stored = aiService.getStoredConversations();
    if (stored && stored.length > 0) return stored;
    const fresh = createFreshConversation(initialMode, lockedCase);
    return [fresh, ...INITIAL_CONVERSATIONS];
  });
  const [activeConvId, setActiveConvId] = useState(() => {
    const savedActive = localStorage.getItem('legalai_active_conv_id');
    const stored = aiService.getStoredConversations();
    if (savedActive && stored.some(c => c.id === savedActive)) return savedActive;
    // Prefer first conversation that has messages so user returns right to their active work
    const withMessages = stored.find(c => c.messages && c.messages.length > 0);
    if (withMessages) return withMessages.id;
    return stored[0]?.id || `conv-${Date.now()}`;
  });
  const [editingConvId, setEditingConvId] = useState(null);
  const [editTitleInput, setEditTitleInput] = useState('');

  // Persist activeConvId across tab navigation (e.g. Calendar <-> AI Assistant)
  useEffect(() => {
    if (activeConvId) {
      localStorage.setItem('legalai_active_conv_id', activeConvId);
    }
  }, [activeConvId]);

  // Auto-persist all conversations on every turn (user message, AI completion, rename, delete)
  useEffect(() => {
    if (conversations && conversations.length > 0) {
      aiService.saveAllConversations(conversations);
    }
  }, [conversations]);

  // Sync conversations from Supabase / Backend on mount without overwriting active messages
  useEffect(() => {
    aiService.getConversations().then(syncedConvs => {
      if (syncedConvs && syncedConvs.length > 0) {
        setConversations(syncedConvs);
      }
    }).catch(err => console.warn('[AIAssistantView] sync error:', err));
  }, []);

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
        aiService.saveConversation(fresh);
        return [fresh, ...prev];
      });
    }
  }, [lockedCase?.id, lockedCase?.caseNumber]);

  const [inputQuery, setInputQuery] = useState(() => {
    const pending = sessionStorage.getItem('courtroom_ai_prompt');
    if (pending) {
      sessionStorage.removeItem('courtroom_ai_prompt');
      return pending;
    }
    return '';
  });

  useEffect(() => {
    const pending = sessionStorage.getItem('courtroom_ai_prompt');
    if (pending) {
      setInputQuery(pending);
      sessionStorage.removeItem('courtroom_ai_prompt');
    }
  }, []);
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
  const [showContextDropdown, setShowContextDropdown] = useState(false);
  const contextDropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (contextDropdownRef.current && !contextDropdownRef.current.contains(event.target)) {
        setShowContextDropdown(false);
      }
    };
    if (showContextDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showContextDropdown]);
  const [historySearch, setHistorySearch] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const isSubmittingRef = useRef(false);

  // Temporary Chat (Incognito mode: not saved to history or database)
  const [isTemporaryChat, setIsTemporaryChat] = useState(false);
  const [tempMessages, setTempMessages] = useState([]);
  const [copiedMsgId, setCopiedMsgId] = useState(null);

  // Track recent questions to drive dynamic suggestions
  const [recentQueries, setRecentQueries] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('legalai_recent_queries') || '[]');
    } catch {
      return [];
    }
  });

  const recordRecentQuery = (text) => {
    try {
      const existing = JSON.parse(localStorage.getItem('legalai_recent_queries') || '[]');
      const updated = [text, ...existing.filter(q => q.toLowerCase() !== text.toLowerCase())].slice(0, 10);
      localStorage.setItem('legalai_recent_queries', JSON.stringify(updated));
      setRecentQueries(updated);
    } catch (e) {
      console.warn(e);
    }
  };

  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const stopGenerationRef = useRef(null);

  const fallbackConv = useMemo(() => createFreshConversation(initialMode, lockedCase), [initialMode, lockedCase]);
  const activeConv = (conversations && conversations.length > 0)
    ? (conversations.find(c => c.id === activeConvId) || conversations[0])
    : fallbackConv;

  const activeMessages = isTemporaryChat ? tempMessages : (activeConv?.messages || []);

  // Dynamic consultation starters derived from recent lawyer inquiries
  const dynamicSuggestions = useMemo(() => {
    const pastText = (activeConv?.messages || []).map(m => m.content).join(' ').toLowerCase() + ' ' + recentQueries.join(' ').toLowerCase();

    if (pastText.includes('bail') || pastText.includes('arrest') || pastText.includes('remand') || pastText.includes('whitfield') || pastText.includes('police') || pastText.includes('custody')) {
      return {
        heading: 'Tailored Next Steps: Bail & Criminal Defense',
        badge: 'BASED ON RECENT INQUIRIES',
        items: [
          { icon: '⚖️', title: 'Regular bail under BNSS s.480', desc: 'Grounds on lack of flight risk, tampering & parity', query: 'Draft regular bail application for Sessions Court citing Section 480 BNSS and parity grounds.' },
          { icon: '🔍', title: 'Challenge electronic seizure (BSA s.63)', desc: 'Examine mandatory certificate & chain of custody flaws', query: 'Examine admissibility of seized digital device evidence without Certificate under BSA Section 63.' },
          { icon: '📋', title: 'Parity with co-accused on bail', desc: 'Draft parity comparison showing identical or lesser role', query: 'Draft arguments on parity showing client had identical or lesser role than enlarged co-accused.' },
          { icon: '⏳', title: '24-hour detention & magistrate remand', desc: 'Scrutinize Article 22(2) and BNSS s.57 timeline', query: 'Check police compliance with Article 22(2) and BNSS Section 57 for magistrate remand.' },
          { icon: '📝', title: 'Cross-examine on search seizure memo', desc: 'Pointers on independent panch witness contradictions', query: 'Draft cross-examination questions for investigating officer regarding absence of independent panch witnesses.' },
          { icon: '🏛️', title: 'Anticipatory bail petition under s.482', desc: 'Pre-arrest protection in Sessions / High Court', query: 'What are the exceptional grounds for anticipatory bail under BNSS Section 482?' }
        ]
      };
    }

    if (pastText.includes('cargo') || pastText.includes('lien') || pastText.includes('injunction') || pastText.includes('martinez') || pastText.includes('arbitration') || pastText.includes('strike') || pastText.includes('charterparty')) {
      return {
        heading: 'Tailored Next Steps: Commercial Injunction & Maritime Disputes',
        badge: 'BASED ON RECENT INQUIRIES',
        items: [
          { icon: '⚡', title: 'Order 39 Rule 1 & 2 injunction merits', desc: 'Prima facie case, irreparable injury & balance of convenience', query: 'Analyze prima facie case, balance of convenience, and irreparable injury test for interim injunction.' },
          { icon: '📜', title: 'Section 9 petition for cargo preservation', desc: 'Urgent interim measure under Arbitration & Conciliation Act', query: 'Draft Section 9 petition under Arbitration Act for immediate court preservation of cargo.' },
          { icon: '🚢', title: 'Scrutinize cargo lien legality', desc: 'Lien enforceability after notice of dispute & tender of security', query: 'Evaluate maritime lien enforceability against cargo after notice of charterparty dispute.' },
          { icon: '⚖️', title: 'Force majeure defense for demurrage', desc: 'Port strike suspension of laytime & penalty clauses', query: 'Examine whether port authority strike constitutes valid force majeure to suspend demurrage.' },
          { icon: '📝', title: 'Urgent demand notice for unlading', desc: 'Formal advocate notice demanding immediate release of goods', query: 'Draft formal advocate demand notice for immediate unlading and release of detained goods.' },
          { icon: '🏢', title: 'Commercial Courts Act Section 12A', desc: 'Exemption from pre-institution mediation for urgent interim relief', query: 'Explain Section 12A Commercial Courts Act exemption from mandatory pre-institution mediation for urgent interim relief.' }
        ]
      };
    }

    if (pastText.includes('evidence') || pastText.includes('witness') || pastText.includes('deposition') || pastText.includes('contradiction')) {
      return {
        heading: 'Tailored Next Steps: Evidentiary Evaluation & Trial Strategy',
        badge: 'BASED ON RECENT INQUIRIES',
        items: [
          { icon: '🔍', title: 'Cross-examine prime witness on omissions', desc: 'Prepare questions highlighting material omissions under Section 161', query: 'Prepare cross-examination questions highlighting material omissions under Section 161 statements.' },
          { icon: '📑', title: 'Electronic evidence admissibility (BSA s.63)', desc: 'Check mandatory requirements for Section 63 BSA certificate', query: 'Check mandatory requirements for Section 63 BSA electronic certificate and custody log.' },
          { icon: '⚖️', title: 'Identify contradictions in police diary', desc: 'Compare witness deposition against general diary entries', query: 'Compare witness deposition against general diary entries to reveal timeline contradictions.' },
          { icon: '📝', title: 'Draft list of defense witness summons', desc: 'Draft application to summon defense witnesses and forensic records', query: 'Draft application under BNSS to summon defense witnesses and forensic records.' },
          { icon: '🔬', title: 'Forensic hash verification of digital seizure', desc: 'Challenge digital evidence where SHA-256 hash was omitted', query: 'Explain procedure to challenge digital evidence where SHA-256 hash was not recorded at seizure.' },
          { icon: '📄', title: 'Filing gaps in prosecution chargesheet', desc: 'Identify critical evidentiary lacunae and missing annexures', query: 'Identify critical evidentiary lacunae and missing annexures in the chargesheet.' }
        ]
      };
    }

    // Default general starters
    return {
      heading: 'Suggested Consultation Starters',
      badge: 'STANDARD PRACTICE',
      items: [
        { icon: '🔎', title: 'Research a legal provision', desc: 'Exact section lookup across BNS, BNSS, BSA, CPC', query: 'Explain the scope and changes under BNS Section 103 compared to old IPC Section 302.' },
        { icon: '📁', title: 'Analyze an active case file', desc: 'Case summary, established facts, and key issues', query: 'Summarize this case and outline the key facts, established precedents, and core issues.' },
        { icon: '📄', title: 'Review missing documents & filings', desc: 'Identify evidentiary and filing gaps in pleadings', query: 'What documents or evidence are missing in my case pleadings before the next hearing?' },
        { icon: '⚖️', title: 'Evaluate witness evidence & statements', desc: 'Check for contradictions in statements and chargesheet', query: 'Analyze the evidence and check for contradictions in witness statements and chargesheet.' },
        { icon: '📝', title: 'Draft a court petition or legal notice', desc: 'Structured civil petition, plaint, or legal notice', query: 'Draft a formal legal notice demanding compliance and threatening legal proceedings.' },
        { icon: '📅', title: 'Prepare for hearing & procedural timeline', desc: 'Key arguments, risks, and procedural timeline', query: 'Prepare me for the upcoming court hearing and outline top 3 arguments for the Bench.' },
      ]
    };
  }, [activeConv?.messages, recentQueries]);

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
  }, [activeConv?.messages, streamingText]);

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
    const isTechOrSystem = /\b(qwen|model|llm|rag|lora|fine-?tuning|embeddings?|vector|database|powers?|built|technolog|ai|machine learning)\b/i.test(t);
    const isCaseEvidence = /\b(evidence|missing|contradiction|witness|chargesheet|pleading|allege|allegation)\b/i.test(t) || 
      (/\b(my case|our case|this case|uploaded documents?)\b/i.test(t) && !/\b(which case|focus|priority|urgent|hearing)\b/i.test(t));
    const isCaseMgmt = /\b(focus|priority|urgent|upcoming hearing|next hearing|deadlines?|calendar|cases?)\b/i.test(t);
    const isLegal = /\b(bns|bnss|bsa|ipc|crpc|iea|section|act|statute|offence|punishment|bail|cognizable|bailable|high court|supreme court|negligence|defamation|fir|self[\s-]defence|consideration|contract)\b/i.test(t);

    if (isTechOrSystem) {
      return [
        "Analyzing technical architecture… 🧠",
        "Formulating system explanation…"
      ];
    }
    if (isCaseMgmt) {
      return [
        "Consulting active case portfolio… 📁",
        "Reviewing priorities and hearings…"
      ];
    }
    if (isCaseEvidence) {
      return [
        "Reviewing case documents… 📁",
        "Evaluating evidentiary points… ⚖️",
        "Synthesizing case findings…"
      ];
    }
    if (isLegal) {
      return [
        "Understanding legal inquiry…",
        "Retrieving authoritative legal provisions… ⚖️",
        "Preparing grounded statutory response…"
      ];
    }
    return [
      "Thinking…",
      "Analyzing query…"
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

  const handleToggleMultiCase = (caseId) => {
    const currentList = activeConv?.selectedCases || [];
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
  const handleSendMessage = (eOrQuery) => {
    if (eOrQuery && typeof eOrQuery.preventDefault === 'function') {
      eOrQuery.preventDefault();
    }
    if (eOrQuery && typeof eOrQuery.stopPropagation === 'function') {
      eOrQuery.stopPropagation();
    }
    if (isSubmittingRef.current || isGenerating) {
      return;
    }
    const userText = (typeof eOrQuery === 'string' && eOrQuery.trim()) ? eOrQuery.trim() : inputQuery.trim();
    if (!userText) return;

    isSubmittingRef.current = true;
    setInputQuery('');

    // Safety fallback to release submit lock
    setTimeout(() => {
      isSubmittingRef.current = false;
    }, 1500);

    const targetConvId = activeConv?.id || activeConvId;
    const currentConv = conversations.find(c => c.id === targetConvId) || activeConv;
    const prevHistory = (currentConv?.messages || []).map(m => ({
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

    const nowIso = new Date().toISOString();
    // Update conversation title if this is the first message
    const shouldUpdateTitle = ((currentConv?.messages || []).length === 0);
    const newTitle = shouldUpdateTitle 
      ? (userText.slice(0, 32) + (userText.length > 32 ? '…' : ''))
      : (currentConv?.title || "Legal Inquiry");

    recordRecentQuery(userText);

    // Add user message to conversation or temporary messages
    if (isTemporaryChat) {
      setTempMessages(prev => {
        const lastMsg = prev[prev.length - 1];
        if (lastMsg && lastMsg.role === 'user' && lastMsg.content === userText) {
          return prev;
        }
        return [...prev, userMessage];
      });
    } else {
      setConversations(prev => {
        const found = prev.some(c => c.id === targetConvId);
        if (!found) {
          const fresh = {
            ...(currentConv || createFreshConversation()),
            id: targetConvId,
            title: newTitle,
            updatedAt: nowIso,
            messages: [...(currentConv?.messages || []), userMessage]
          };
          return [fresh, ...prev];
        }
        return prev.map(c => {
          if (c.id === targetConvId) {
            const currentMsgs = c.messages || [];
            const lastMsg = currentMsgs[currentMsgs.length - 1];
            if (lastMsg && lastMsg.role === 'user' && lastMsg.content === userText) {
              return c;
            }
            return {
              ...c,
              title: newTitle,
              updatedAt: nowIso,
              messages: [...currentMsgs, userMessage]
            };
          }
          return c;
        });
      });
    }

    // Setup thinking stages
    const stages = getThinkingStagesForQuery(userText, currentConv?.mode);
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
        isSubmittingRef.current = false;
        const finalContent = (aiMessage?.content && aiMessage.content.trim()) 
          ? aiMessage.content 
          : (streamingText || 'Response completed.');

        setStreamingText('');
        setGenerationState('COMPLETED');
        setTimeout(() => setGenerationState('IDLE'), 30);

        const safeAiMessage = {
          id: aiMessage?.id || `msg-${Date.now()}`,
          role: 'assistant',
          timestamp: aiMessage?.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          content: finalContent,
          reliability: aiMessage?.reliability || 'supported',
          reliabilityLabel: aiMessage?.reliabilityLabel || 'Supported by sources',
          sources: aiMessage?.sources || [],
          citations: aiMessage?.citations || [],
          query_type: aiMessage?.query_type || null,
          sub_intent: aiMessage?.sub_intent || null,
          user_goal: aiMessage?.user_goal || null,
          output_plan: aiMessage?.output_plan || null,
          suggestions: aiMessage?.suggestions || []
        };

        const nowIso = new Date().toISOString();
        if (isTemporaryChat) {
          setTempMessages(prev => [...prev, safeAiMessage]);
        } else {
          setConversations(prev => prev.map(c => {
            if (c.id === targetConvId) {
              const currentMsgs = c.messages || [];
              const hasFinal = currentMsgs.some(m => m.id === safeAiMessage.id);
              return {
                ...c,
                updatedAt: nowIso,
                messages: hasFinal ? currentMsgs : [...currentMsgs, safeAiMessage]
              };
            }
            return c;
          }));
        }
      },
      onError: (err) => {
        stopGenerationRef.current = null;
        isSubmittingRef.current = false;
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
        if (isTemporaryChat) {
          setTempMessages(prev => [...prev, errorMsg]);
        } else {
          setConversations(prev => prev.map(c => {
            if (c.id === targetConvId) {
              return { ...c, messages: [...c.messages, errorMsg] };
            }
            return c;
          }));
        }
      }
    });

    stopGenerationRef.current = stopFn;
  };

  const handleStopGeneration = () => {
    isSubmittingRef.current = false;
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
    aiService.saveConversation(freshConv);
  };

  const handleStartRename = (conv, e) => {
    if (e) e.stopPropagation();
    setEditingConvId(conv.id);
    setEditTitleInput(conv.title);
  };

  const handleSaveRename = async (convId, e) => {
    if (e) e.stopPropagation();
    const trimmed = editTitleInput.trim();
    if (!trimmed) {
      setEditingConvId(null);
      return;
    }
    setConversations(prev => prev.map(c => c.id === convId ? { ...c, title: trimmed } : c));
    await aiService.renameConversation(convId, trimmed);
    setEditingConvId(null);
  };

  const handleDeleteConversation = async (convId, e) => {
    if (e) e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this conversation?")) return;
    
    setConversations(prev => {
      const next = prev.filter(c => c.id !== convId);
      if (next.length === 0) {
        const fresh = createFreshConversation(initialMode, lockedCase);
        setActiveConvId(fresh.id);
        aiService.saveConversation(fresh);
        return [fresh];
      }
      if (activeConvId === convId) {
        setActiveConvId(next[0].id);
      }
      return next;
    });
    await aiService.deleteConversation(convId);
  };

  const handleClearAllHistory = async (e) => {
    if (e) e.stopPropagation();
    if (!window.confirm("Are you sure you want to clear all consultation history? This will start a fresh inquiry.")) return;

    const fresh = createFreshConversation(initialMode, lockedCase);
    setConversations([fresh]);
    setActiveConvId(fresh.id);

    if (aiService.clearAllConversations) {
      await aiService.clearAllConversations();
    }
    await aiService.saveConversation(fresh);
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
        display: 'flex',
        flexDirection: 'row',
        flex: 1,
        height: '100%',
        width: '100%',
        minHeight: 0,
        backgroundColor: 'var(--color-bg-surface)',
        border: lockedCase ? '1px solid var(--color-border-subtle)' : 'none',
        borderRadius: lockedCase ? 'var(--radius-lg)' : 0,
        overflow: 'hidden'
      }}
      className="ai-workspace-container"
    >
      <style>{`
        @keyframes slideDownCurtain {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
      {/* 1. Left Rail: Conversation History (§15.11) */}
      {isSidebarOpen && (
        <aside
          aria-label="Inquiry History"
          style={{
            backgroundColor: 'var(--color-bg-surface-sunken)',
            borderRight: '1px solid var(--color-border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            minHeight: 0,
            overflow: 'hidden',
            width: '280px',
            minWidth: '280px',
            maxWidth: '280px',
            flexShrink: 0
          }}
        >
          {/* Dedicated History Side Header with Weighing Balance Icon */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px 12px',
              borderBottom: '1px solid var(--color-border-subtle)',
              backgroundColor: 'var(--color-bg-surface)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Scale size={16} style={{ color: 'var(--color-ai-600, #4f46e5)' }} />
              <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-ink-900)' }}>
                Case Inquiries
              </span>
            </div>
            {/* Collapse button on the history side */}
            <button
              type="button"
              onClick={() => setIsSidebarOpen(false)}
              title="Collapse Inquiry History (Scales of Justice)"
              style={{
                background: 'none',
                border: '1px solid var(--color-border-subtle)',
                cursor: 'pointer',
                padding: '4px 6px',
                borderRadius: '6px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--color-text-secondary)',
                fontSize: '11px',
                fontWeight: 600,
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-ai-100)'; e.currentTarget.style.color = 'var(--color-ai-700)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
            >
              <Scale size={13} style={{ color: 'var(--color-ai-600)' }} />
              <PanelLeftClose size={13} />
            </button>
          </div>

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
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 8px 4px 8px' }}>
            <span style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)', fontWeight: 600 }}>
              Recent Legal Inquiries
            </span>
            {conversations.length > 0 && (
              <button
                type="button"
                onClick={handleClearAllHistory}
                title="Clear all chat history"
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--color-text-muted)',
                  fontSize: '10px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '3px',
                  padding: '2px 4px',
                  borderRadius: '3px',
                  transition: 'color 0.15s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--color-text-muted)'}
              >
                <Trash2 size={10} />
                <span>Clear All</span>
              </button>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {(() => {
              const groups = groupConversationsByDate(filteredConversations);
              const groupDefs = [
                { key: 'today', label: 'Today', items: groups.today },
                { key: 'yesterday', label: 'Yesterday', items: groups.yesterday },
                { key: 'last7Days', label: 'Previous 7 Days', items: groups.last7Days },
                { key: 'older', label: 'Older', items: groups.older }
              ];
              const hasAny = groupDefs.some(g => g.items.length > 0);

              if (!hasAny) {
                return (
                  <div style={{ textAlign: 'center', padding: '24px 12px', color: 'var(--color-text-muted)', fontSize: '12px' }}>
                    No consultations found
                  </div>
                );
              }

              return groupDefs.map(group => {
                if (group.items.length === 0) return null;
                return (
                  <div key={group.key} style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                    <div style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-text-muted)', fontWeight: 700, padding: '4px 6px 2px 6px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span>{group.label}</span>
                      <span style={{ fontSize: '9px', opacity: 0.65 }}>{group.items.length}</span>
                    </div>

                    {group.items.map((conv) => {
                      const isActive = conv.id === activeConvId;
                      const isEditing = editingConvId === conv.id;
                      return (
                        <div
                          key={conv.id}
                          onClick={() => !isEditing && setActiveConvId(conv.id)}
                          style={{
                            width: '100%',
                            background: isActive ? 'var(--color-bg-surface)' : 'transparent',
                            border: isActive ? '1px solid var(--color-border-subtle)' : '1px solid transparent',
                            borderRadius: 'var(--radius-md)',
                            padding: '8px 10px',
                            textAlign: 'left',
                            cursor: isEditing ? 'default' : 'pointer',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '4px',
                            boxShadow: isActive ? 'var(--elevation-1)' : 'none',
                            position: 'relative'
                          }}
                        >
                          {isEditing ? (
                            <div 
                              style={{ display: 'flex', alignItems: 'center', gap: '4px', width: '100%' }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <input
                                type="text"
                                value={editTitleInput}
                                onChange={(e) => setEditTitleInput(e.target.value)}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') handleSaveRename(conv.id, e);
                                  if (e.key === 'Escape') setEditingConvId(null);
                                }}
                                autoFocus
                                style={{
                                  flex: 1,
                                  fontSize: '12px',
                                  padding: '3px 6px',
                                  border: '1px solid var(--color-accent-700)',
                                  borderRadius: 'var(--radius-sm)',
                                  outline: 'none',
                                  backgroundColor: 'var(--color-bg-surface-sunken)',
                                  color: 'var(--color-ink-900)'
                                }}
                              />
                              <button
                                title="Save chat title"
                                onClick={(e) => handleSaveRename(conv.id, e)}
                                style={{
                                  background: 'none',
                                  border: 'none',
                                  cursor: 'pointer',
                                  color: 'var(--color-accent-700)',
                                  padding: '3px',
                                  display: 'flex',
                                  alignItems: 'center'
                                }}
                              >
                                <Check size={14} />
                              </button>
                              <button
                                title="Cancel"
                                onClick={(e) => { e.stopPropagation(); setEditingConvId(null); }}
                                style={{
                                  background: 'none',
                                  border: 'none',
                                  cursor: 'pointer',
                                  color: 'var(--color-text-muted)',
                                  padding: '3px',
                                  display: 'flex',
                                  alignItems: 'center'
                                }}
                              >
                                <X size={14} />
                              </button>
                            </div>
                          ) : (
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', gap: '6px' }}>
                              <span
                                style={{
                                  fontSize: '12px',
                                  fontWeight: isActive ? 600 : 500,
                                  color: isActive ? 'var(--color-ink-700)' : 'var(--color-text-primary)',
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap',
                                  flex: 1
                                }}
                                title={conv.title}
                              >
                                {conv.title}
                              </span>
                              <div 
                                style={{ display: 'flex', alignItems: 'center', gap: '3px', flexShrink: 0 }}
                                onClick={(e) => e.stopPropagation()}
                              >
                                <button
                                  title="Rename chat"
                                  onClick={(e) => handleStartRename(conv, e)}
                                  style={{
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    color: 'var(--color-text-muted)',
                                    padding: '2px 4px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    borderRadius: '3px'
                                  }}
                                  onMouseEnter={(e) => e.currentTarget.style.color = 'var(--color-ink-900)'}
                                  onMouseLeave={(e) => e.currentTarget.style.color = 'var(--color-text-muted)'}
                                >
                                  <Edit2 size={12} />
                                </button>
                                <button
                                  title="Delete chat"
                                  onClick={(e) => handleDeleteConversation(conv.id, e)}
                                  style={{
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    color: 'var(--color-text-muted)',
                                    padding: '2px 4px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    borderRadius: '3px'
                                  }}
                                  onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
                                  onMouseLeave={(e) => e.currentTarget.style.color = 'var(--color-text-muted)'}
                                >
                                  <Trash2 size={12} />
                                </button>
                              </div>
                            </div>
                          )}
                          
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '10px', color: 'var(--color-text-muted)' }}>
                            <span style={{ fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                              {conv.mode ? conv.mode.replace('_', ' ') : 'GENERAL'}
                            </span>
                            <span>{formatConversationTime(conv.updatedAt || conv.id)}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                );
              });
            })()}
          </div>
        </div>
        </aside>
      )}

      {/* 2. Main AI Panel */}
      <main
        style={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          flex: 1,
          minWidth: 0,
          width: isSidebarOpen ? 'calc(100% - 280px)' : '100%',
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
          {/* Left: History Opener (when closed) & Legal Weighing Balance Curtain Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {/* History Rail Opener with Weighing Balance (Only when closed) */}
            {!isSidebarOpen && (
              <button
                type="button"
                onClick={() => setIsSidebarOpen(true)}
                title="Open Case Inquiries History (Scales of Justice)"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 11px',
                  borderRadius: 'var(--radius-md, 8px)',
                  border: '1px solid var(--color-ai-border, var(--color-border-subtle))',
                  backgroundColor: 'var(--color-bg-surface)',
                  color: 'var(--color-ink-900)',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: 650,
                  boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
                  transition: 'all 0.15s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--color-ai-100)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--color-bg-surface)'}
              >
                <Scale size={15} style={{ color: 'var(--color-ai-600, #4f46e5)' }} />
                <span>History</span>
                <PanelLeftOpen size={13} style={{ color: 'var(--color-text-muted)' }} />
              </button>
            )}

            {/* Weighing Balance Legal Symbol Curtain Dropdown */}
            <div style={{ position: 'relative' }} ref={contextDropdownRef}>
              <button
                type="button"
                onClick={() => setShowContextDropdown(prev => !prev)}
                title="Toggle Legal Context & Case Curtain (Scales of Justice)"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '6px 14px',
                  borderRadius: 'var(--radius-md, 8px)',
                  border: showContextDropdown ? '1.5px solid var(--color-ai-500)' : '1px solid var(--color-ai-border)',
                  backgroundColor: showContextDropdown ? 'var(--color-accent-100)' : 'var(--color-bg-surface)',
                  color: 'var(--color-ink-900)',
                  fontSize: '12.5px',
                  fontWeight: 650,
                  cursor: 'pointer',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                  transition: 'all 0.18s ease'
                }}
              >
                <Scale size={16} style={{ color: 'var(--color-ai-600, #4f46e5)' }} />
                <span style={{ color: 'var(--color-text-secondary)', fontWeight: 500 }}>Legal Context Curtain:</span>
                <span style={{ color: 'var(--color-ink-900)', fontWeight: 700 }}>
                  {activeConv?.mode === 'SINGLE_CASE' 
                    ? (activeConv?.caseNumber || allCases?.[0]?.caseNumber || 'Single Matter')
                    : activeConv?.mode === 'MULTI_CASE'
                    ? `Multi-Matter (${activeConv?.selectedCases?.length || 2})`
                    : 'General Indian Law'}
                </span>
                {showContextDropdown ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>

              {/* The Judicial Context Curtain Dropdown Panel */}
              {showContextDropdown && (
                <div
                  style={{
                    position: 'absolute',
                    top: 'calc(100% + 8px)',
                    left: 0,
                    width: 'min(760px, calc(100vw - 340px))',
                    maxWidth: '92vw',
                    backgroundColor: 'var(--color-bg-surface)',
                    border: '1px solid var(--color-ai-border, var(--color-border-subtle))',
                    borderRadius: '14px',
                    boxShadow: '0 20px 35px -5px rgba(0,0,0,0.2), 0 10px 15px -5px rgba(0,0,0,0.1)',
                    zIndex: 80,
                    padding: '18px 20px 14px 20px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '14px',
                    animation: 'slideDownCurtain 0.22s cubic-bezier(0.16, 1, 0.3, 1)'
                  }}
                >
                  {/* Curtain Header */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border-subtle)', paddingBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'var(--color-ai-100)', color: 'var(--color-ai-600)' }}>
                        <Scale size={20} />
                      </div>
                      <div>
                        <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--color-ink-900)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span>Judicial Context & Case Dossier Curtain</span>
                          <span style={{ fontSize: '10px', padding: '1px 7px', borderRadius: '4px', backgroundColor: 'var(--color-ai-100)', color: 'var(--color-ai-700)', fontWeight: 650 }}>Scales of Justice</span>
                        </div>
                        <div style={{ fontSize: '11.5px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                          Configure consultation jurisdiction, bind active case records, and fine-tune statutory retrieval
                        </div>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setShowContextDropdown(false)}
                      title="Pull up curtain"
                      style={{
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        padding: '5px',
                        borderRadius: '6px',
                        color: 'var(--color-text-muted)'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.color = 'var(--color-ink-900)'}
                      onMouseLeave={(e) => e.currentTarget.style.color = 'var(--color-text-muted)'}
                    >
                      <X size={16} />
                    </button>
                  </div>

                  {/* 1. Legal Consultation Scope */}
                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      1. Legal Consultation Scope
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', backgroundColor: 'var(--color-bg-surface-sunken)', padding: '4px', borderRadius: '10px' }}>
                      <button
                        type="button"
                        onClick={() => { handleModeChange('GENERAL'); setShowCaseDropdown(false); }}
                        style={{
                          padding: '8px 10px',
                          borderRadius: '8px',
                          border: activeConv?.mode === 'GENERAL' ? '1px solid var(--color-ai-500)' : '1px solid transparent',
                          background: activeConv?.mode === 'GENERAL' ? 'var(--color-bg-surface)' : 'transparent',
                          color: activeConv?.mode === 'GENERAL' ? 'var(--color-ai-700, #4338ca)' : 'var(--color-text-secondary)',
                          fontSize: '12px',
                          fontWeight: 650,
                          cursor: 'pointer',
                          boxShadow: activeConv?.mode === 'GENERAL' ? '0 1px 3px rgba(0,0,0,0.06)' : 'none',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '6px'
                        }}
                      >
                        <BookOpen size={14} />
                        <span>General Indian Law</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => handleModeChange('SINGLE_CASE')}
                        style={{
                          padding: '8px 10px',
                          borderRadius: '8px',
                          border: activeConv?.mode === 'SINGLE_CASE' ? '1px solid var(--color-ai-500)' : '1px solid transparent',
                          background: activeConv?.mode === 'SINGLE_CASE' ? 'var(--color-bg-surface)' : 'transparent',
                          color: activeConv?.mode === 'SINGLE_CASE' ? 'var(--color-ai-700, #4338ca)' : 'var(--color-text-secondary)',
                          fontSize: '12px',
                          fontWeight: 650,
                          cursor: 'pointer',
                          boxShadow: activeConv?.mode === 'SINGLE_CASE' ? '0 1px 3px rgba(0,0,0,0.06)' : 'none',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '6px'
                        }}
                      >
                        <Scale size={14} />
                        <span>Single Matter / Case</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => handleModeChange('MULTI_CASE')}
                        style={{
                          padding: '8px 10px',
                          borderRadius: '8px',
                          border: activeConv?.mode === 'MULTI_CASE' ? '1px solid var(--color-ai-500)' : '1px solid transparent',
                          background: activeConv?.mode === 'MULTI_CASE' ? 'var(--color-bg-surface)' : 'transparent',
                          color: activeConv?.mode === 'MULTI_CASE' ? 'var(--color-ai-700, #4338ca)' : 'var(--color-text-secondary)',
                          fontSize: '12px',
                          fontWeight: 650,
                          cursor: 'pointer',
                          boxShadow: activeConv?.mode === 'MULTI_CASE' ? '0 1px 3px rgba(0,0,0,0.06)' : 'none',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '6px'
                        }}
                      >
                        <Layers size={14} />
                        <span>Multi-Matter Dossier</span>
                      </button>
                    </div>
                  </div>

                  {/* 2. Active Case Dossier Binding */}
                  {activeConv?.mode === 'SINGLE_CASE' && (
                    <div style={{ borderTop: '1px solid var(--color-border-subtle)', paddingTop: '10px' }}>
                      <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span>2. Active Case Dossier Binding</span>
                        <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', fontWeight: 500 }}>Select matter to ground legal citations</span>
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '8px', maxHeight: '160px', overflowY: 'auto', paddingRight: '4px' }}>
                        {allCases.map((c) => {
                          const isSelected = activeConv?.caseId === c.id || activeConv?.caseNumber === c.caseNumber;
                          return (
                            <button
                              key={c.id}
                              type="button"
                              onClick={() => { handleSwitchCase(c); }}
                              style={{
                                textAlign: 'left',
                                padding: '8px 10px',
                                background: isSelected ? 'var(--color-accent-100)' : 'var(--color-bg-surface-sunken)',
                                border: isSelected ? '1.5px solid var(--color-ai-500)' : '1px solid var(--color-border-subtle)',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '3px',
                                transition: 'all 0.15s ease'
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11.5px', fontWeight: 700, color: 'var(--color-ink-900)' }}>
                                  {c.caseNumber}
                                </span>
                                {isSelected && <Check size={12} style={{ color: 'var(--color-ai-600)' }} />}
                              </div>
                              <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                {c.title}
                              </span>
                              <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
                                {c.court || 'High Court of Delhi'}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* 3. Context Retrieval Filters */}
                  <div style={{ borderTop: '1px solid var(--color-border-subtle)', paddingTop: '10px' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-secondary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      3. Context Retrieval & Corpus Scope
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                      {[
                        { key: 'includeDocuments', label: 'Primary Evidence & Pleadings', desc: 'Petitions, chargesheets, affidavits' },
                        { key: 'includeNotes', label: 'Senior Counsel Notes', desc: 'Strategy briefs & attorney work product' },
                        { key: 'includeTimeline', label: 'Case Fact Chronology', desc: 'FIR dates, notices, order dates' },
                        { key: 'includeHistory', label: 'Prior Consultation Turns', desc: 'Preserve multi-turn reasoning context' }
                      ].map(({ key, label, desc }) => {
                        const isOn = !!activeConv?.contextSettings?.[key];
                        return (
                          <label
                            key={key}
                            style={{
                              display: 'flex',
                              alignItems: 'flex-start',
                              gap: '8px',
                              padding: '7px 9px',
                              borderRadius: '6px',
                              backgroundColor: isOn ? 'var(--color-ai-100)' : 'var(--color-bg-surface-sunken)',
                              border: isOn ? '1px solid var(--color-ai-border)' : '1px solid transparent',
                              cursor: 'pointer',
                              transition: 'all 0.15s ease'
                            }}
                          >
                            <input
                              type="checkbox"
                              checked={isOn}
                              onChange={() => handleToggleContextSetting(key)}
                              style={{ marginTop: '2px', cursor: 'pointer', accentColor: 'var(--color-ai-500)' }}
                            />
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                              <span style={{ fontSize: '11.5px', fontWeight: 600, color: 'var(--color-text-primary)' }}>{label}</span>
                              <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>{desc}</span>
                            </div>
                          </label>
                        );
                      })}
                    </div>
                  </div>

                  {/* Curtain Pull-Up Control Button */}
                  <div style={{ borderTop: '1px solid var(--color-border-subtle)', paddingTop: '10px', display: 'flex', justifyContent: 'center' }}>
                    <button
                      type="button"
                      onClick={() => setShowContextDropdown(false)}
                      title="Pull up legal context curtain"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '6px 20px',
                        borderRadius: 'var(--radius-full, 9999px)',
                        backgroundColor: 'var(--color-bg-surface-sunken)',
                        border: '1px solid var(--color-border-subtle)',
                        color: 'var(--color-text-secondary)',
                        fontSize: '11.5px',
                        fontWeight: 650,
                        cursor: 'pointer',
                        transition: 'all 0.15s ease'
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-ai-100)'; e.currentTarget.style.color = 'var(--color-ai-700)'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-bg-surface-sunken)'; e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
                    >
                      <ChevronUp size={14} />
                      <span>Pull Up Legal Curtain</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right: Temporary Chat Symbol Button (Outside the dropdown box for instant access) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              type="button"
              onClick={() => {
                if (!isTemporaryChat) {
                  setTempMessages([]);
                }
                setIsTemporaryChat(!isTemporaryChat);
              }}
              title={isTemporaryChat ? "Temporary Chat is ON (Incognito mode - chats not saved to history)" : "Turn ON Temporary Chat (Incognito mode - chats not saved to history)"}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '5px 11px',
                borderRadius: 'var(--radius-md, 8px)',
                border: isTemporaryChat ? '1px solid #f59e0b' : '1px solid var(--color-ai-border, var(--color-border-subtle))',
                backgroundColor: isTemporaryChat ? '#fef3c7' : 'var(--color-bg-surface)',
                color: isTemporaryChat ? '#b45309' : 'var(--color-text-secondary)',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: 600,
                transition: 'all 0.15s ease',
                boxShadow: isTemporaryChat ? '0 0 0 2px rgba(245, 158, 11, 0.25)' : 'none'
              }}
            >
              <span style={{ fontSize: '14px', lineHeight: 1 }}>🕶️</span>
              {isTemporaryChat ? (
                <span style={{ fontSize: '11px', fontWeight: 700, color: '#b45309' }}>
                  Temporary ON
                </span>
              ) : (
                <span style={{ fontSize: '11px', fontWeight: 500, color: 'var(--color-text-muted)' }}>
                  Incognito
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Temporary Chat Active Banner */}
        {isTemporaryChat && (
          <div
            style={{
              backgroundColor: 'var(--color-warning-wash)',
              borderBottom: '1px solid var(--color-warning-border)',
              padding: '8px 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '12px',
              color: 'var(--color-warning-text)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '15px' }}>🕶️</span>
              <span style={{ fontWeight: 600 }}>Temporary Chat is Active</span>
              <span>&bull;</span>
              <span>Messages in this session will not be saved to your case history or local database.</span>
            </div>
            <button
              onClick={() => {
                setIsTemporaryChat(false);
                setTempMessages([]);
              }}
              style={{
                background: 'none',
                border: '1px solid var(--color-warning-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '2px 8px',
                fontSize: '11px',
                fontWeight: 600,
                color: 'var(--color-warning-text)',
                cursor: 'pointer'
              }}
            >
              Exit Temporary Chat
            </button>
          </div>
        )}

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
            {activeConv?.mode === 'SINGLE_CASE' ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span style={{ width: '8px', height: '8px', backgroundColor: 'var(--color-ink-700)', display: 'inline-block' }} />
                  <strong>Current Matter: {activeConv?.caseNumber || "Case 01"}</strong>
                  <span style={{ color: 'var(--color-text-muted)', fontSize: '11px' }}>(Locked, primary scope)</span>
                </div>

                <div style={{ marginBottom: '8px' }}>
                  <span style={{ color: 'var(--color-text-secondary)', marginRight: '12px' }}>Include facets:</span>
                  <label style={{ marginRight: '12px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={activeConv?.contextSettings?.includeDocuments ?? true}
                      onChange={() => handleToggleContextSetting('includeDocuments')}
                      style={{ accentColor: 'var(--color-accent-500)', marginRight: '4px' }}
                    />
                    Documents
                  </label>
                  <label style={{ marginRight: '12px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={activeConv?.contextSettings?.includeTimeline ?? true}
                      onChange={() => handleToggleContextSetting('includeTimeline')}
                      style={{ accentColor: 'var(--color-accent-500)', marginRight: '4px' }}
                    />
                    Timeline
                  </label>
                  <label style={{ marginRight: '12px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={activeConv?.contextSettings?.includeNotes ?? true}
                      onChange={() => handleToggleContextSetting('includeNotes')}
                      style={{ accentColor: 'var(--color-accent-500)', marginRight: '4px' }}
                    />
                    Advocate Notes
                  </label>
                </div>

                {/* Supporting Cases (additive context §15.6) */}
                <div>
                  <span style={{ color: 'var(--color-text-secondary)', marginRight: '8px' }}>Supporting matters:</span>
                  {allCases.filter(c => c.id !== activeConv?.caseId).map(sc => {
                    const isChecked = activeConv?.contextSettings?.supportingCases?.includes(sc.id);
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
            ) : activeConv?.mode === 'MULTI_CASE' ? (
              <div>
                <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '6px' }}>
                  Select Matters for Cross-Synthesis:
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {allCases.map(c => {
                    const isSelected = activeConv?.selectedCases?.includes(c.id);
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
            padding: '24px 16px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center'
          }}
        >
          <div
            style={{
              maxWidth: '960px',
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: '20px'
            }}
          >
            {activeMessages.length === 0 && (
              <div style={{ margin: '30px auto', textAlign: 'center', maxWidth: '680px', color: 'var(--color-text-secondary)', padding: '20px' }}>
                <div
                  style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '14px',
                    background: 'linear-gradient(135deg, #1e3a8a, #3b82f6)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#FFFFFF',
                    margin: '0 auto 16px auto',
                    boxShadow: '0 4px 14px rgba(59, 130, 246, 0.25)'
                  }}
                >
                  <Sparkles size={24} />
                </div>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '24px', fontWeight: 600, color: 'var(--color-ink-900)', marginBottom: '8px' }}>
                  LegalChat Consultation Ready
                </h2>
                <p style={{ fontSize: '13.5px', lineHeight: 1.6, color: '#475569', marginBottom: '28px', maxWidth: '580px', margin: '0 auto 28px auto' }}>
                  Professional intelligence for Indian legal practice: exact statutory research (BNS, BNSS, BSA, CPC), case analysis, evidentiary evaluation, and structured court pleadings.
                </p>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-text-muted)' }}>
                    {dynamicSuggestions.heading}
                  </span>
                  <span style={{ fontSize: '10px', fontWeight: 600, padding: '2px 8px', borderRadius: '6px', backgroundColor: 'var(--color-bg-surface-sunken)', color: 'var(--color-text-muted)' }}>
                    {dynamicSuggestions.badge}
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', textAlign: 'left' }}>
                  {dynamicSuggestions.items.map((item, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSendMessage(item.query)}
                      style={{
                        padding: '12px 14px',
                        backgroundColor: 'var(--color-bg-surface)',
                        border: '1px solid var(--color-border-subtle)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '12px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                        textAlign: 'left',
                        boxShadow: 'var(--elevation-0)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = 'var(--color-accent-500)';
                        e.currentTarget.style.backgroundColor = 'var(--color-bg-surface-raised)';
                        e.currentTarget.style.transform = 'translateY(-1px)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = 'var(--color-border-subtle)';
                        e.currentTarget.style.backgroundColor = 'var(--color-bg-surface)';
                        e.currentTarget.style.transform = 'translateY(0)';
                      }}
                    >
                      <span style={{ fontSize: '18px', marginTop: '1px' }}>{item.icon}</span>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <span style={{ fontSize: '12.5px', fontWeight: 600, color: 'var(--color-ink-900)' }}>
                          {item.title}
                        </span>
                        <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
                          {item.desc}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {activeMessages.map((msg) => {
              const isLawyer = msg.role === 'user';

              return (
                <div
                  key={msg.id}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignSelf: isLawyer ? 'flex-end' : 'flex-start',
                    maxWidth: isLawyer ? '80%' : '100%',
                    width: isLawyer ? 'auto' : '100%'
                  }}
                >
                  {isLawyer ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                      <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 500, marginBottom: '4px', paddingRight: '4px' }}>
                        You • {msg.timestamp || 'Just now'}
                      </div>
                      <div
                        style={{
                          backgroundColor: 'var(--color-ai-500)',
                          color: '#FFFFFF',
                          borderRadius: '18px 18px 4px 18px',
                          padding: '12px 18px',
                          boxShadow: 'var(--elevation-1)',
                          fontFamily: 'var(--font-sans)',
                          fontSize: '14px',
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
                        border: '1px solid var(--color-border-subtle)',
                        borderRadius: '16px',
                        padding: '20px 24px',
                        boxShadow: 'var(--elevation-1)',
                        position: 'relative',
                        width: '100%'
                      }}
                    >
                      <LegalAnswerRenderer message={msg} isStreaming={false} />

                      {/* Lawyer Suggestion Chips: Dynamically tailored to the generated response */}
                      {(() => {
                        const dynamicS = deriveDynamicSuggestions(msg);
                        const hasMismatchedStatic = (msg.suggestions || []).some(s => 
                          s.label === 'Check punishment' && (msg.content.includes('Sakshya') || msg.content.includes('Contract') || msg.content.includes('Specific Relief') || msg.content.includes('Civil') || msg.content.includes('Arbitration') || msg.content.includes('BSA'))
                        );
                        const effectiveSuggestions = (msg.suggestions && msg.suggestions.length > 0 && !hasMismatchedStatic)
                          ? msg.suggestions
                          : dynamicS;

                        if (!effectiveSuggestions || effectiveSuggestions.length === 0) return null;

                        return (
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              flexWrap: 'wrap',
                              gap: '10px',
                              marginTop: '14px',
                              paddingTop: '12px',
                              borderTop: '1px solid var(--color-border-subtle)'
                            }}
                          >
                            {/* Suggestions list on the left */}
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', flex: 1, minWidth: 0 }}>
                              {effectiveSuggestions.map((sugg, sIdx) => (
                                <button
                                  key={`sugg-${sIdx}`}
                                  id={`suggestion-chip-${msg.id}-${sIdx}`}
                                  type="button"
                                  onClick={() => handleSendMessage(sugg.query || sugg.label)}
                                  disabled={isGenerating}
                                  title={sugg.query || sugg.label}
                                  style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    padding: '6px 14px',
                                    fontSize: '12px',
                                    fontWeight: 500,
                                    color: 'var(--color-accent-700)',
                                    backgroundColor: 'var(--color-accent-100)',
                                    border: '1px solid var(--color-border-subtle)',
                                    borderRadius: '18px',
                                    cursor: isGenerating ? 'not-allowed' : 'pointer',
                                    transition: 'all 0.15s ease',
                                    opacity: isGenerating ? 0.6 : 1
                                  }}
                                  onMouseEnter={(e) => {
                                    if (!isGenerating) {
                                      e.currentTarget.style.backgroundColor = 'var(--color-bg-surface-raised)';
                                      e.currentTarget.style.borderColor = 'var(--color-accent-500)';
                                    }
                                  }}
                                  onMouseLeave={(e) => {
                                    if (!isGenerating) {
                                      e.currentTarget.style.backgroundColor = 'var(--color-accent-100)';
                                      e.currentTarget.style.borderColor = 'var(--color-border-subtle)';
                                    }
                                  }}
                                >
                                  <span style={{ fontSize: '12px' }}>💡</span>
                                  <span>{sugg.label}</span>
                                </button>
                              ))}
                            </div>

                            {/* Copy Response Button on the Right Side */}
                            <button
                              type="button"
                              onClick={() => {
                                const clean = (msg.content || '').replace(/\*\*/g, '').replace(/###\s*/g, '');
                                navigator.clipboard.writeText(clean);
                                setCopiedMsgId(msg.id);
                                setTimeout(() => setCopiedMsgId(null), 2000);
                              }}
                              title="Copy synthesized response"
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '5px',
                                padding: '5px 11px',
                                borderRadius: 'var(--radius-sm, 6px)',
                                backgroundColor: copiedMsgId === msg.id ? 'var(--color-success-wash)' : 'var(--color-bg-surface-raised, #f8fafc)',
                                border: copiedMsgId === msg.id ? '1px solid var(--color-success-border)' : '1px solid var(--color-border-subtle)',
                                color: copiedMsgId === msg.id ? 'var(--color-success-text)' : 'var(--color-text-secondary)',
                                fontSize: '11.5px',
                                fontWeight: 500,
                                cursor: 'pointer',
                                transition: 'all 0.15s ease',
                                flexShrink: 0
                              }}
                              onMouseEnter={(e) => {
                                if (copiedMsgId !== msg.id) {
                                  e.currentTarget.style.backgroundColor = 'var(--color-bg-subtle, #f1f5f9)';
                                  e.currentTarget.style.color = 'var(--color-text-primary)';
                                }
                              }}
                              onMouseLeave={(e) => {
                                if (copiedMsgId !== msg.id) {
                                  e.currentTarget.style.backgroundColor = 'var(--color-bg-surface-raised, #f8fafc)';
                                  e.currentTarget.style.color = 'var(--color-text-secondary)';
                                }
                              }}
                            >
                              {copiedMsgId === msg.id ? <Check size={13} /> : <Copy size={13} />}
                              <span>{copiedMsgId === msg.id ? 'Copied' : 'Copy Response'}</span>
                            </button>
                          </div>
                        );
                      })()}
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
                  width: '100%',
                  animation: 'fadeIn 0.2s ease-in-out'
                }}
              >
                <div
                  style={{
                    backgroundColor: 'var(--color-bg-surface)',
                    border: '1px solid var(--color-border-subtle)',
                    borderRadius: '16px',
                    padding: '14px 20px',
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
                      border: '2px solid var(--color-border-default)',
                      borderTopColor: 'var(--color-accent-500)',
                      animation: 'spin 0.9s linear infinite',
                      flexShrink: 0
                    }}
                  />
                  <span style={{ fontSize: '13px', color: 'var(--color-text-primary)', fontWeight: 500, fontFamily: 'var(--font-sans)' }}>
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
                  width: '100%'
                }}
              >
                <div
                  style={{
                    backgroundColor: 'var(--color-bg-surface)',
                    border: '1px solid var(--color-border-subtle)',
                    borderRadius: '16px',
                    padding: '20px 24px',
                    boxShadow: 'var(--elevation-1)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px', opacity: 0.85, fontSize: '11px', color: 'var(--color-accent-700)', fontWeight: 500 }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', border: '1.5px solid var(--color-border-default)', borderTopColor: 'var(--color-accent-700)', animation: 'spin 0.9s linear infinite', flexShrink: 0 }} />
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
        </div>

        {/* Selected-Text Contextual Ask AI Floating Popup Hook (§15.7) */}
        <SelectedTextAskAI
          containerRef={chatContainerRef}
          activeConversationTitle={activeConv?.title || "Case Inquiry"}
          onOpenInMainChat={handleBridgeSelectedTextToMain}
          onAskFollowUp={aiService.askContextualAI}
        />

        {/* 3. Centered Modern Input Pill Bar */}
        <form
          onSubmit={handleSendMessage}
          style={{
            flexShrink: 0,
            padding: '12px 20px 18px 20px',
            backgroundColor: 'var(--color-bg-surface)',
            borderTop: '1px solid var(--color-border-subtle)',
            display: 'flex',
            justifyContent: 'center',
            width: '100%'
          }}
        >
          <div
            style={{
              maxWidth: '960px',
              width: '100%',
              display: 'flex',
              alignItems: 'flex-end',
              gap: '10px',
              backgroundColor: 'var(--color-bg-surface-sunken)',
              border: '1.5px solid var(--color-border-default)',
              borderRadius: '24px',
              padding: '8px 12px 8px 18px',
              boxShadow: 'var(--elevation-1)',
              transition: 'border-color 0.15s ease'
            }}
          >
            <textarea
              rows={1}
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  e.stopPropagation();
                  handleSendMessage();
                }
              }}
              placeholder="Ask about this matter, research a legal statute, or draft a petition… (Enter to send, Shift+Enter for newline)"
              style={{
                flex: 1,
                border: 'none',
                outline: 'none',
                resize: 'none',
                maxHeight: '120px',
                fontSize: '14px',
                lineHeight: '1.5',
                backgroundColor: 'transparent',
                padding: '4px 0',
                color: 'var(--color-text-primary)'
              }}
            />

            {/* Send / Stop Button per §15.3 (never both visible at once) */}
            {isGenerating ? (
              <button
                type="button"
                onClick={handleStopGeneration}
                title="Stop generation"
                style={{
                  width: '34px',
                  height: '34px',
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
                  width: '34px',
                  height: '34px',
                  borderRadius: '50%',
                  border: 'none',
                  backgroundColor: inputQuery.trim() ? 'var(--color-accent-700)' : 'var(--color-bg-surface-raised)',
                  color: inputQuery.trim() ? '#ffffff' : 'var(--color-text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: inputQuery.trim() ? 'pointer' : 'not-allowed',
                  flexShrink: 0,
                  transition: 'all 0.15s ease'
                }}
              >
                <Send size={15} />
              </button>
            )}
          </div>
        </form>

      </main>

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
