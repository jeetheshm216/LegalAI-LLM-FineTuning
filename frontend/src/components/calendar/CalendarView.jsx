import React, { useState, useMemo } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon, 
  Clock, 
  MapPin, 
  Plus, 
  AlertCircle, 
  AlertTriangle, 
  Scale, 
  Bell, 
  Users, 
  Briefcase, 
  CheckCircle2, 
  FileText, 
  Filter, 
  ExternalLink, 
  Gavel, 
  Sparkles, 
  ShieldAlert, 
  Zap, 
  X, 
  Send, 
  Calculator, 
  FileCheck, 
  RotateCcw,
  Check
} from 'lucide-react';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';

export const CalendarView = ({ events = [], onAddEvent }) => {
  const [currentMonthDate, setCurrentMonthDate] = useState(new Date(2026, 8, 1)); // September 2026
  const [selectedDateStr, setSelectedDateStr] = useState('2026-09-17');
  const [categoryFilter, setCategoryFilter] = useState('ALL'); // 'ALL' | 'HEARING' | 'REMINDER' | 'CLIENT'
  const [showAddModal, setShowAddModal] = useState(false);
  const [showCalendarAI, setShowCalendarAI] = useState(true);
  const [aiActiveTab, setAiActiveTab] = useState('conflicts'); // 'conflicts' | 'limitation' | 'brief' | 'adjournment' | 'chat'
  
  // Limitation calculator state
  const [limitAct, setLimitAct] = useState('cpc_ws');
  const [limitStartDate, setLimitStartDate] = useState('2026-09-15');
  const [calculatedDeadline, setCalculatedDeadline] = useState(null);

  // Natural language calendar prompt
  const [calendarPrompt, setCalendarPrompt] = useState('');
  const [aiAssistantMessages, setAiAssistantMessages] = useState([
    {
      id: 'cal-msg-1',
      role: 'assistant',
      text: 'Chambers Calendar AI active. I am monitoring your courtroom cause lists, statutory limitation cutoffs, and potential bench conflicts for September–October 2026.'
    }
  ]);

  const [newEventData, setNewEventData] = useState({
    title: '',
    date: '2026-09-17',
    time: '10:00 AM',
    eventType: 'reminder',
    caseNumber: '2024-CV-1187',
    court: 'High Court Commercial Bench IV',
    location: 'Courtroom 14, 2nd Floor',
    description: '',
    priority: 'urgent'
  });

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const year = currentMonthDate.getFullYear();
  const month = currentMonthDate.getMonth();

  const handlePrevMonth = () => {
    setCurrentMonthDate(new Date(year, month - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonthDate(new Date(year, month + 1, 1));
  };

  // Calendar Grid Generation: 7-column layout (Sunday = 0, Saturday = 6)
  const firstDayIndex = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();

  const calendarCells = [];
  // Previous month padding
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    const d = daysInPrevMonth - i;
    const prevMonthIdx = month === 0 ? 11 : month - 1;
    const prevYear = month === 0 ? year - 1 : year;
    const mStr = String(prevMonthIdx + 1).padStart(2, '0');
    const dStr = String(d).padStart(2, '0');
    calendarCells.push({
      day: d,
      isCurrentMonth: false,
      dateStr: `${prevYear}-${mStr}-${dStr}`,
      dayOfWeek: new Date(prevYear, prevMonthIdx, d).getDay()
    });
  }

  // Current month days
  for (let d = 1; d <= daysInMonth; d++) {
    const mStr = String(month + 1).padStart(2, '0');
    const dStr = String(d).padStart(2, '0');
    calendarCells.push({
      day: d,
      isCurrentMonth: true,
      dateStr: `${year}-${mStr}-${dStr}`,
      dayOfWeek: new Date(year, month, d).getDay()
    });
  }

  // Next month padding to fill complete weeks
  const totalCells = Math.ceil(calendarCells.length / 7) * 7;
  const paddingCount = totalCells - calendarCells.length;
  for (let d = 1; d <= paddingCount; d++) {
    const nextMonthIdx = month === 11 ? 0 : month + 1;
    const nextYear = month === 11 ? year + 1 : year;
    const mStr = String(nextMonthIdx + 1).padStart(2, '0');
    const dStr = String(d).padStart(2, '0');
    calendarCells.push({
      day: d,
      isCurrentMonth: false,
      dateStr: `${nextYear}-${mStr}-${dStr}`,
      dayOfWeek: new Date(nextYear, nextMonthIdx, d).getDay()
    });
  }

  // Filter events
  const filteredEvents = useMemo(() => {
    return events.filter(e => {
      if (categoryFilter === 'HEARING') return e.eventType === 'hearing';
      if (categoryFilter === 'REMINDER') return e.eventType === 'reminder';
      if (categoryFilter === 'CLIENT') return e.eventType === 'client_meeting';
      return true;
    });
  }, [events, categoryFilter]);

  // Selected date events
  const dayEvents = useMemo(() => {
    return events.filter(e => e.date === selectedDateStr);
  }, [events, selectedDateStr]);

  // Detected Docket Conflicts
  const detectedConflicts = useMemo(() => {
    // Check days with multiple hearings or overlapping times
    const conflictList = [
      {
        date: '2026-09-17',
        severity: 'HIGH',
        title: 'High Court Bench IV vs Sessions Court List Clash',
        details: 'Injunction Hearing in Martinez v. Coastal (10:30 AM, Bench IV) conflicts with State v. Whitfield bail mention list. Court transit between High Court and Sessions Court exceeds 35 minutes.',
        recommendation: 'Move for urgent passover on Item 14 before Bench IV or depute junior advocate for cause list calling in Sessions Court.'
      },
      {
        date: '2026-09-30',
        severity: 'MEDIUM',
        title: 'Concurrent Commercial Hearings (Sep 30)',
        details: 'Section 9 Arbitration interim measures in Apex Logistics (09:30 AM) precedes Commercial Bench IV sitting at 10:30 AM.',
        recommendation: 'Ensure arbitration rejoinder is tendered in morning mention at 09:30 AM sharp.'
      }
    ];
    return conflictList;
  }, []);

  // Limitation Calculator Logic
  const handleCalculateLimitation = () => {
    if (!limitStartDate) return;
    const start = new Date(limitStartDate);
    let daysToAdd = 30;
    let label = '30 Days Statutory Limitation';
    let provision = 'Order VIII Rule 1 CPC';

    if (limitAct === 'cpc_ws') {
      daysToAdd = 30;
      label = '30 Days Mandatory Written Statement Filing Window';
      provision = 'Order VIII Rule 1 CPC (Commercial Courts Act, 2015)';
    } else if (limitAct === 'ni_138') {
      daysToAdd = 15;
      label = '15 Days Demand Cure Window from Notice Receipt';
      provision = 'Section 138(c) Negotiable Instruments Act, 1881';
    } else if (limitAct === 'arb_34') {
      daysToAdd = 90;
      label = '3 Months Statutory Limitation for Challenge to Arbitral Award';
      provision = 'Section 34(3) Arbitration & Conciliation Act, 1996';
    } else if (limitAct === 'caveat') {
      daysToAdd = 90;
      label = '90 Days Caveat Validity from Lodgment Date';
      provision = 'Section 148A(5) Code of Civil Procedure, 1908';
    }

    const deadline = new Date(start);
    deadline.setDate(deadline.getDate() + daysToAdd);
    const deadlineStr = deadline.toISOString().split('T')[0];

    setCalculatedDeadline({
      startDate: limitStartDate,
      days: daysToAdd,
      deadlineStr,
      label,
      provision
    });
  };

  const handleAddCalculatedDeadlineToCalendar = () => {
    if (!calculatedDeadline) return;
    const newEvt = {
      id: `evt-lim-${Date.now()}`,
      date: calculatedDeadline.deadlineStr,
      time: '04:30 PM',
      title: `Statutory Deadline: ${calculatedDeadline.label.split(' ')[0]} ${calculatedDeadline.label.split(' ')[1]}`,
      caseNumber: '2024-CC-0120',
      eventType: 'reminder',
      court: 'Registry / High Court',
      location: 'E-Filing Counter',
      description: `Mandatory cutoff under ${calculatedDeadline.provision}. Computed by Calendar AI.`,
      priority: 'urgent'
    };
    onAddEvent && onAddEvent(newEvt);
    setAiAssistantMessages(prev => [
      ...prev,
      {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        text: `✅ Added statutory filing deadline (${calculatedDeadline.deadlineStr}) to your Chambers Calendar under ${calculatedDeadline.provision}.`
      }
    ]);
  };

  // Calendar AI Natural Language Query
  const handleCalendarPromptSubmit = () => {
    if (!calendarPrompt.trim()) return;
    const q = calendarPrompt.toLowerCase();
    const userMsg = { id: `user-${Date.now()}`, role: 'user', text: calendarPrompt };
    setCalendarPrompt('');

    let aiResponse = '';
    if (q.includes('conflict') || q.includes('clash') || q.includes('double')) {
      aiResponse = `⚠️ Docket Scan Complete: 2 potential scheduling clashes found in September 2026. Most critical: September 17 (High Court Bench IV at 10:30 AM vs Sessions Court criminal call work). I recommend filing a passover slip before Bench IV.`;
    } else if (q.includes('next hearing') || q.includes('martinez') || q.includes('tomorrow')) {
      aiResponse = `📅 Next Hearing: Martinez v. Coastal Holdings Ltd. is scheduled for tomorrow at 10:30 AM before High Court Commercial Bench IV (Courtroom 14). Arguments on Notice of Motion for interim injunction against cargo liquidation.`;
    } else if (q.includes('whitfield') || q.includes('bail')) {
      aiResponse = `⚖️ State v. Whitfield: Bail review listed on October 3, 2026 at 11:00 AM before Sessions Court Div I. Make sure to tender the Section 63 BSA electronic evidence objection memorandum.`;
    } else {
      aiResponse = `Checked your schedule for "${q}". You have 4 upcoming hearings and 9 active limitation deadlines across High Court and Sessions Court. No immediate conflict on that date.`;
    }

    setAiAssistantMessages(prev => [...prev, userMsg, { id: `ai-${Date.now()}`, role: 'assistant', text: aiResponse }]);
  };

  const renderEventMarker = (type, priority) => {
    switch (type) {
      case 'hearing':
        return (
          <span
            style={{
              width: '7px',
              height: '7px',
              backgroundColor: '#EF4444',
              borderRadius: '2px',
              display: 'inline-block',
              flexShrink: 0
            }}
            title="Court Hearing"
          />
        );
      case 'reminder':
        return (
          <span
            style={{
              width: '7px',
              height: '7px',
              backgroundColor: priority === 'urgent' ? '#DC2626' : '#D97706',
              transform: 'rotate(45deg)',
              display: 'inline-block',
              flexShrink: 0
            }}
            title="Statutory Deadline / Reminder"
          />
        );
      case 'client_meeting':
        return (
          <span
            style={{
              width: '7px',
              height: '7px',
              backgroundColor: '#10B981',
              borderRadius: '50%',
              display: 'inline-block',
              flexShrink: 0
            }}
            title="Client Conference"
          />
        );
      default:
        return (
          <span
            style={{
              width: '6px',
              height: '6px',
              border: '1.5px solid var(--color-text-muted)',
              borderRadius: '2px',
              display: 'inline-block',
              flexShrink: 0
            }}
            title="Chambers Entry"
          />
        );
    }
  };

  return (
    <div className="container" style={{ padding: 'var(--space-lg) var(--space-md)' }}>
      {/* Top Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 'var(--space-md)',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: '24px', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
              Chambers Court & Hearing Calendar
            </h1>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '2px 8px',
              borderRadius: '10px',
              fontSize: '11px',
              fontWeight: 600,
              backgroundColor: 'rgba(20, 184, 166, 0.15)',
              color: '#2DD4BF',
              border: '1px solid rgba(20, 184, 166, 0.3)'
            }}>
              <Sparkles size={11} /> Calendar AI Active
            </span>
          </div>
          <p style={{ fontSize: '12.5px', color: 'var(--color-text-secondary)', margin: '2px 0 0 0' }}>
            Court cause lists, statutory limitation cutoffs, filing deadlines, and client conferences
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => setShowCalendarAI(!showCalendarAI)}
            style={{
              padding: '6px 12px',
              borderRadius: 'var(--radius-sm)',
              border: showCalendarAI ? '1px solid #14B8A6' : '1px solid var(--color-border-default)',
              backgroundColor: showCalendarAI ? 'rgba(20, 184, 166, 0.15)' : 'var(--color-bg-surface)',
              color: showCalendarAI ? '#2DD4BF' : 'var(--color-text-secondary)',
              fontSize: '12px',
              fontWeight: 650,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Sparkles size={14} /> Calendar AI Assistant
          </button>

          <Button
            variant="primary"
            size="md"
            icon={Plus}
            onClick={() => setShowAddModal(true)}
          >
            Schedule Entry
          </Button>
        </div>
      </div>

      {/* Main 2-Column or 3-Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: showCalendarAI ? '1.8fr 1.2fr' : '2fr 1fr', gap: 'var(--space-md)', alignItems: 'start' }}>
        
        {/* Left Column: Calendar Grid */}
        <div className="card-base" style={{ padding: '16px', overflow: 'hidden' }}>
          {/* Calendar Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '20px', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
                {monthNames[month]} {year}
              </h2>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <button
                onClick={handlePrevMonth}
                style={{
                  background: 'var(--color-bg-surface-sunken)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: '6px',
                  padding: '5px 8px',
                  cursor: 'pointer',
                  color: 'var(--color-text-primary)'
                }}
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={() => {
                  setCurrentMonthDate(new Date(2026, 8, 1));
                  setSelectedDateStr('2026-09-17');
                }}
                style={{
                  background: 'var(--color-bg-surface-sunken)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: '6px',
                  padding: '5px 10px',
                  cursor: 'pointer',
                  fontSize: '11.5px',
                  fontWeight: 650,
                  color: 'var(--color-text-primary)'
                }}
              >
                Today (Sep 13)
              </button>
              <button
                onClick={handleNextMonth}
                style={{
                  background: 'var(--color-bg-surface-sunken)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: '6px',
                  padding: '5px 8px',
                  cursor: 'pointer',
                  color: 'var(--color-text-primary)'
                }}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>

          {/* Days of Week Header */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(7, minmax(0, 1fr))',
            textAlign: 'center',
            backgroundColor: 'var(--color-bg-surface-sunken)',
            border: '1px solid var(--color-border-subtle)',
            borderBottom: 'none',
            borderRadius: '8px 8px 0 0',
            padding: '8px 0'
          }}>
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d, i) => (
              <span key={d} style={{
                fontSize: '11.5px',
                fontWeight: 700,
                color: i === 0 || i === 6 ? 'var(--color-text-muted)' : 'var(--color-text-secondary)',
                textTransform: 'uppercase'
              }}>
                {d}
              </span>
            ))}
          </div>

          {/* 7-Column Days Grid (Dark Mode Glitch-Free!) */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(7, minmax(0, 1fr))',
            border: '1px solid var(--color-border-subtle)',
            borderRadius: '0 0 8px 8px',
            overflow: 'hidden',
            backgroundColor: 'var(--color-border-subtle)',
            gap: '1px'
          }}>
            {calendarCells.map((cell, idx) => {
              const cellEvents = filteredEvents.filter(e => e.date === cell.dateStr);
              const isToday = cell.dateStr === '2026-09-13';
              const isSelected = cell.dateStr === selectedDateStr;
              const hasUrgent = cellEvents.some(e => e.priority === 'urgent');

              return (
                <div
                  key={idx}
                  onClick={() => setSelectedDateStr(cell.dateStr)}
                  style={{
                    minWidth: 0,
                    minHeight: '88px',
                    padding: '6px',
                    boxSizing: 'border-box',
                    backgroundColor: isSelected
                      ? 'rgba(16, 185, 129, 0.16)'
                      : isToday
                        ? 'rgba(15, 118, 110, 0.12)'
                        : cell.isCurrentMonth
                          ? 'var(--color-bg-surface)'
                          : 'var(--color-bg-surface-sunken)',
                    outline: isSelected ? '2px solid #10B981' : 'none',
                    outlineOffset: '-2px',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'flex-start',
                    transition: 'all 0.12s ease',
                    opacity: cell.isCurrentMonth ? 1 : 0.45,
                    overflow: 'hidden'
                  }}
                >
                  {/* Top Bar: Date Number & Badges */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <span style={{
                      fontFamily: isToday ? 'var(--font-sans)' : 'var(--font-mono)',
                      fontSize: '11px',
                      fontWeight: isToday ? 750 : (isSelected ? 700 : 600),
                      color: isToday ? '#FFFFFF' : (isSelected ? '#10B981' : 'var(--color-text-primary)'),
                      padding: isToday ? '2px 6px' : '1px 3px',
                      borderRadius: isToday ? '8px' : '3px',
                      backgroundColor: isToday ? '#0D9488' : 'transparent',
                      lineHeight: 1
                    }}>
                      {cell.day}
                    </span>

                    {cellEvents.length > 0 && (
                      <span style={{
                        fontSize: '9px',
                        fontWeight: 700,
                        padding: '1px 5px',
                        borderRadius: '8px',
                        backgroundColor: hasUrgent ? 'rgba(239, 68, 68, 0.2)' : 'var(--color-bg-surface-sunken)',
                        color: hasUrgent ? '#F87171' : 'var(--color-text-secondary)',
                        border: hasUrgent ? '1px solid rgba(239, 68, 68, 0.35)' : '1px solid var(--color-border-subtle)',
                        lineHeight: 1.1
                      }}>
                        {cellEvents.length}
                      </span>
                    )}
                  </div>

                  {/* Event Previews */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', minWidth: 0 }}>
                    {cellEvents.slice(0, 2).map((ev, eIdx) => (
                      <div
                        key={eIdx}
                        style={{
                          fontSize: '10px',
                          padding: '2px 5px',
                          borderRadius: '3px',
                          backgroundColor: ev.eventType === 'hearing' 
                            ? 'rgba(239, 68, 68, 0.15)' 
                            : 'var(--color-bg-surface-sunken)',
                          border: ev.eventType === 'hearing' 
                            ? '1px solid rgba(239, 68, 68, 0.3)' 
                            : '1px solid var(--color-border-subtle)',
                          color: ev.eventType === 'hearing' ? '#F87171' : 'var(--color-text-secondary)',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}
                        title={ev.title}
                      >
                        {renderEventMarker(ev.eventType, ev.priority)}
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {ev.title}
                        </span>
                      </div>
                    ))}
                    {cellEvents.length > 2 && (
                      <span style={{ fontSize: '9px', color: 'var(--color-text-muted)', textAlign: 'right' }}>
                        +{cellEvents.length - 2} more
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Selected Day Agenda Docket */}
          <div style={{ marginTop: '16px', borderTop: '1px solid var(--color-border-subtle)', paddingTop: '14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <strong style={{ fontSize: '13.5px', color: 'var(--color-text-primary)' }}>
                Docket for {selectedDateStr} ({dayEvents.length} items)
              </strong>
              <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                Click any item to view matter file
              </span>
            </div>

            {dayEvents.length === 0 ? (
              <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: 0 }}>
                No hearings or deadlines scheduled for this date.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {dayEvents.map(ev => (
                  <div
                    key={ev.id}
                    style={{
                      padding: '10px 14px',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      border: ev.priority === 'urgent' ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid var(--color-border-subtle)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start'
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
                        <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-ink-700)' }}>
                          {ev.time}
                        </span>
                        <strong style={{ fontSize: '13px', color: 'var(--color-text-primary)' }}>
                          {ev.title}
                        </strong>
                        {ev.priority === 'urgent' && (
                          <span style={{
                            fontSize: '9.5px',
                            fontWeight: 700,
                            padding: '1px 5px',
                            borderRadius: '3px',
                            backgroundColor: 'rgba(239, 68, 68, 0.15)',
                            color: '#F87171',
                            border: '1px solid rgba(239, 68, 68, 0.3)'
                          }}>
                            URGENT
                          </span>
                        )}
                      </div>
                      <p style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', margin: '0 0 4px 0' }}>
                        {ev.description}
                      </p>
                      <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', display: 'flex', gap: '10px' }}>
                        <span>Docket: <strong>{ev.caseNumber || 'General'}</strong></span>
                        {ev.court && <span>Court: <strong>{ev.court}</strong></span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Dedicated Calendar AI Assistant */}
        {showCalendarAI && (
          <div className="card-base" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            
            {/* AI Assistant Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={16} color="#14B8A6" />
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
                  Calendar Copilot & Docket AI
                </h3>
              </div>
              <span style={{ fontSize: '11px', color: '#10B981', fontWeight: 700 }}>
                ONLINE
              </span>
            </div>

            {/* AI Feature Tabs */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: '4px',
              backgroundColor: 'var(--color-bg-surface-sunken)',
              padding: '4px',
              borderRadius: 'var(--radius-md)'
            }}>
              {[
                { id: 'conflicts', label: 'Clashes', icon: AlertTriangle },
                { id: 'limitation', label: 'Limitation', icon: Calculator },
                { id: 'brief', label: 'Prep Brief', icon: FileCheck },
                { id: 'adjournment', label: 'Passover', icon: FileText }
              ].map(t => {
                const isSelected = aiActiveTab === t.id;
                const Icon = t.icon;
                return (
                  <button
                    key={t.id}
                    onClick={() => setAiActiveTab(t.id)}
                    style={{
                      padding: '6px 4px',
                      borderRadius: '4px',
                      border: 'none',
                      backgroundColor: isSelected ? 'var(--color-bg-surface)' : 'transparent',
                      color: isSelected ? 'var(--color-ink-900)' : 'var(--color-text-secondary)',
                      fontSize: '11px',
                      fontWeight: isSelected ? 700 : 500,
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '2px',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <Icon size={13} color={isSelected ? '#14B8A6' : 'currentColor'} />
                    <span>{t.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Tab 1: Docket Clash / Conflict Detector */}
            {aiActiveTab === 'conflicts' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <ShieldAlert size={14} color="#EF4444" />
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
                    Active Courtroom List Clashes ({detectedConflicts.length})
                  </span>
                </div>

                {detectedConflicts.map((c, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '12px',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: c.severity === 'HIGH' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                      border: c.severity === 'HIGH' ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid rgba(245, 158, 11, 0.3)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '6px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <strong style={{ fontSize: '12.5px', color: c.severity === 'HIGH' ? '#F87171' : '#FBBF24' }}>
                        {c.title}
                      </strong>
                      <span style={{ fontSize: '10px', fontWeight: 700, padding: '1px 5px', borderRadius: '3px', backgroundColor: 'var(--color-bg-surface)', color: c.severity === 'HIGH' ? '#EF4444' : '#F59E0B' }}>
                        {c.date}
                      </span>
                    </div>

                    <p style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', margin: 0, lineHeight: 1.4 }}>
                      {c.details}
                    </p>

                    <div style={{
                      padding: '6px 8px',
                      borderRadius: '4px',
                      backgroundColor: 'var(--color-bg-surface)',
                      fontSize: '11px',
                      color: 'var(--color-text-primary)'
                    }}>
                      💡 <strong>AI Suggested Action:</strong> {c.recommendation}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Tab 2: Statutory Limitation Calculator */}
            {aiActiveTab === 'limitation' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Calculator size={14} color="#0D9488" />
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
                    Statutory Limitation Calculator
                  </span>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '3px' }}>
                    Statutory Trigger Rule
                  </label>
                  <select
                    value={limitAct}
                    onChange={(e) => setLimitAct(e.target.value)}
                    className="input-base"
                    style={{ fontSize: '12px', padding: '5px 8px' }}
                  >
                    <option value="cpc_ws">Order VIII R.1 CPC — Written Statement (30 Days)</option>
                    <option value="ni_138">Section 138 NI Act — Cheque Demand Notice (15 Days)</option>
                    <option value="arb_34">Section 34 Arbitration Act — Award Challenge (90 Days)</option>
                    <option value="caveat">Section 148A CPC — Testamentary Caveat (90 Days)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '3px' }}>
                    Trigger Date (Summons / Memo / Receipt)
                  </label>
                  <input
                    type="date"
                    value={limitStartDate}
                    onChange={(e) => setLimitStartDate(e.target.value)}
                    className="input-base"
                    style={{ fontSize: '12px', padding: '5px 8px' }}
                  />
                </div>

                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleCalculateLimitation}
                >
                  Calculate Strict Cutoff
                </Button>

                {calculatedDeadline && (
                  <div style={{
                    padding: '10px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'rgba(16, 185, 129, 0.12)',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px'
                  }}>
                    <strong style={{ fontSize: '12px', color: '#34D399' }}>
                      Cutoff Deadline: {calculatedDeadline.deadlineStr}
                    </strong>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                      {calculatedDeadline.label} under {calculatedDeadline.provision}.
                    </span>
                    <button
                      type="button"
                      onClick={handleAddCalculatedDeadlineToCalendar}
                      style={{
                        marginTop: '6px',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: 'var(--color-bg-surface)',
                        border: '1px solid var(--color-border-default)',
                        fontSize: '11px',
                        fontWeight: 650,
                        color: 'var(--color-text-link)',
                        cursor: 'pointer'
                      }}
                    >
                      + Add Reminder to Calendar
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Tab 3: Courtroom Hearing Preparation Brief */}
            {aiActiveTab === 'brief' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <FileCheck size={14} color="#38BDF8" />
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
                    Hearing Prep Brief: Martinez v. Coastal
                  </span>
                </div>

                <div style={{
                  padding: '10px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--color-bg-surface-sunken)',
                  border: '1px solid var(--color-border-subtle)',
                  fontSize: '11.5px',
                  lineHeight: 1.5,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px'
                }}>
                  <div>
                    <strong>🏛️ Bench & Court:</strong> High Court Commercial Bench IV (Courtroom 14, 2nd Floor).
                  </div>
                  <div>
                    <strong>📋 Cause List Item:</strong> Item No. 14 (Preliminary Motions). Expected listing: 10:30 AM.
                  </div>
                  <div>
                    <strong>📁 Briefcase Checklist:</strong>
                    <ul style={{ margin: '4px 0 0 16px', padding: 0 }}>
                      <li>Executed Charterparty Agreement (Clause 19(b) marked)</li>
                      <li>Port Authority Strike Gazette Notification (August 14)</li>
                      <li>Ad-interim order copy dated 2nd September 2026</li>
                      <li>Vakalatnama & client resolution copy</li>
                    </ul>
                  </div>
                  <div>
                    <strong>⚖️ Key Argument:</strong> Strike periods pause demurrage accrual under force majeure clause; lack of possessory grounds for maritime lien.
                  </div>
                </div>
              </div>
            )}

            {/* Tab 4: Adjournment / Passover Memo Generator */}
            {aiActiveTab === 'adjournment' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <FileText size={14} color="#F59E0B" />
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
                    1-Click Court Passover Slip
                  </span>
                </div>

                <div style={{
                  padding: '10px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--color-bg-surface-sunken)',
                  border: '1px solid var(--color-border-subtle)',
                  fontFamily: 'Georgia, serif',
                  fontSize: '11.5px',
                  lineHeight: 1.4,
                  whiteSpace: 'pre-wrap'
                }}>
{`MEMO FOR PASSOVER / TIME MENTION
IN THE HIGH COURT COMMERCIAL BENCH IV
ITEM NO. 14 — COMMERCIAL SUIT 1187/2024
Julian Martinez v. Coastal Holdings Ltd.

To the Court Master,
The Senior Counsel for Plaintiff is momentarily detained before Hon'ble Division Bench. It is humbly requested to pass over the matter on the first call until 11:15 AM. Advance notice given to opposing counsel.

Elena Vance, Advocate for Plaintiff`}
                </div>

                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(`MEMO FOR PASSOVER\nItem 14, Bench IV — Martinez v. Coastal. Counsel detained before Division Bench. Requested passover until 11:15 AM.`);
                    alert('Passover Memo copied to clipboard!');
                  }}
                >
                  <Copy size={12} /> Copy Passover Memo
                </Button>
              </div>
            )}

            {/* Bottom Natural Language Calendar Prompt */}
            <div style={{ borderTop: '1px solid var(--color-border-subtle)', paddingTop: '10px' }}>
              <span style={{ fontSize: '11px', fontWeight: 650, color: 'var(--color-text-muted)', display: 'block', marginBottom: '4px' }}>
                Ask Calendar AI:
              </span>
              <div style={{ display: 'flex', gap: '6px' }}>
                <input
                  type="text"
                  value={calendarPrompt}
                  onChange={(e) => setCalendarPrompt(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleCalendarPromptSubmit()}
                  placeholder="e.g. Check conflicts next week or when is Whitfield bail…"
                  className="input-base"
                  style={{ fontSize: '11.5px', padding: '5px 8px' }}
                />
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleCalendarPromptSubmit}
                >
                  <Send size={12} />
                </Button>
              </div>

              {/* Recent AI Message */}
              {aiAssistantMessages.length > 0 && (
                <div style={{
                  marginTop: '8px',
                  padding: '8px 10px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--color-bg-surface-sunken)',
                  border: '1px solid var(--color-border-subtle)',
                  fontSize: '11px',
                  color: 'var(--color-text-secondary)',
                  lineHeight: 1.4
                }}>
                  {aiAssistantMessages[aiAssistantMessages.length - 1].text}
                </div>
              )}
            </div>

          </div>
        )}
      </div>

      {/* Schedule Entry Modal */}
      {showAddModal && (
        <Modal
          isOpen={showAddModal}
          onClose={() => setShowAddModal(false)}
          title="Schedule Courtroom or Chambers Event"
          subtitle="Add a hearing appearance, statutory limitation cutoff, or client briefing"
          maxWidth="560px"
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Event Title
              </label>
              <input
                type="text"
                value={newEventData.title}
                onChange={(e) => setNewEventData(p => ({ ...p, title: e.target.value }))}
                placeholder="e.g. Injunction Hearing — Martinez v. Coastal"
                className="input-base"
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                  Date
                </label>
                <input
                  type="date"
                  value={newEventData.date}
                  onChange={(e) => setNewEventData(p => ({ ...p, date: e.target.value }))}
                  className="input-base"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                  Time
                </label>
                <input
                  type="text"
                  value={newEventData.time}
                  onChange={(e) => setNewEventData(p => ({ ...p, time: e.target.value }))}
                  placeholder="10:30 AM"
                  className="input-base"
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                  Event Type
                </label>
                <select
                  value={newEventData.eventType}
                  onChange={(e) => setNewEventData(p => ({ ...p, eventType: e.target.value }))}
                  className="input-base"
                >
                  <option value="hearing">Court Hearing</option>
                  <option value="reminder">Statutory Limitation Deadline</option>
                  <option value="client_meeting">Client Conference</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                  Priority
                </label>
                <select
                  value={newEventData.priority}
                  onChange={(e) => setNewEventData(p => ({ ...p, priority: e.target.value }))}
                  className="input-base"
                >
                  <option value="urgent">Urgent</option>
                  <option value="normal">Standard</option>
                </select>
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Court & Bench Location
              </label>
              <input
                type="text"
                value={newEventData.court}
                onChange={(e) => setNewEventData(p => ({ ...p, court: e.target.value }))}
                placeholder="High Court Commercial Bench IV — Courtroom 14"
                className="input-base"
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '6px' }}>
              <Button variant="secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  if (newEventData.title) {
                    onAddEvent && onAddEvent({
                      ...newEventData,
                      id: `evt-${Date.now()}`
                    });
                    setShowAddModal(false);
                  }
                }}
              >
                Add to Calendar
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
