import React, { useState, useEffect, useRef } from 'react';
import { 
  Scale, 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Maximize2, 
  Minimize2, 
  AlertTriangle, 
  CheckCircle2, 
  Award, 
  ShieldAlert, 
  FileText, 
  ChevronRight, 
  Send, 
  RotateCcw, 
  Gavel, 
  UserCheck, 
  Radio,
  BookOpen,
  ArrowRight,
  Sparkles,
  Info,
  Play,
  Download,
  Filter,
  Activity,
  Bookmark,
  Plus,
  Compass,
  Check,
  HelpCircle,
  FolderOpen,
  Sun,
  Moon,
  ChevronDown,
  ChevronUp,
  Sliders,
  ExternalLink,
  Edit3
} from 'lucide-react';

const API_BASE = 'http://' + window.location.hostname + ':8008';

// Phonetic and Domain Auto-Correction for Indian Courtroom Speech
const normalizeSpeech = (text) => {
  if (!text) return "";
  let s = text;
  // Case & party names
  s = s.replace(/\b(madness|martin is|martinez's|martynis|martine)\b/gi, "Martinez");
  s = s.replace(/\b(coastal holding|costal holdings|coastal holding ltd)\b/gi, "Coastal Holdings Ltd.");
  s = s.replace(/\b(whit field|white field|witfield)\b/gi, "Whitfield");
  s = s.replace(/\b(apex logistic|apex logistics)\b/gi, "Apex Logistics Corp.");
  s = s.replace(/\b(harish salvi|harish salve's|advocate salve)\b/gi, "Sr. Adv. Harish Salve");
  s = s.replace(/\b(rekha bali|justice bali|justice rekha)\b/gi, "Justice Rekha Palli");
  s = s.replace(/\b(vikram rathod|inspector rathod)\b/gi, "Inspector Vikram Rathore");
  // Statutes & Codes
  s = s.replace(/\b(b\s*n\s*s\s*s|beanies|b\s*n\s*s\s*s\s*act|be an ass)\b/gi, "BNSS");
  s = s.replace(/\b(b\s*n\s*s|bns act)\b/gi, "BNS");
  s = s.replace(/\b(b\s*s\s*a|bsa act)\b/gi, "BSA");
  s = s.replace(/\b(c\s*r\s*p\s*c|cr pc|crpc act)\b/gi, "CrPC");
  s = s.replace(/\b(c\s*p\s*c|c pc|sea pc)\b/gi, "CPC");
  s = s.replace(/\b(n\s*d\s*p\s*s|ndps act)\b/gi, "NDPS Act");
  // Courtroom terms
  s = s.replace(/\b(station dairy|general dairy|station daily)\b/gi, "Station Diary");
  s = s.replace(/\b(caesar memo|seizer memo|cease memo|sizer memo)\b/gi, "Seizure Memo");
  s = s.replace(/\b(punch witness|panch witness|punch nama|panchanama)\b/gi, "Panch Witness");
  s = s.replace(/\b(cfsl report|c f s l report)\b/gi, "CFSL Report");
  s = s.replace(/\b(order thirty nine|order 39|o 39)\b/gi, "Order 39");
  s = s.replace(/\b(rule one and two|rules 1 and 2|rule 1 and 2)\b/gi, "Rules 1 & 2");
  s = s.replace(/\b(section four eighty|section 480|sec 480)\b/gi, "Section 480");
  s = s.replace(/\b(section nine|section 9|sec 9)\b/gi, "Section 9");
  s = s.replace(/\b(my lourd|m'lud|milord|your honour)\b/gi, "My Lord");
  return s;
};

export const CourtroomSimulationView = ({ 
  globalTheme = 'light',
  onNavigate,
  onStartAIChat
}) => {
  // Case & Session State
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [sessionMode, setSessionMode] = useState('WITNESS_EXAMINATION'); // WITNESS_EXAMINATION | SUBMISSIONS_ARGUMENT | BAIL_HEARING
  const [selectedWitness, setSelectedWitness] = useState(null);
  const [witnessComposure, setWitnessComposure] = useState(85);
  const [sessionId] = useState(() => 'court-' + Math.random().toString(36).substring(2, 9));

  // Chat & Transcript State
  const [transcript, setTranscript] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Active Speakers & Animations
  const [activeSpeaker, setActiveSpeaker] = useState(null); // 'JUDGE' | 'OPPONENT' | 'WITNESS' | 'ADVOCATE' | null
  const [currentObjection, setCurrentObjection] = useState(null);
  const [judgeRuling, setJudgeRuling] = useState(null);

  // Audio Pipeline (STT & TTS)
  const [isListening, setIsListening] = useState(false);
  const [isTTSMuted, setIsTTSMuted] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const recognitionRef = useRef(null);

  // Theme Management (Light mode by default, independent toggle, syncs with global dark mode)
  const [pageTheme, setPageTheme] = useState(() => (globalTheme === 'dark' ? 'dark' : 'light'));
  useEffect(() => {
    if (globalTheme === 'dark') {
      setPageTheme('dark');
    }
  }, [globalTheme]);
  const isDark = pageTheme === 'dark';

  // Full-screen Permission Modal State (Always prompts on arrival if not fullscreen)
  const [showFullscreenPrompt, setShowFullscreenPrompt] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Collapsible Secondary Header Tray (Dropdown Header)
  const [isHeaderTrayOpen, setIsHeaderTrayOpen] = useState(false);

  // Case Notes & Arguments Drawer State
  const [showNotesDrawer, setShowNotesDrawer] = useState(false);
  const [newNoteText, setNewNoteText] = useState('');
  const [newNoteCategory, setNewNoteCategory] = useState('Litigation Strategy');
  const [isSavingNote, setIsSavingNote] = useState(false);

  // Exhibits & Scorecard Modals
  const [showScorecard, setShowScorecard] = useState(false);
  const [scorecardData, setScorecardData] = useState(null);
  const [showExhibitDrawer, setShowExhibitDrawer] = useState(false);
  const [showInstantTips, setShowInstantTips] = useState(false);

  const containerRef = useRef(null);
  const transcriptEndRef = useRef(null);
  const inputRef = useRef(null);
  const speechQueueRef = useRef([]);
  const isSpeakingRef = useRef(false);
  const speechBaseTextRef = useRef('');

  // Initialize Cases from API & Trigger Fullscreen Permission Prompt
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/courtroom/cases`)
      .then(r => r.json())
      .then(data => {
        if (data.cases && data.cases.length > 0) {
          setCases(data.cases);
          const initialCase = data.cases[0];
          setSelectedCase(initialCase);
          if (initialCase.witnesses && initialCase.witnesses.length > 0) {
            setSelectedWitness(initialCase.witnesses[0]);
            setWitnessComposure(initialCase.witnesses[0].default_composure || 85);
          }
        }
      })
      .catch(err => {
        console.error("Failed to load courtroom cases:", err);
      });

    // Prompt for full-screen permission whenever entering this view if not already fullscreen
    if (!document.fullscreenElement) {
      setShowFullscreenPrompt(true);
    }
  }, []);

  // Monitor fullscreen change events
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Web Speech API STT Setup (Real-Time Voice Handling & Interruption)
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSpeechSupported(true);
      const recog = new SpeechRecognition();
      recog.continuous = true;
      recog.interimResults = true;
      recog.lang = 'en-IN';

      // ChatGPT-style voice interruption: stop AI speech when user begins speaking
      recog.onspeechstart = () => {
        stopAllSpeech();
      };

      recog.onresult = (event) => {
        // Immediate interruption of any ongoing AI TTS
        stopAllSpeech();

        let interim = '';
        let final = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        const rawCombined = (speechBaseTextRef.current + ' ' + final + ' ' + interim).trim();
        const corrected = normalizeSpeech(rawCombined);
        setInputText(corrected);

        if (final) {
          speechBaseTextRef.current = normalizeSpeech((speechBaseTextRef.current + ' ' + final).trim());
        }

        // Maintain cursor focus in type box at the end
        if (inputRef.current) {
          inputRef.current.focus();
          const len = corrected.length;
          inputRef.current.setSelectionRange(len, len);
        }
      };

      recog.onerror = (e) => {
        console.warn('Speech recognition error:', e.error);
        setIsListening(false);
      };

      recog.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recog;
    }
  }, []);

  // Auto-scroll transcript
  useEffect(() => {
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [transcript]);

  // Request Fullscreen Handler with Permission
  const handleAcceptFullscreen = () => {
    setShowFullscreenPrompt(false);
    if (!document.fullscreenElement && containerRef.current) {
      containerRef.current.requestFullscreen().catch(err => {
        console.warn("Fullscreen request error:", err);
      });
      setIsFullscreen(true);
    }
  };

  const handleDeclineFullscreen = () => {
    setShowFullscreenPrompt(false);
  };

  // Toggle Fullscreen manually
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen().catch(err => console.error(err));
      setIsFullscreen(true);
    } else {
      document.exitFullscreen().catch(err => console.error(err));
      setIsFullscreen(false);
    }
  };

  // Stop any active speech immediately (ChatGPT-like interruption)
  const stopAllSpeech = () => {
    speechQueueRef.current = [];
    isSpeakingRef.current = false;
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setActiveSpeaker(null);
  };

  // Play events one after another without collision (Sequential Speech Queue)
  const playEventQueue = async (events) => {
    if (isTTSMuted || !window.speechSynthesis || !events || events.length === 0) return;

    // Interrupt any ongoing speech
    stopAllSpeech();
    speechQueueRef.current = [...events];
    isSpeakingRef.current = true;

    for (let i = 0; i < events.length; i++) {
      if (!isSpeakingRef.current) break;

      const ev = events[i];
      if (!ev.text) continue;

      await new Promise((resolve) => {
        const utterance = new SpeechSynthesisUtterance(ev.text);
        const voices = window.speechSynthesis.getVoices();

        if (ev.speaker === 'JUDGE') {
          utterance.pitch = 0.88;
          utterance.rate = 0.95;
          const maleVoice = voices.find(v => v.lang.includes('en') && (v.name.includes('Male') || v.name.includes('David') || v.name.includes('Guy')));
          if (maleVoice) utterance.voice = maleVoice;
        } else if (ev.speaker === 'OPPONENT') {
          utterance.pitch = 1.05;
          utterance.rate = 1.05;
          const sharpVoice = voices.find(v => v.lang.includes('en') && (v.name.includes('George') || v.name.includes('Mark')));
          if (sharpVoice) utterance.voice = sharpVoice;
        } else if (ev.speaker === 'WITNESS') {
          const comp = witnessComposure;
          utterance.pitch = comp < 40 ? 1.15 : 0.98;
          utterance.rate = comp < 40 ? 0.90 : 1.0;
        }

        utterance.onstart = () => {
          setActiveSpeaker(ev.speaker);
        };

        utterance.onend = () => {
          setActiveSpeaker(null);
          // 400ms natural courtroom breath pause between speakers
          setTimeout(resolve, 400);
        };

        utterance.onerror = () => {
          setActiveSpeaker(null);
          resolve();
        };

        window.speechSynthesis.speak(utterance);
      });
    }

    isSpeakingRef.current = false;
  };

  // Toggle Microphone with Cursor Focus Preservation
  const toggleListening = (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!recognitionRef.current) {
      alert("Speech recognition is not supported in this browser. You can type your submissions directly.");
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      // User starts voice mode -> immediately silence AI speech
      stopAllSpeech();
      speechBaseTextRef.current = inputText;
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.warn("Could not start speech recognition:", err);
      }
    }

    // Keep cursor and focus in type box
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
        const len = inputRef.current.value.length;
        inputRef.current.setSelectionRange(len, len);
      }
    }, 50);
  };

  // Case Change Handler
  const handleCaseChange = (caseId) => {
    const c = cases.find(item => item.id === caseId);
    if (c) {
      setSelectedCase(c);
      if (c.witnesses && c.witnesses.length > 0) {
        setSelectedWitness(c.witnesses[0]);
        setWitnessComposure(c.witnesses[0].default_composure || 85);
      }
      setTranscript([]);
      setCurrentObjection(null);
      setJudgeRuling(null);
    }
  };

  // Insert Note or Argument Point into input box
  const handleSelectNoteForArgument = (noteText) => {
    setInputText(noteText);
    setShowNotesDrawer(false);
  };

  // Save Custom Note for Active Case
  const handleSaveCustomNote = async () => {
    if (!newNoteText.trim() || !selectedCase || isSavingNote) return;
    setIsSavingNote(true);

    try {
      const resp = await fetch(`${API_BASE}/api/v1/courtroom/cases/${selectedCase.id}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          note: newNoteText.trim(),
          category: newNoteCategory
        })
      });
      const data = await resp.json();
      if (data.ok && data.note) {
        const updatedCases = cases.map(c => {
          if (c.id === selectedCase.id) {
            const currentNotes = c.case_notes || [];
            return { ...c, case_notes: [data.note, ...currentNotes] };
          }
          return c;
        });
        setCases(updatedCases);
        setSelectedCase(prev => ({
          ...prev,
          case_notes: [data.note, ...(prev.case_notes || [])]
        }));
        setNewNoteText('');
      }
    } catch (err) {
      console.error("Failed to save note:", err);
    } finally {
      setIsSavingNote(false);
    }
  };

  // Submit Oral Point / Question (Sequential Speech & Intent-Driven Arbiter)
  const handleSendTurn = async (customInput = null) => {
    const rawSubmission = (customInput || inputText).trim();
    if (!rawSubmission || isLoading) return;

    // Apply speech normalizer to the submission text
    const submission = normalizeSpeech(rawSubmission);

    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
    stopAllSpeech();
    speechBaseTextRef.current = '';

    setInputText('');
    setIsLoading(true);

    const userTurn = {
      id: Date.now(),
      speaker: 'ADVOCATE',
      text: submission,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    };
    setTranscript(prev => [...prev, userTurn]);

    try {
      const resp = await fetch(`${API_BASE}/api/v1/courtroom/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          case_id: selectedCase?.id || '2024-CV-1187',
          mode: sessionMode,
          advocate_input: submission,
          witness_name: selectedWitness?.name || 'Witness in the Box',
          witness_composure: witnessComposure,
          conversation_history: transcript.map(t => ({
            role: t.speaker === 'ADVOCATE' ? 'user' : 'assistant',
            content: `${t.speaker}: ${t.text}`
          }))
        })
      });

      const data = await resp.json();

      // Handle Blunder Alert / Decorum Penalty
      if (data.score_delta && data.score_delta < 0) {
        setCurrentObjection({
          reason: `Factual / Decorum Blunder (${data.score_delta} Marks Penalty)`
        });
        setTimeout(() => setCurrentObjection(null), 5000);
      } else {
        setCurrentObjection(null);
      }

      // Update Witness State
      if (data.witness_state) {
        setWitnessComposure(data.witness_state.composure);
      }

      // Handle Events and Sequential Audio Queue
      if (data.events && Array.isArray(data.events) && data.events.length > 0) {
        const newTurns = data.events.map((ev, idx) => ({
          id: Date.now() + idx + 1,
          speaker: ev.speaker,
          speaker_name: ev.speaker_name,
          text: ev.text,
          badge: ev.badge,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        }));

        setTranscript(prev => [...prev, ...newTurns]);

        // Sequential Speech Queue (Strictly waits for Speaker 1 to finish before Speaker 2 speaks)
        playEventQueue(data.events);
      }
    } catch (err) {
      console.error("Courtroom turn error:", err);
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 80);
    }
  };

  // Conclude Session & Generate Scorecard
  const handleConcludeSession = async () => {
    setIsLoading(true);
    try {
      const advocateTurns = transcript
        .filter(t => t.speaker === 'ADVOCATE')
        .map(t => ({ advocate_text: t.text }));

      const resp = await fetch(`${API_BASE}/api/v1/courtroom/scorecard`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_history: advocateTurns,
          case_title: selectedCase?.title || "Indian Legal Trial"
        })
      });
      const data = await resp.json();
      if (data.ok) {
        setScorecardData(data.scorecard);
        setShowScorecard(true);
      }
    } catch (err) {
      console.error("Scorecard evaluation error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Reset Session
  const handleResetSession = () => {
    setTranscript([]);
    setCurrentObjection(null);
    setJudgeRuling(null);
    if (selectedWitness) {
      setWitnessComposure(selectedWitness.default_composure || 85);
    }
    setShowScorecard(false);
  };

  // Exhibit Insertion
  const handleConfrontExhibit = (ex) => {
    setInputText(`Officer, I direct your attention to ${ex.id} (${ex.title}). How do you explain the direct contradiction between this record and your oral testimony?`);
    setShowExhibitDrawer(false);
  };

  // Navigate to AI Assistant with Pre-populated Trial Review Prompt
  const handleNavigateToAIAssistant = () => {
    if (!scorecardData) return;

    const weakPoints = (scorecardData.improvements || []).map((im, i) => `${i + 1}. ${im}`).join('\n');
    const aiPrompt = `In my moot trial hearing on "${selectedCase?.title || 'Our Case'}", the Bench gave a score of ${scorecardData.overall_score}/100 with the verdict "${scorecardData.bench_verdict}".\n\nThe Bench highlighted these specific tactical weaknesses:\n${weakPoints}\n\nPlease analyze these points and draft 3 persuasive counter-arguments with statutory citations under the Bharatiya Sakshya Adhiniyam, 2023, BNSS 2023, and relevant Supreme Court precedents to overcome the Bench's skepticism.`;

    if (onStartAIChat) {
      onStartAIChat(aiPrompt);
    } else if (onNavigate) {
      sessionStorage.setItem('courtroom_ai_prompt', aiPrompt);
      onNavigate('ai');
    }
    setShowScorecard(false);
  };

  // Navigate to Drafting Studio
  const handleNavigateToDrafting = () => {
    if (onNavigate) {
      onNavigate('drafting');
    }
    setShowScorecard(false);
  };

  // Audio Waveform Bar Component
  const AudioWave = ({ color = '#2563EB' }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '3px', height: '16px' }}>
      <span style={{ width: '3px', height: '14px', backgroundColor: color, borderRadius: '2px', animation: 'wave 0.8s ease-in-out infinite' }} />
      <span style={{ width: '3px', height: '9px', backgroundColor: color, borderRadius: '2px', animation: 'wave 0.8s ease-in-out 0.2s infinite' }} />
      <span style={{ width: '3px', height: '16px', backgroundColor: color, borderRadius: '2px', animation: 'wave 0.8s ease-in-out 0.4s infinite' }} />
      <span style={{ width: '3px', height: '7px', backgroundColor: color, borderRadius: '2px', animation: 'wave 0.8s ease-in-out 0.1s infinite' }} />
    </div>
  );

  // Dynamic Theme Palette
  const theme = isDark ? {
    bgCanvas: '#0B0F17',
    bgCard: '#131B2A',
    bgCardSubtle: 'rgba(15, 23, 42, 0.85)',
    borderDefault: '#1E293B',
    borderActive: '#3B82F6',
    borderJudge: 'rgba(217, 119, 6, 0.45)',
    borderOpp: 'rgba(239, 68, 68, 0.35)',
    borderWit: 'rgba(59, 130, 246, 0.35)',
    textPrimary: '#F8FAFC',
    textSecondary: '#94A3B8',
    textMuted: '#64748B',
    headerBg: '#101622',
    inputBg: '#090D14',
    stenoBg: '#0D131F',
    stenoHeader: '#121A2B',
    benchDais: 'linear-gradient(180deg, #1A2334 0%, #121927 100%)',
    shadowCard: '0 4px 16px rgba(0,0,0,0.4)',
  } : {
    bgCanvas: '#F8FAFC',
    bgCard: '#FFFFFF',
    bgCardSubtle: '#F1F5F9',
    borderDefault: '#E2E8F0',
    borderActive: '#2563EB',
    borderJudge: 'rgba(217, 119, 6, 0.35)',
    borderOpp: 'rgba(220, 38, 38, 0.25)',
    borderWit: 'rgba(37, 99, 235, 0.25)',
    textPrimary: '#0F172A',
    textSecondary: '#475569',
    textMuted: '#64748B',
    headerBg: '#FFFFFF',
    inputBg: '#FFFFFF',
    stenoBg: '#F8FAFC',
    stenoHeader: '#F1F5F9',
    benchDais: 'linear-gradient(180deg, #FFFDF8 0%, #FDFBF7 100%)',
    shadowCard: '0 2px 10px rgba(15, 23, 42, 0.05)',
  };

  return (
    <div 
      ref={containerRef}
      style={{
        width: '100%',
        height: isFullscreen ? '100vh' : 'calc(100vh - 60px)',
        backgroundColor: theme.bgCanvas,
        color: theme.textPrimary,
        display: 'flex',
        flexDirection: 'column',
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        overflow: 'hidden',
        position: 'relative',
        transition: 'background-color 0.2s ease, color 0.2s ease'
      }}
    >
      <style>{`
        @keyframes wave {
          0%, 100% { transform: scaleY(0.35); }
          50% { transform: scaleY(1.3); }
        }
        @keyframes pulseGlow {
          0%, 100% { box-shadow: 0 0 15px rgba(217, 119, 6, 0.4); }
          50% { box-shadow: 0 0 35px rgba(217, 119, 6, 0.8); }
        }
        @keyframes micPulse {
          0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
          70% { box-shadow: 0 0 0 16px rgba(239, 68, 68, 0); }
          100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
      `}</style>

      {/* 1. SLIM EXECUTIVE COURTROOM HEADER (Clean & Uncluttered) */}
      <header
        style={{
          height: '48px',
          borderBottom: `1px solid ${theme.borderDefault}`,
          backgroundColor: theme.headerBg,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 18px',
          boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
          zIndex: 20,
          flexShrink: 0
        }}
      >
        {/* Left: Court Badge & Case Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: isDark ? 'rgba(217, 119, 6, 0.15)' : '#FEF3C7',
            border: isDark ? '1px solid rgba(217, 119, 6, 0.4)' : '1px solid #FDE68A',
            padding: '4px 10px',
            borderRadius: '16px'
          }}>
            <Scale size={14} color="#D97706" />
            <span style={{ fontSize: '10.5px', fontWeight: 800, color: '#D97706', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
              Courtroom 01
            </span>
          </div>

          <div style={{ fontWeight: 700, fontSize: '13px', color: theme.textPrimary, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>{selectedCase?.title || 'Martinez v. Coastal Holdings Ltd.'}</span>
            {selectedCase?.stakes && (
              <span style={{ fontSize: '11px', fontWeight: 600, color: '#10B981', backgroundColor: isDark ? 'rgba(16, 185, 129, 0.12)' : '#ECFDF5', padding: '2px 8px', borderRadius: '10px' }}>
                {selectedCase.stakes}
              </span>
            )}
          </div>
        </div>

        {/* Center: Hearing Mode Pills */}
        <div style={{
          display: 'flex',
          backgroundColor: isDark ? '#090D14' : '#F1F5F9',
          borderRadius: '8px',
          padding: '2px',
          border: `1px solid ${theme.borderDefault}`
        }}>
          {[
            { id: 'WITNESS_EXAMINATION', label: 'Witness Cross-Exam', icon: '👤' },
            { id: 'SUBMISSIONS_ARGUMENT', label: 'Oral Arguments', icon: '⚖️' },
            { id: 'BAIL_HEARING', label: 'Bail & Liberty', icon: '🕊️' }
          ].map(m => {
            const isAct = sessionMode === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setSessionMode(m.id)}
                style={{
                  backgroundColor: isAct ? (isDark ? '#2563EB' : '#1E293B') : 'transparent',
                  color: isAct ? '#FFFFFF' : theme.textSecondary,
                  border: 'none',
                  padding: '4px 12px',
                  borderRadius: '6px',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  transition: 'all 0.15s ease'
                }}
              >
                <span>{m.icon}</span>
                <span>{m.label}</span>
              </button>
            );
          })}
        </div>

        {/* Right: Collapsible Header Dropdown Trigger & Key Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Dropdown Header Toggle (User Requested: "make the header of that page to be a dropdown") */}
          <button
            onClick={() => setIsHeaderTrayOpen(!isHeaderTrayOpen)}
            style={{
              backgroundColor: isHeaderTrayOpen ? (isDark ? '#1E293B' : '#E2E8F0') : 'transparent',
              color: isHeaderTrayOpen ? (isDark ? '#F8FAFC' : '#0F172A') : theme.textSecondary,
              border: `1px solid ${theme.borderDefault}`,
              padding: '5px 10px',
              borderRadius: '6px',
              fontSize: '11.5px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}
            title="Expand / Collapse Dossier & Controls"
          >
            <Sliders size={13} />
            <span>Case Controls</span>
            {isHeaderTrayOpen ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>

          {/* In-Page Theme Toggle (Light mode by default, independent toggle) */}
          <button
            onClick={() => setPageTheme(isDark ? 'light' : 'dark')}
            style={{
              backgroundColor: isDark ? '#1E293B' : '#F1F5F9',
              color: isDark ? '#F59E0B' : '#475569',
              border: `1px solid ${theme.borderDefault}`,
              padding: '5px 9px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
              fontWeight: 600
            }}
            title={isDark ? "Switch Courtroom to Light Mode" : "Switch Courtroom to Dark Mode"}
          >
            {isDark ? <Sun size={13} /> : <Moon size={13} />}
            <span>{isDark ? 'Light' : 'Dark'}</span>
          </button>

          {/* Seek Verdict */}
          <button
            onClick={handleConcludeSession}
            disabled={transcript.length === 0}
            style={{
              backgroundColor: transcript.length > 0 ? (isDark ? '#D97706' : '#0F172A') : (isDark ? '#1E293B' : '#E2E8F0'),
              color: transcript.length > 0 ? '#FFFFFF' : (isDark ? '#64748B' : '#94A3B8'),
              border: 'none',
              padding: '5px 12px',
              borderRadius: '6px',
              fontSize: '11.5px',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              cursor: transcript.length > 0 ? 'pointer' : 'not-allowed'
            }}
          >
            <Gavel size={13} />
            <span>Seek Verdict</span>
          </button>

          {/* Fullscreen Button */}
          <button
            onClick={toggleFullscreen}
            style={{
              backgroundColor: 'transparent',
              color: theme.textSecondary,
              border: `1px solid ${theme.borderDefault}`,
              padding: '5px 8px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center'
            }}
            title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen Mode"}
          >
            {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
      </header>

      {/* DROPDOWN EXPANDABLE CONTROL TRAY (When lawyer clicks "Case Controls") */}
      {isHeaderTrayOpen && (
        <div
          style={{
            backgroundColor: isDark ? '#101622' : '#F1F5F9',
            borderBottom: `1px solid ${theme.borderDefault}`,
            padding: '10px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '14px',
            zIndex: 15,
            flexShrink: 0,
            animation: 'fadeIn 0.2s ease'
          }}
        >
          {/* Case Switcher & Court Info */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: theme.textSecondary, textTransform: 'uppercase' }}>
              Switch Matter:
            </span>
            <select
              value={selectedCase?.id || ''}
              onChange={(e) => handleCaseChange(e.target.value)}
              style={{
                backgroundColor: theme.bgCard,
                color: theme.textPrimary,
                border: `1px solid ${theme.borderDefault}`,
                borderRadius: '6px',
                padding: '4px 10px',
                fontSize: '12px',
                fontWeight: 600,
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              {cases.map(c => (
                <option key={c.id} value={c.id}>
                  {c.id}: {c.title} ({c.stakes})
                </option>
              ))}
            </select>
            <span style={{ fontSize: '11.5px', color: theme.textSecondary }}>
              · {selectedCase?.court || 'Commercial Division, High Court'}
            </span>
          </div>

          {/* Quick Tools: Case Notes, Exhibits, Voice Toggle */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {/* Case Notes & Arguments Drawer Button */}
            <button
              onClick={() => {
                setShowNotesDrawer(!showNotesDrawer);
                setShowExhibitDrawer(false);
              }}
              style={{
                backgroundColor: showNotesDrawer ? (isDark ? 'rgba(217, 119, 6, 0.25)' : '#FEF3C7') : theme.bgCard,
                color: showNotesDrawer ? '#D97706' : theme.textPrimary,
                border: `1px solid ${showNotesDrawer ? '#D97706' : theme.borderDefault}`,
                padding: '5px 12px',
                borderRadius: '6px',
                fontSize: '11.5px',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                cursor: 'pointer'
              }}
            >
              <Bookmark size={13} color="#D97706" />
              <span>Case Notes & Arguments ({selectedCase?.case_notes?.length || 0})</span>
            </button>

            {/* Exhibits Button */}
            <button
              onClick={() => {
                setShowExhibitDrawer(!showExhibitDrawer);
                setShowNotesDrawer(false);
              }}
              style={{
                backgroundColor: showExhibitDrawer ? (isDark ? 'rgba(37, 99, 235, 0.25)' : '#EFF6FF') : theme.bgCard,
                color: showExhibitDrawer ? '#2563EB' : theme.textPrimary,
                border: `1px solid ${showExhibitDrawer ? '#2563EB' : theme.borderDefault}`,
                padding: '5px 12px',
                borderRadius: '6px',
                fontSize: '11.5px',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                cursor: 'pointer'
              }}
            >
              <FileText size={13} color="#2563EB" />
              <span>Exhibits ({selectedCase?.exhibits?.length || 0})</span>
            </button>

            {/* Voice Mute Toggle */}
            <button
              onClick={() => setIsTTSMuted(!isTTSMuted)}
              style={{
                backgroundColor: theme.bgCard,
                color: isTTSMuted ? '#EF4444' : '#10B981',
                border: `1px solid ${theme.borderDefault}`,
                padding: '5px 10px',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '11px',
                fontWeight: 600
              }}
              title={isTTSMuted ? "Unmute AI Voice Output" : "Mute AI Voice Output"}
            >
              {isTTSMuted ? <VolumeX size={14} /> : <Volume2 size={14} />}
              <span>{isTTSMuted ? 'Muted' : 'Audio On'}</span>
            </button>
          </div>
        </div>
      )}

      {/* 2. MAIN COURTROOM LAYOUT: BALANCED STAGE (LEFT 70%) + STENOGRAPHER RECORD (RIGHT 30%) */}
      <div style={{ flex: 1, display: 'flex', minHeight: 0, overflow: 'hidden' }}>
        
        {/* === COURTROOM STAGE === */}
        <div 
          style={{
            flex: 7,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            padding: '14px 20px 10px 20px',
            backgroundColor: theme.bgCanvas,
            position: 'relative',
            overflow: 'hidden'
          }}
        >
          {/* OBJECTION FLASH ALERT */}
          {currentObjection && (
            <div
              style={{
                position: 'absolute',
                top: '10px',
                left: '50%',
                transform: 'translateX(-50%)',
                backgroundColor: '#DC2626',
                color: '#FFFFFF',
                padding: '8px 20px',
                borderRadius: '6px',
                boxShadow: '0 4px 20px rgba(220, 38, 38, 0.45)',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                zIndex: 25,
                fontWeight: 700,
                fontSize: '13px'
              }}
            >
              <AlertTriangle size={18} />
              <span>OBJECTION RAISED BY OPPOSING COUNSEL!</span>
              <span style={{ fontSize: '11.5px', fontWeight: 600, backgroundColor: 'rgba(0,0,0,0.25)', padding: '2px 8px', borderRadius: '4px' }}>
                {currentObjection.reason}
              </span>
            </div>
          )}

          {/* --- TOP: COMPACT JUDICIAL BENCH (Clean Dais) --- */}
          <div style={{ display: 'flex', justifyContent: 'center', flexShrink: 0 }}>
            <div
              style={{
                width: '100%',
                maxWidth: '740px',
                background: theme.benchDais,
                border: activeSpeaker === 'JUDGE' ? `2px solid #D97706` : `1px solid ${theme.borderJudge}`,
                borderRadius: '10px',
                padding: '10px 18px',
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                boxShadow: theme.shadowCard,
                position: 'relative',
                transition: 'all 0.2s ease'
              }}
            >
              {/* Crest Badge */}
              <div
                style={{
                  position: 'absolute',
                  top: '-10px',
                  left: '20px',
                  backgroundColor: '#D97706',
                  color: '#FFFFFF',
                  padding: '2px 10px',
                  borderRadius: '10px',
                  fontSize: '9.5px',
                  fontWeight: 800,
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <Gavel size={10} />
                <span>Court Bench</span>
              </div>

              {/* Judge Avatar */}
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '50%',
                  backgroundColor: isDark ? '#1E293B' : '#FEF3C7',
                  border: '1.5px solid #D97706',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '20px',
                  flexShrink: 0
                }}
              >
                ⚖️
              </div>

              {/* Judge Speech Bubble */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontWeight: 800, fontSize: '13.5px', color: theme.textPrimary }}>
                    {selectedCase?.bench || "Hon'ble Presiding Judge"}
                  </div>
                  {activeSpeaker === 'JUDGE' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <AudioWave color="#D97706" />
                      <span style={{ fontSize: '10px', fontWeight: 700, color: '#D97706', textTransform: 'uppercase' }}>
                        Speaking
                      </span>
                    </div>
                  )}
                </div>

                <div style={{
                  marginTop: '4px',
                  backgroundColor: isDark ? 'rgba(9, 13, 20, 0.7)' : '#F8FAFC',
                  border: `1px solid ${theme.borderDefault}`,
                  padding: '6px 12px',
                  borderRadius: '6px',
                  borderLeft: judgeRuling?.type === 'SUSTAINED' 
                    ? '3px solid #EF4444' 
                    : (judgeRuling?.type === 'OVERRULED' ? '3px solid #10B981' : '3px solid #D97706'),
                  fontSize: '13px',
                  color: theme.textPrimary,
                  lineHeight: '1.5',
                  fontStyle: 'italic'
                }}>
                  {judgeRuling ? (
                    <div>
                      <strong style={{ color: judgeRuling.type === 'SUSTAINED' ? '#EF4444' : '#10B981', fontStyle: 'normal' }}>
                        [{judgeRuling.type}]:
                      </strong> {judgeRuling.statement}
                    </div>
                  ) : (
                    transcript.slice().reverse().find(t => t.speaker === 'JUDGE')?.text || 
                    "Bench: 'The Court is seized of the matter. Counsel may proceed with examination or oral submissions.'"
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* --- MIDDLE: BALANCED OPPOSING COUNSEL (LEFT) vs. WITNESS BOX (RIGHT) --- */}
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '16px', margin: '8px 0', flex: 1, minHeight: 0 }}>
            
            {/* OPPOSING COUNSEL LECTERN */}
            <div
              style={{
                flex: 1,
                backgroundColor: theme.bgCard,
                border: activeSpeaker === 'OPPONENT' ? '2px solid #EF4444' : `1px solid ${theme.borderOpp}`,
                borderRadius: '10px',
                padding: '14px',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: theme.shadowCard,
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{
                    width: '34px',
                    height: '34px',
                    borderRadius: '6px',
                    backgroundColor: isDark ? 'rgba(239, 68, 68, 0.15)' : '#FEE2E2',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '18px'
                  }}>
                    👔
                  </div>
                  <div>
                    <div style={{ fontWeight: 800, fontSize: '13px', color: theme.textPrimary }}>
                      {selectedCase?.opposing_counsel || "Opposing Senior Counsel"}
                    </div>
                    <div style={{ fontSize: '10.5px', color: theme.textSecondary }}>
                      Senior Advocate for Respondent
                    </div>
                  </div>
                </div>

                {activeSpeaker === 'OPPONENT' && <AudioWave color="#EF4444" />}
              </div>

              {/* Opponent Statement */}
              <div style={{
                flex: 1,
                backgroundColor: theme.bgCardSubtle,
                border: `1px solid ${theme.borderDefault}`,
                borderRadius: '6px',
                padding: '10px 12px',
                fontSize: '13px',
                color: theme.textPrimary,
                lineHeight: '1.5',
                overflowY: 'auto'
              }}>
                <div style={{ fontSize: '10px', color: '#EF4444', fontWeight: 800, textTransform: 'uppercase', marginBottom: '4px' }}>
                  {activeSpeaker === 'OPPONENT' ? '⚡ Arguing Rebuttal' : 'Adversarial Strategy'}
                </div>
                <div>
                  {transcript.slice().reverse().find(t => t.speaker === 'OPPONENT')?.text || 
                    "Counsel for Respondent is prepared to raise evidentiary objections under Bharatiya Sakshya Adhiniyam, 2023."}
                </div>
              </div>
            </div>

            {/* WITNESS STAND / KATGHARA */}
            <div
              style={{
                flex: 1,
                backgroundColor: theme.bgCard,
                border: activeSpeaker === 'WITNESS' ? '2px solid #2563EB' : `1px solid ${theme.borderWit}`,
                borderRadius: '10px',
                padding: '14px',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: theme.shadowCard,
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{
                    width: '34px',
                    height: '34px',
                    borderRadius: '6px',
                    backgroundColor: isDark ? 'rgba(37, 99, 235, 0.15)' : '#EFF6FF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '18px'
                  }}>
                    👤
                  </div>
                  <div>
                    <div style={{ fontWeight: 800, fontSize: '13px', color: theme.textPrimary }}>
                      {selectedWitness?.name || "Witness in the Box"}
                    </div>
                    <div style={{ fontSize: '10.5px', color: theme.textSecondary }}>
                      {selectedWitness?.role || "Sworn Deponent"}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {activeSpeaker === 'WITNESS' && <AudioWave color="#2563EB" />}
                  {selectedCase?.witnesses && selectedCase.witnesses.length > 1 && (
                    <select
                      value={selectedWitness?.name || ''}
                      onChange={(e) => {
                        const w = selectedCase.witnesses.find(wit => wit.name === e.target.value);
                        if (w) {
                          setSelectedWitness(w);
                          setWitnessComposure(w.default_composure || 85);
                        }
                      }}
                      style={{
                        backgroundColor: theme.bgCanvas,
                        color: theme.textPrimary,
                        border: `1px solid ${theme.borderDefault}`,
                        borderRadius: '4px',
                        padding: '2px 6px',
                        fontSize: '10.5px',
                        outline: 'none',
                        cursor: 'pointer'
                      }}
                    >
                      {selectedCase.witnesses.map(w => (
                        <option key={w.name} value={w.name}>{w.name}</option>
                      ))}
                    </select>
                  )}
                </div>
              </div>

              {/* Dynamic Composure Meter */}
              <div style={{ marginBottom: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
                  <span style={{ fontSize: '10.5px', color: theme.textSecondary, fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Activity size={12} color={witnessComposure > 65 ? '#10B981' : (witnessComposure > 35 ? '#F59E0B' : '#EF4444')} />
                    <span>Witness Composure & Credibility</span>
                  </span>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: 800,
                    color: witnessComposure > 65 ? '#10B981' : (witnessComposure > 35 ? '#F59E0B' : '#EF4444')
                  }}>
                    {witnessComposure}% {witnessComposure > 65 ? '🛡️ Composed' : (witnessComposure > 35 ? '⚠️ Wavering' : '🚨 Cornered')}
                  </span>
                </div>
                <div style={{ width: '100%', height: '6px', backgroundColor: isDark ? '#090D14' : '#E2E8F0', borderRadius: '3px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${witnessComposure}%`,
                      height: '100%',
                      backgroundColor: witnessComposure > 65 ? '#10B981' : (witnessComposure > 35 ? '#F59E0B' : '#EF4444'),
                      transition: 'width 0.6s ease, background-color 0.6s ease'
                    }}
                  />
                </div>
              </div>

              {/* Witness Deposition Speech Bubble */}
              <div style={{
                flex: 1,
                backgroundColor: theme.bgCardSubtle,
                border: `1px solid ${theme.borderDefault}`,
                borderRadius: '6px',
                padding: '10px 12px',
                fontSize: '13px',
                color: theme.textPrimary,
                lineHeight: '1.5',
                overflowY: 'auto'
              }}>
                <div style={{ fontSize: '10px', color: '#2563EB', fontWeight: 800, textTransform: 'uppercase', marginBottom: '4px' }}>
                  {activeSpeaker === 'WITNESS' ? '🗣️ Deposing under Oath...' : 'Sworn Statement'}
                </div>
                <div>
                  {transcript.slice().reverse().find(t => t.speaker === 'WITNESS')?.text || 
                    "Witness is in the box, sworn under oath. Awaiting Counsel's cross-examination questions."}
                </div>
              </div>
            </div>
          </div>

          {/* --- BOTTOM: ADVOCATE SUBMISSION BAR --- */}
          <div
            style={{
              backgroundColor: theme.bgCard,
              border: isListening ? '2px solid #EF4444' : `1px solid ${theme.borderDefault}`,
              borderRadius: '10px',
              padding: '12px 16px',
              flexShrink: 0,
              boxShadow: theme.shadowCard,
              transition: 'all 0.2s ease'
            }}
          >
            {/* Quick Tactical Question Chips */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontWeight: 800, fontSize: '12.5px', color: theme.textPrimary }}>
                  Advocate at the Bar (You)
                </span>
                <span style={{ fontSize: '11px', color: theme.textSecondary }}>
                  {isListening ? '🔴 Speaking live... (Speech-to-Text active)' : 'Type oral point or speak into microphone'}
                </span>
              </div>

              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  onClick={() => setInputText("Officer, please direct your attention to Exhibit P-4 and explain the 40-minute discrepancy.")}
                  style={{
                    backgroundColor: isDark ? 'rgba(255, 255, 255, 0.06)' : '#F1F5F9',
                    color: theme.textPrimary,
                    border: `1px solid ${theme.borderDefault}`,
                    borderRadius: '4px',
                    padding: '3px 8px',
                    fontSize: '10.5px',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  ⏱️ 40-Min Gap
                </button>
                <button
                  onClick={() => setInputText("My Lord, under Section 480 BNSS, the mandatory conditions are met and personal liberty must be protected.")}
                  style={{
                    backgroundColor: isDark ? 'rgba(255, 255, 255, 0.06)' : '#F1F5F9',
                    color: theme.textPrimary,
                    border: `1px solid ${theme.borderDefault}`,
                    borderRadius: '4px',
                    padding: '3px 8px',
                    fontSize: '10.5px',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  ⚖️ Sec 480 BNSS
                </button>
                <button
                  onClick={() => setInputText("I put it to you that this seizure memo was antedated at the police station and not at the scene.")}
                  style={{
                    backgroundColor: isDark ? 'rgba(255, 255, 255, 0.06)' : '#F1F5F9',
                    color: theme.textPrimary,
                    border: `1px solid ${theme.borderDefault}`,
                    borderRadius: '4px',
                    padding: '3px 8px',
                    fontSize: '10.5px',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  🎯 Antedated Memo
                </button>
              </div>
            </div>

            {/* Input Row */}
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              {/* Continuous Mic Button with Focus Retention */}
              <button
                onMouseDown={(e) => e.preventDefault()}
                onClick={(e) => toggleListening(e)}
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '50%',
                  backgroundColor: isListening ? '#EF4444' : (isDark ? '#2563EB' : '#1E293B'),
                  color: '#FFFFFF',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  flexShrink: 0,
                  boxShadow: isListening ? '0 0 16px rgba(239, 68, 68, 0.7)' : '0 2px 8px rgba(0,0,0,0.15)',
                  animation: isListening ? 'micPulse 1.5s infinite' : 'none',
                  transition: 'all 0.2s ease'
                }}
                title={isListening ? "Mute Microphone" : "Activate Microphone to Speak"}
              >
                {isListening ? <MicOff size={18} /> : <Mic size={18} />}
              </button>

              {/* Text Input with Ref & Cursor Preservation */}
              <div style={{ flex: 1, position: 'relative' }}>
                <input
                  ref={inputRef}
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSendTurn();
                  }}
                  placeholder={
                    isListening 
                      ? "Listening to your voice... (Speak freely)" 
                      : (sessionMode === 'WITNESS_EXAMINATION' 
                          ? "Ask your cross-examination question to the witness in the box..." 
                          : "Advance your oral submission before the Division Bench...")
                  }
                  style={{
                    width: '100%',
                    backgroundColor: theme.inputBg,
                    color: theme.textPrimary,
                    border: `1px solid ${theme.borderDefault}`,
                    borderRadius: '6px',
                    padding: '9px 14px',
                    fontSize: '13px',
                    outline: 'none',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              {/* Submit Turn Button */}
              <button
                onClick={() => handleSendTurn()}
                disabled={!inputText.trim() || isLoading}
                style={{
                  backgroundColor: inputText.trim() && !isLoading ? '#10B981' : (isDark ? '#1E293B' : '#E2E8F0'),
                  color: inputText.trim() && !isLoading ? '#FFFFFF' : theme.textMuted,
                  border: 'none',
                  height: '38px',
                  padding: '0 16px',
                  borderRadius: '6px',
                  fontSize: '12.5px',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  cursor: inputText.trim() && !isLoading ? 'pointer' : 'not-allowed',
                  flexShrink: 0,
                  transition: 'all 0.2s ease'
                }}
              >
                <span>Argue Point</span>
                <Send size={13} />
              </button>
            </div>
          </div>
        </div>

        {/* === RIGHT: COURTROOM STENOGRAPHER MINUTES (30% WIDTH) === */}
        <div
          style={{
            flex: 3,
            backgroundColor: theme.stenoBg,
            borderLeft: `1px solid ${theme.borderDefault}`,
            display: 'flex',
            flexDirection: 'column',
            minHeight: 0,
            overflow: 'hidden'
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '12px 16px',
              borderBottom: `1px solid ${theme.borderDefault}`,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              backgroundColor: theme.stenoHeader,
              flexShrink: 0
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BookOpen size={15} color="#2563EB" />
              <div>
                <div style={{ fontWeight: 800, fontSize: '12.5px', color: theme.textPrimary }}>
                  Official Record of Proceedings
                </div>
                <div style={{ fontSize: '10.5px', color: theme.textSecondary }}>
                  Stenographer Minutes (Live)
                </div>
              </div>
            </div>

            <button
              onClick={handleResetSession}
              style={{
                backgroundColor: 'transparent',
                border: 'none',
                color: theme.textSecondary,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '11px'
              }}
              title="Reset Trial Minutes"
            >
              <RotateCcw size={12} />
              <span>Reset</span>
            </button>
          </div>

          {/* Transcript Log */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '12px 14px',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px'
            }}
          >
            {transcript.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '36px 14px', color: theme.textSecondary }}>
                <Scale size={28} style={{ margin: '0 auto 10px auto', opacity: 0.35 }} />
                <p style={{ margin: 0, fontWeight: 700, fontSize: '12.5px', color: theme.textPrimary }}>The Court is in session.</p>
                <p style={{ margin: '4px 0 0 0', fontSize: '11.5px', lineHeight: '1.45' }}>
                  All oral submissions, witness depositions, objections, and rulings are recorded contemporaneously.
                </p>
              </div>
            ) : (
              transcript.map((item) => {
                const isAdvocate = item.speaker === 'ADVOCATE';
                const isJudge = item.speaker === 'JUDGE';
                const isOpponent = item.speaker === 'OPPONENT';
                const isWitness = item.speaker === 'WITNESS';

                return (
                  <div
                    key={item.id}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      backgroundColor: theme.bgCard,
                      borderLeft: isAdvocate 
                        ? '3px solid #2563EB' 
                        : (isJudge ? '3px solid #D97706' : (isOpponent ? '3px solid #EF4444' : '3px solid #3B82F6')),
                      border: `1px solid ${theme.borderDefault}`,
                      borderLeftWidth: '3px',
                      borderRadius: '6px',
                      padding: '8px 12px',
                      fontSize: '12px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
                      <span style={{
                        fontWeight: 800,
                        fontSize: '10.5px',
                        letterSpacing: '0.04em',
                        color: isAdvocate ? '#2563EB' : (isJudge ? '#D97706' : (isOpponent ? '#EF4444' : '#3B82F6'))
                      }}>
                        {isAdvocate && 'MR. COUNSEL (YOU):'}
                        {isJudge && 'HON\'BLE COURT BENCH:'}
                        {isOpponent && 'SR. ADV. OPPOSING COUNSEL:'}
                        {isWitness && `DEPONENT (${selectedWitness?.name?.split(' ')[0] || 'Witness'}):`}
                      </span>
                      <span style={{ fontSize: '9.5px', color: theme.textMuted }}>{item.timestamp}</span>
                    </div>

                    {item.badge && (
                      <div style={{
                        alignSelf: 'flex-start',
                        fontSize: '9.5px',
                        fontWeight: 700,
                        padding: '1px 6px',
                        borderRadius: '3px',
                        backgroundColor: isDark ? 'rgba(0,0,0,0.35)' : '#F1F5F9',
                        color: theme.textPrimary,
                        marginBottom: '3px'
                      }}>
                        {item.badge}
                      </div>
                    )}

                    <div style={{ color: theme.textPrimary, lineHeight: '1.45' }}>
                      {item.text}
                    </div>
                  </div>
                );
              })
            )}
            <div ref={transcriptEndRef} />
          </div>

          {/* Footer */}
          <div style={{
            padding: '8px 14px',
            borderTop: `1px solid ${theme.borderDefault}`,
            backgroundColor: theme.stenoHeader,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexShrink: 0
          }}>
            <span style={{ fontSize: '10.5px', color: theme.textSecondary }}>
              Recorded Minutes: {transcript.length}
            </span>
            <button
              onClick={handleConcludeSession}
              disabled={transcript.length === 0}
              style={{
                backgroundColor: 'transparent',
                border: 'none',
                color: transcript.length > 0 ? '#2563EB' : theme.textMuted,
                cursor: transcript.length > 0 ? 'pointer' : 'default',
                fontSize: '11px',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <span>Conclude & Score</span>
              <ArrowRight size={11} />
            </button>
          </div>
        </div>
      </div>

      {/* 3. CASE NOTES & ARGUMENTS DRAWER (LAWYER'S NOTEBOOK) */}
      {showNotesDrawer && selectedCase && (
        <div
          style={{
            position: 'absolute',
            top: isHeaderTrayOpen ? '96px' : '48px',
            right: 0,
            width: '440px',
            height: isHeaderTrayOpen ? 'calc(100% - 96px)' : 'calc(100% - 48px)',
            backgroundColor: theme.bgCard,
            borderLeft: `1px solid ${theme.borderDefault}`,
            boxShadow: '-8px 0 30px rgba(0,0,0,0.3)',
            zIndex: 35,
            padding: '18px',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          {/* Drawer Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Bookmark size={16} color="#D97706" />
              <div>
                <div style={{ fontWeight: 800, fontSize: '14px', color: theme.textPrimary }}>
                  Advocate Case Notes & Arguments
                </div>
                <div style={{ fontSize: '11px', color: theme.textSecondary }}>
                  {selectedCase.title}
                </div>
              </div>
            </div>
            <button
              onClick={() => setShowNotesDrawer(false)}
              style={{ background: 'none', border: 'none', color: theme.textSecondary, cursor: 'pointer', fontSize: '18px' }}
            >
              ✕
            </button>
          </div>

          <p style={{ fontSize: '11.5px', color: theme.textSecondary, marginBottom: '12px', lineHeight: '1.45' }}>
            Select any argument point or statutory ground below to instantly place it into your oral submission box.
          </p>

          {/* Quick Add Custom Note Form */}
          <div style={{
            backgroundColor: theme.bgCardSubtle,
            borderRadius: '6px',
            padding: '10px',
            marginBottom: '14px',
            border: `1px solid ${theme.borderDefault}`
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#D97706', textTransform: 'uppercase' }}>
                ✍️ Add Custom Note to Case
              </span>
              <select
                value={newNoteCategory}
                onChange={(e) => setNewNoteCategory(e.target.value)}
                style={{
                  backgroundColor: theme.bgCard,
                  color: theme.textPrimary,
                  border: `1px solid ${theme.borderDefault}`,
                  borderRadius: '4px',
                  padding: '2px 6px',
                  fontSize: '10px'
                }}
              >
                <option value="Litigation Strategy">Litigation Strategy</option>
                <option value="Statutory Grounds">Statutory Grounds</option>
                <option value="Cross-Examination Trap">Cross-Examination Trap</option>
                <option value="Binding Precedent">Binding Precedent</option>
              </select>
            </div>
            <div style={{ display: 'flex', gap: '6px' }}>
              <input
                type="text"
                value={newNoteText}
                onChange={(e) => setNewNoteText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSaveCustomNote();
                }}
                placeholder="Type argument note (e.g. Confront IO on broken seal)..."
                style={{
                  flex: 1,
                  backgroundColor: theme.bgCard,
                  color: theme.textPrimary,
                  border: `1px solid ${theme.borderDefault}`,
                  borderRadius: '5px',
                  padding: '6px 10px',
                  fontSize: '11.5px',
                  outline: 'none'
                }}
              />
              <button
                onClick={handleSaveCustomNote}
                disabled={!newNoteText.trim() || isSavingNote}
                style={{
                  backgroundColor: '#D97706',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '5px',
                  padding: '0 10px',
                  fontSize: '11px',
                  fontWeight: 700,
                  cursor: newNoteText.trim() && !isSavingNote ? 'pointer' : 'not-allowed',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <Plus size={12} />
                <span>Save</span>
              </button>
            </div>
          </div>

          {/* Notes List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1, overflowY: 'auto' }}>
            {(!selectedCase.case_notes || selectedCase.case_notes.length === 0) ? (
              <div style={{ textAlign: 'center', padding: '24px', color: theme.textSecondary, fontSize: '11.5px' }}>
                No argument notes saved for this matter. You can add one above!
              </div>
            ) : (
              selectedCase.case_notes.map((note, idx) => (
                <div
                  key={idx}
                  style={{
                    backgroundColor: theme.bgCardSubtle,
                    border: `1px solid ${theme.borderDefault}`,
                    borderRadius: '6px',
                    padding: '10px 12px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
                    <span style={{
                      fontSize: '9.5px',
                      fontWeight: 800,
                      color: note.category === 'Statutory Grounds' ? '#2563EB' : (note.category === 'Cross-Examination Trap' ? '#EF4444' : '#D97706'),
                      backgroundColor: theme.bgCard,
                      padding: '2px 5px',
                      borderRadius: '3px',
                      textTransform: 'uppercase'
                    }}>
                      {note.category}
                    </span>
                    <button
                      onClick={() => handleSelectNoteForArgument(note.text)}
                      style={{
                        backgroundColor: '#2563EB',
                        color: '#FFFFFF',
                        border: 'none',
                        borderRadius: '4px',
                        padding: '2px 6px',
                        fontSize: '10px',
                        fontWeight: 700,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '3px'
                      }}
                      title="Insert this note directly into submission box"
                    >
                      <span>Argue Point</span>
                      <ChevronRight size={10} />
                    </button>
                  </div>

                  <div style={{ fontWeight: 700, fontSize: '12px', color: theme.textPrimary, marginBottom: '2px' }}>
                    {note.title}
                  </div>
                  <div style={{ fontSize: '11.5px', color: theme.textSecondary, lineHeight: '1.45' }}>
                    "{note.text}"
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* 4. CASE EXHIBITS DRAWER */}
      {showExhibitDrawer && selectedCase?.exhibits && (
        <div
          style={{
            position: 'absolute',
            top: isHeaderTrayOpen ? '96px' : '48px',
            right: 0,
            width: '360px',
            height: isHeaderTrayOpen ? 'calc(100% - 96px)' : 'calc(100% - 48px)',
            backgroundColor: theme.bgCard,
            borderLeft: `1px solid ${theme.borderDefault}`,
            boxShadow: '-8px 0 30px rgba(0,0,0,0.3)',
            zIndex: 30,
            padding: '18px',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div style={{ fontWeight: 800, fontSize: '14px', color: theme.textPrimary, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FileText size={16} color="#2563EB" />
              <span>Marked Exhibits & Evidence</span>
            </div>
            <button
              onClick={() => setShowExhibitDrawer(false)}
              style={{ background: 'none', border: 'none', color: theme.textSecondary, cursor: 'pointer', fontSize: '18px' }}
            >
              ✕
            </button>
          </div>

          <p style={{ fontSize: '11.5px', color: theme.textSecondary, marginBottom: '12px', lineHeight: '1.45' }}>
            Click any exhibit below to instantly frame a confrontation question for the deponent in the witness box.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1, overflowY: 'auto' }}>
            {selectedCase.exhibits.map((ex) => (
              <div
                key={ex.id}
                onClick={() => handleConfrontExhibit(ex)}
                style={{
                  backgroundColor: theme.bgCardSubtle,
                  border: `1px solid ${theme.borderDefault}`,
                  borderRadius: '6px',
                  padding: '10px 12px',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ fontWeight: 800, fontSize: '12px', color: '#2563EB', marginBottom: '2px' }}>
                  {ex.id}
                </div>
                <div style={{ fontSize: '11.5px', color: theme.textPrimary, lineHeight: '1.45' }}>
                  {ex.title}
                </div>
                <div style={{ marginTop: '6px', fontSize: '10.5px', color: '#10B981', display: 'flex', alignItems: 'center', gap: '3px', fontWeight: 700 }}>
                  <span>Confront Deponent</span>
                  <ChevronRight size={11} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. FULL-SCREEN HEARING PERMISSION MODAL (Always prompts on arrival if not fullscreen) */}
      {showFullscreenPrompt && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0,0,0,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 60,
            backdropFilter: 'blur(8px)'
          }}
        >
          <div
            style={{
              width: '500px',
              backgroundColor: theme.bgCard,
              border: `2px solid ${isDark ? 'rgba(217, 119, 6, 0.5)' : '#D97706'}`,
              borderRadius: '14px',
              padding: '24px 28px',
              boxShadow: '0 20px 50px rgba(0,0,0,0.4)',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <div style={{
              width: '54px',
              height: '54px',
              borderRadius: '50%',
              backgroundColor: isDark ? 'rgba(217, 119, 6, 0.15)' : '#FEF3C7',
              border: '2px solid #D97706',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '14px',
              color: '#D97706'
            }}>
              <Scale size={26} />
            </div>

            <div style={{ fontSize: '10px', fontWeight: 800, letterSpacing: '0.08em', color: '#D97706', textTransform: 'uppercase', marginBottom: '4px' }}>
              Judicial Immersion Chamber
            </div>
            <h2 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: 800, color: theme.textPrimary }}>
              Enter Full-Screen Hearing Mode?
            </h2>

            <p style={{ fontSize: '12.5px', color: theme.textSecondary, lineHeight: '1.55', margin: '0 0 20px 0' }}>
              For an authentic courtroom hearing experience, this trial session operates in an immersive full-screen chamber with continuous stenography, live speech recognition, and dual-pitch voice synthesis.
            </p>

            <div style={{ display: 'flex', gap: '10px', width: '100%' }}>
              <button
                onClick={handleDeclineFullscreen}
                style={{
                  flex: 1,
                  backgroundColor: theme.bgCardSubtle,
                  color: theme.textPrimary,
                  border: `1px solid ${theme.borderDefault}`,
                  padding: '10px',
                  borderRadius: '7px',
                  fontSize: '12.5px',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Windowed Mode
              </button>
              <button
                onClick={handleAcceptFullscreen}
                style={{
                  flex: 1,
                  backgroundColor: '#2563EB',
                  color: '#FFFFFF',
                  border: 'none',
                  padding: '10px',
                  borderRadius: '7px',
                  fontSize: '12.5px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  boxShadow: '0 4px 12px rgba(37, 99, 235, 0.35)'
                }}
              >
                <Maximize2 size={15} />
                <span>Enter Full-Screen</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 6. BENCH SCORECARD MODAL WITH DIRECT NAVIGATION TO AI SUGGESTIONS */}
      {showScorecard && scorecardData && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0,0,0,0.85)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 50,
            backdropFilter: 'blur(8px)'
          }}
        >
          <div
            style={{
              width: '680px',
              maxHeight: '90vh',
              overflowY: 'auto',
              backgroundColor: theme.bgCard,
              border: `1px solid ${isDark ? '#334155' : '#CBD5E1'}`,
              borderRadius: '14px',
              padding: '24px',
              boxShadow: '0 20px 50px rgba(0,0,0,0.6)',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Award size={22} color="#D97706" />
                <div>
                  <div style={{ fontWeight: 800, fontSize: '16px', color: theme.textPrimary }}>
                    Bench Assessment & Advocacy Scorecard
                  </div>
                  <div style={{ fontSize: '11.5px', color: theme.textSecondary }}>
                    Evaluation for {selectedCase?.title || 'Court Hearing'}
                  </div>
                </div>
              </div>
              <button
                onClick={() => setShowScorecard(false)}
                style={{ background: 'none', border: 'none', color: theme.textSecondary, cursor: 'pointer', fontSize: '18px' }}
              >
                ✕
              </button>
            </div>

            {/* Verdict Banner */}
            <div
              style={{
                backgroundColor: isDark ? 'rgba(217, 119, 6, 0.12)' : '#FEF3C7',
                border: isDark ? '1px solid rgba(217, 119, 6, 0.35)' : '1px solid #FDE68A',
                borderRadius: '8px',
                padding: '12px 16px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '16px'
              }}
            >
              <div>
                <div style={{ fontSize: '10px', color: '#D97706', fontWeight: 800, textTransform: 'uppercase' }}>
                  Bench Disposition & Ruling
                </div>
                <div style={{ fontSize: '15px', fontWeight: 800, color: theme.textPrimary, marginTop: '2px' }}>
                  {scorecardData.bench_verdict}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '10.5px', color: theme.textSecondary }}>Overall Score</div>
                <div style={{ fontSize: '24px', fontWeight: 900, color: scorecardData.overall_score >= 75 ? '#10B981' : '#D97706' }}>
                  {scorecardData.overall_score}<span style={{ fontSize: '13px', color: theme.textSecondary }}>/100</span>
                </div>
              </div>
            </div>

            {/* Metric Bars */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '9px', marginBottom: '16px' }}>
              {[
                { label: 'Substantive Argument Solidity', val: scorecardData.argument_solidity },
                { label: 'Statutory & Case Law Precision', val: scorecardData.statutory_accuracy },
                { label: 'Cross-Examination & Confrontation', val: scorecardData.cross_exam_sharpness },
                { label: 'Courtroom Demeanor & Deference', val: scorecardData.courtroom_demeanor },
                { label: 'Procedural Rules Compliance', val: scorecardData.procedural_compliance }
              ].map((m) => (
                <div key={m.label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '2px' }}>
                    <span style={{ color: theme.textPrimary }}>{m.label}</span>
                    <span style={{ fontWeight: 700, color: theme.textPrimary }}>{m.val}%</span>
                  </div>
                  <div style={{ width: '100%', height: '5px', backgroundColor: isDark ? '#1E293B' : '#E2E8F0', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${m.val}%`, height: '100%', backgroundColor: '#2563EB', borderRadius: '3px' }} />
                  </div>
                </div>
              ))}
            </div>

            {/* Strengths & Tactical Improvements */}
            <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
              <div style={{ flex: 1, backgroundColor: theme.bgCardSubtle, borderRadius: '8px', padding: '10px', border: `1px solid ${theme.borderDefault}` }}>
                <div style={{ fontSize: '10.5px', fontWeight: 800, color: '#10B981', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '6px' }}>
                  <CheckCircle2 size={12} />
                  <span>Demonstrated Strengths</span>
                </div>
                <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '11.5px', color: theme.textPrimary, lineHeight: '1.45' }}>
                  {scorecardData.strengths.map((s, idx) => (
                    <li key={idx} style={{ marginBottom: '3px' }}>{s}</li>
                  ))}
                </ul>
              </div>

              <div style={{ flex: 1, backgroundColor: theme.bgCardSubtle, borderRadius: '8px', padding: '10px', border: `1px solid ${theme.borderDefault}` }}>
                <div style={{ fontSize: '10.5px', fontWeight: 800, color: '#D97706', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '6px' }}>
                  <Info size={12} />
                  <span>Tactical Improvements</span>
                </div>
                <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '11.5px', color: theme.textPrimary, lineHeight: '1.45' }}>
                  {scorecardData.improvements.map((im, idx) => (
                    <li key={idx} style={{ marginBottom: '3px' }}>{im}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* AI SUGGESTIONS NAVIGATION BANNER (User Requested: "navigate to another page to get the ai suggestions to improve the arguments points") */}
            <div style={{
              backgroundColor: isDark ? 'rgba(37, 99, 235, 0.12)' : '#EFF6FF',
              border: isDark ? '1px solid rgba(37, 99, 235, 0.35)' : '1px solid #BFDBFE',
              borderRadius: '8px',
              padding: '12px 16px',
              marginBottom: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontWeight: 800, fontSize: '12.5px', color: '#2563EB', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <Sparkles size={14} />
                  <span>Improve Oral Arguments with AI Litigator</span>
                </div>
                <div style={{ fontSize: '11px', color: theme.textSecondary, marginTop: '2px' }}>
                  Launch LegalChat with this hearing's review to draft counter-arguments & statutory grounds.
                </div>
              </div>

              <button
                onClick={handleNavigateToAIAssistant}
                style={{
                  backgroundColor: '#2563EB',
                  color: '#FFFFFF',
                  border: 'none',
                  padding: '7px 14px',
                  borderRadius: '6px',
                  fontSize: '11.5px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  boxShadow: '0 2px 8px rgba(37, 99, 235, 0.3)'
                }}
              >
                <span>Get AI Suggestions</span>
                <ArrowRight size={12} />
              </button>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button
                onClick={handleNavigateToDrafting}
                style={{
                  backgroundColor: 'transparent',
                  color: theme.textSecondary,
                  border: `1px solid ${theme.borderDefault}`,
                  padding: '7px 12px',
                  borderRadius: '6px',
                  fontSize: '11.5px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <Edit3 size={12} />
                <span>Draft in Studio</span>
              </button>

              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={handleResetSession}
                  style={{
                    backgroundColor: theme.bgCardSubtle,
                    color: theme.textPrimary,
                    border: `1px solid ${theme.borderDefault}`,
                    padding: '7px 14px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    cursor: 'pointer'
                  }}
                >
                  Restart Simulation
                </button>
                <button
                  onClick={() => setShowScorecard(false)}
                  style={{
                    backgroundColor: isDark ? '#1E293B' : '#0F172A',
                    color: '#FFFFFF',
                    border: 'none',
                    padding: '7px 16px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  Resume Hearing
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourtroomSimulationView;
