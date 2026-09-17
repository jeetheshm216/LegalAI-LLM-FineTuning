/**
 * CalendarView.jsx
 * 
 * Professional Chambers Court & Hearing Calendar Component.
 * Provides an executive, structured monthly calendar with:
 * - Clean date grid layout (no overlapping numbers or distorted padding)
 * - Comprehensive Reminders & Statutory Limitation Deadlines integration
 * - Quick category filter pills (All, Hearings, Reminders & Deadlines, Client Conferences)
 * - Color-coded, highly legible event pill tags in calendar cells
 * - Interactive Day Docket with detailed procedural metadata
 * - Dedicated "Upcoming Statutory Deadlines & Reminders" priority sidebar card
 * - Full scheduling modal for court appearances, client briefings, and limitation reminders
 */

import React, { useState } from 'react';
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
  ExternalLink
} from 'lucide-react';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';

export const CalendarView = ({ events = [], onAddEvent }) => {
  const [currentMonthDate, setCurrentMonthDate] = useState(new Date(2026, 8, 1)); // September 2026
  const [selectedDateStr, setSelectedDateStr] = useState('2026-09-17');
  const [categoryFilter, setCategoryFilter] = useState('ALL'); // 'ALL' | 'HEARING' | 'REMINDER' | 'CLIENT'
  const [showAddModal, setShowAddModal] = useState(false);
  const [newEventData, setNewEventData] = useState({
    title: '',
    date: '2026-09-17',
    time: '10:00 AM',
    eventType: 'reminder',
    caseNumber: '2024-CV-1187',
    court: 'High Court Registry',
    location: 'Courtroom 14 / Registry Desk',
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

  // Calendar Grid Generation for exact 35 or 42 cells
  const firstDayIndex = new Date(year, month, 1).getDay(); // 0 = Sun
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();

  const calendarCells = [];
  // Prev month padding
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    const day = daysInPrevMonth - i;
    const prevMonthIdx = month === 0 ? 11 : month - 1;
    const prevYear = month === 0 ? year - 1 : year;
    const dateStr = `${prevYear}-${String(prevMonthIdx + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    calendarCells.push({ day, isCurrentMonth: false, dateStr });
  }
  // Current month days
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    calendarCells.push({ day: d, isCurrentMonth: true, dateStr });
  }
  // Next month padding to complete 35 or 42 cells
  const totalSlots = calendarCells.length <= 35 ? 35 : 42;
  const nextMonthPadding = totalSlots - calendarCells.length;
  for (let n = 1; n <= nextMonthPadding; n++) {
    const nextMonthIdx = month === 11 ? 0 : month + 1;
    const nextYear = month === 11 ? year + 1 : year;
    const dateStr = `${nextYear}-${String(nextMonthIdx + 1).padStart(2, '0')}-${String(n).padStart(2, '0')}`;
    calendarCells.push({ day: n, isCurrentMonth: false, dateStr });
  }

  // Filter events based on active category
  const filteredEvents = events.filter(e => {
    if (categoryFilter === 'ALL') return true;
    if (categoryFilter === 'HEARING') return e.eventType === 'hearing';
    if (categoryFilter === 'REMINDER') return e.eventType === 'reminder';
    if (categoryFilter === 'CLIENT') return e.eventType === 'client_meeting' || e.eventType === 'visitor';
    return true;
  });

  // Events on currently selected day
  const selectedDateEvents = filteredEvents.filter(e => e.date === selectedDateStr);

  // All upcoming reminders sorted chronologically for the dedicated Reminders Panel
  const allReminders = events
    .filter(e => e.eventType === 'reminder')
    .sort((a, b) => a.date.localeCompare(b.date));

  // Shape Marker Helper
  const renderEventMarker = (type, priority) => {
    switch (type) {
      case 'hearing':
        return (
          <span
            style={{
              width: '8px',
              height: '8px',
              backgroundColor: 'var(--color-ink-900)',
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
              width: '8px',
              height: '8px',
              backgroundColor: priority === 'urgent' ? '#DC2626' : '#D97706',
              transform: 'rotate(45deg)',
              display: 'inline-block',
              flexShrink: 0,
              boxShadow: priority === 'urgent' ? '0 0 4px rgba(220, 38, 38, 0.4)' : 'none'
            }}
            title="Statutory Deadline / Reminder"
          />
        );
      case 'client_meeting':
        return (
          <span
            style={{
              width: '8px',
              height: '8px',
              backgroundColor: 'var(--color-accent-700)',
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
              width: '8px',
              height: '8px',
              border: '1.5px solid var(--color-text-muted)',
              borderRadius: '2px',
              display: 'inline-block',
              flexShrink: 0
            }}
            title="General Chamber Task"
          />
        );
    }
  };

  const handleCreateSubmit = (e) => {
    e.preventDefault();
    if (!newEventData.title) return;
    onAddEvent(newEventData);
    setShowAddModal(false);
    setSelectedDateStr(newEventData.date);
  };

  // Format date helper for human readable display (e.g. "Thursday, September 17, 2026")
  const formatHumanDate = (dateStr) => {
    try {
      const [y, m, d] = dateStr.split('-').map(Number);
      const dt = new Date(y, m - 1, d);
      return dt.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  // Counts for filters
  const countHearings = events.filter(e => e.eventType === 'hearing').length;
  const countReminders = events.filter(e => e.eventType === 'reminder').length;
  const countClients = events.filter(e => e.eventType === 'client_meeting' || e.eventType === 'visitor').length;

  return (
    <div className="container" style={{ padding: 'var(--space-lg) var(--space-md)' }}>
      {/* Top Header & Toolbar */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 'var(--space-md)',
          marginBottom: 'var(--space-lg)',
          borderBottom: '1px solid var(--color-border-subtle)',
          paddingBottom: 'var(--space-md)'
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '28px',
                height: '28px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--color-ink-900)',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <CalendarIcon size={16} />
            </div>
            <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: '24px', fontWeight: 700, color: 'var(--color-ink-900)', margin: 0 }}>
              Chambers Court & Hearing Calendar
            </h1>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px', marginLeft: '36px' }}>
            Tribunal listings, statutory limitation deadlines, filing reminders, and client sessions
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          {/* Quick Filter Segmented Pills */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: 'var(--color-bg-surface-sunken)',
              borderRadius: 'var(--radius-md)',
              padding: '3px',
              border: '1px solid var(--color-border-subtle)'
            }}
          >
            <button
              onClick={() => setCategoryFilter('ALL')}
              style={{
                background: categoryFilter === 'ALL' ? 'var(--color-bg-surface)' : 'transparent',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '5px 10px',
                fontSize: '11px',
                fontWeight: 650,
                color: categoryFilter === 'ALL' ? 'var(--color-ink-900)' : 'var(--color-text-secondary)',
                boxShadow: categoryFilter === 'ALL' ? '0 1px 2px rgba(0,0,0,0.06)' : 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              All ({events.length})
            </button>

            <button
              onClick={() => setCategoryFilter('HEARING')}
              style={{
                background: categoryFilter === 'HEARING' ? 'var(--color-bg-surface)' : 'transparent',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '5px 10px',
                fontSize: '11px',
                fontWeight: 650,
                color: categoryFilter === 'HEARING' ? 'var(--color-ink-900)' : 'var(--color-text-secondary)',
                boxShadow: categoryFilter === 'HEARING' ? '0 1px 2px rgba(0,0,0,0.06)' : 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <span style={{ width: '7px', height: '7px', backgroundColor: 'var(--color-ink-900)', borderRadius: '1px' }} />
              Hearings ({countHearings})
            </button>

            <button
              onClick={() => setCategoryFilter('REMINDER')}
              style={{
                background: categoryFilter === 'REMINDER' ? 'var(--color-bg-surface)' : 'transparent',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '5px 10px',
                fontSize: '11px',
                fontWeight: 650,
                color: categoryFilter === 'REMINDER' ? '#92400E' : 'var(--color-text-secondary)',
                boxShadow: categoryFilter === 'REMINDER' ? '0 1px 2px rgba(0,0,0,0.06)' : 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <span style={{ width: '7px', height: '7px', backgroundColor: '#D97706', transform: 'rotate(45deg)' }} />
              Reminders ({countReminders})
            </button>

            <button
              onClick={() => setCategoryFilter('CLIENT')}
              style={{
                background: categoryFilter === 'CLIENT' ? 'var(--color-bg-surface)' : 'transparent',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '5px 10px',
                fontSize: '11px',
                fontWeight: 650,
                color: categoryFilter === 'CLIENT' ? 'var(--color-accent-700)' : 'var(--color-text-secondary)',
                boxShadow: categoryFilter === 'CLIENT' ? '0 1px 2px rgba(0,0,0,0.06)' : 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <span style={{ width: '7px', height: '7px', backgroundColor: 'var(--color-accent-700)', borderRadius: '50%' }} />
              Clients ({countClients})
            </button>
          </div>

          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() => setShowAddModal(true)}
          >
            Schedule Entry
          </Button>
        </div>
      </div>

      {/* Main Grid: Calendar (67%) and Day Inspector + Reminders (33%) */}
      <div style={{ display: 'grid', gridTemplateColumns: '67% 33%', gap: 'var(--space-md)' }} className="calendar-layout">
        
        {/* Left Column: Monthly Calendar View */}
        <div
          className="card-base"
          style={{
            padding: '16px',
            backgroundColor: 'var(--color-bg-surface)',
            borderRadius: 'var(--radius-lg, 10px)',
            border: '1px solid var(--color-border-subtle)',
            boxShadow: '0 1px 3px rgba(0,0,0,0.04)'
          }}
        >
          {/* Month Header & Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '20px', fontWeight: 700, color: 'var(--color-ink-900)', margin: 0 }}>
                {monthNames[month]} {year}
              </h2>
              {categoryFilter !== 'ALL' && (
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-full, 9999px)',
                    backgroundColor: 'var(--color-bg-surface-sunken)',
                    color: 'var(--color-ink-700)',
                    border: '1px solid var(--color-border-subtle)'
                  }}
                >
                  Filtered: {categoryFilter}
                </span>
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <button
                onClick={handlePrevMonth}
                aria-label="Previous month"
                style={{
                  background: 'none',
                  border: '1px solid var(--color-border-default)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '5px 8px',
                  cursor: 'pointer',
                  color: 'var(--color-ink-700)',
                  display: 'flex',
                  alignItems: 'center'
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
                  border: '1px solid var(--color-border-default)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '5px 12px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: 600,
                  color: 'var(--color-ink-900)'
                }}
              >
                Today (Sep 13)
              </button>
              <button
                onClick={handleNextMonth}
                aria-label="Next month"
                style={{
                  background: 'none',
                  border: '1px solid var(--color-border-default)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '5px 8px',
                  cursor: 'pointer',
                  color: 'var(--color-ink-700)',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>

          {/* Days of Week Header */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(7, 1fr)',
              textAlign: 'center',
              marginBottom: '4px',
              borderBottom: '1px solid var(--color-border-subtle)',
              paddingBottom: '6px'
            }}
          >
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((dayName, idx) => {
              const isWeekend = idx === 0 || idx === 6;
              return (
                <div
                  key={dayName}
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                    color: isWeekend ? 'var(--color-text-muted)' : 'var(--color-ink-700)',
                    padding: '2px 0'
                  }}
                >
                  {dayName}
                </div>
              );
            })}
          </div>

          {/* Month Cells Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(7, 1fr)',
              gap: '1px',
              backgroundColor: 'var(--color-border-subtle)',
              border: '1px solid var(--color-border-subtle)',
              borderRadius: 'var(--radius-sm, 6px)',
              overflow: 'hidden'
            }}
          >
            {calendarCells.map((cell, idx) => {
              const cellEvents = filteredEvents.filter(e => e.date === cell.dateStr);
              const isToday = cell.dateStr === '2026-09-13'; // Today per chambers scenario
              const isSelected = cell.dateStr === selectedDateStr;
              const hasUrgent = cellEvents.some(e => e.priority === 'urgent');

              return (
                <div
                  key={idx}
                  onClick={() => setSelectedDateStr(cell.dateStr)}
                  style={{
                    minHeight: '94px',
                    padding: '6px',
                    backgroundColor: isSelected
                      ? 'var(--color-accent-100)'
                      : isToday
                        ? '#F8FAFC'
                        : cell.isCurrentMonth
                          ? 'var(--color-bg-surface)'
                          : 'var(--color-bg-surface-sunken)',
                    border: isSelected ? '2px solid var(--color-ink-900)' : 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    transition: 'background-color 0.15s ease',
                    position: 'relative',
                    opacity: cell.isCurrentMonth ? 1 : 0.55
                  }}
                >
                  {/* Top Bar: Clean Day Number & Category Indicators */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '12px',
                        fontWeight: isToday || isSelected ? 700 : 500,
                        color: isToday
                          ? '#0D9488'
                          : isSelected
                            ? 'var(--color-ink-900)'
                            : cell.isCurrentMonth
                              ? 'var(--color-text-primary)'
                              : 'var(--color-text-muted)',
                        padding: isToday ? '1px 5px' : '0',
                        borderRadius: isToday ? '4px' : '0',
                        backgroundColor: isToday ? 'var(--color-accent-100)' : 'transparent'
                      }}
                    >
                      {cell.day}
                    </span>

                    {/* Styled Item Counter (Never bare floating number!) */}
                    {cellEvents.length > 0 && (
                      <span
                        style={{
                          fontSize: '9.5px',
                          fontWeight: 700,
                          padding: '1px 5px',
                          borderRadius: '8px',
                          backgroundColor: hasUrgent ? '#FEE2E2' : 'var(--color-bg-surface-sunken)',
                          color: hasUrgent ? '#B91C1C' : 'var(--color-ink-700)',
                          border: hasUrgent ? '1px solid #FCA5A5' : '1px solid var(--color-border-subtle)'
                        }}
                      >
                        {cellEvents.length}
                      </span>
                    )}
                  </div>

                  {/* Event indicator preview items */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', marginTop: '4px' }}>
                    {cellEvents.slice(0, 2).map((ev) => {
                      const isHearing = ev.eventType === 'hearing';
                      const isReminder = ev.eventType === 'reminder';
                      const isClient = ev.eventType === 'client_meeting';
                      const isUrgent = ev.priority === 'urgent';

                      let badgeBg = 'var(--color-bg-surface-sunken)';
                      let badgeColor = 'var(--color-ink-900)';
                      let badgeBorder = '1px solid var(--color-border-subtle)';

                      if (isHearing) {
                        badgeBg = '#1E293B';
                        badgeColor = '#FFFFFF';
                        badgeBorder = 'none';
                      } else if (isReminder) {
                        badgeBg = isUrgent ? '#FEF2F2' : '#FFFBEB';
                        badgeColor = isUrgent ? '#B91C1C' : '#92400E';
                        badgeBorder = isUrgent ? '1px solid #FECACA' : '1px solid #FDE68A';
                      } else if (isClient) {
                        badgeBg = '#F0FDF4';
                        badgeColor = '#166534';
                        badgeBorder = '1px solid #BBF7D0';
                      }

                      return (
                        <div
                          key={ev.id}
                          title={`${ev.time} — ${ev.title}`}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontSize: '10.5px',
                            fontWeight: 500,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            color: badgeColor,
                            backgroundColor: badgeBg,
                            border: badgeBorder,
                            padding: '2px 4px',
                            borderRadius: '3px',
                            lineHeight: 1.2
                          }}
                        >
                          {renderEventMarker(ev.eventType, ev.priority)}
                          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {ev.title}
                          </span>
                        </div>
                      );
                    })}

                    {cellEvents.length > 2 && (
                      <span
                        style={{
                          fontSize: '9.5px',
                          fontWeight: 600,
                          color: 'var(--color-accent-700)',
                          paddingLeft: '2px'
                        }}
                      >
                        +{cellEvents.length - 2} more
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Calendar Bottom Legend Bar */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginTop: '12px',
              paddingTop: '10px',
              borderTop: '1px solid var(--color-border-subtle)',
              fontSize: '11px',
              color: 'var(--color-text-secondary)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '8px', height: '8px', backgroundColor: 'var(--color-ink-900)', borderRadius: '1px' }} />
                Court Hearing
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '8px', height: '8px', backgroundColor: '#D97706', transform: 'rotate(45deg)' }} />
                Statutory Reminder
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '8px', height: '8px', backgroundColor: 'var(--color-accent-700)', borderRadius: '50%' }} />
                Client Meeting
              </span>
            </div>

            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
              Click any cell to inspect scheduled matter details
            </div>
          </div>
        </div>

        {/* Right Column: Day Docket + Dedicated Reminders Card */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          
          {/* 1. Day Docket Card */}
          <div
            className="card-base"
            style={{
              padding: '16px',
              backgroundColor: 'var(--color-bg-surface)',
              borderRadius: 'var(--radius-lg, 10px)',
              border: '1px solid var(--color-border-subtle)',
              boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <div style={{ borderBottom: '1px solid var(--color-border-subtle)', paddingBottom: '10px', marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Day Docket
                </span>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 650,
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-full, 9999px)',
                    backgroundColor: 'var(--color-bg-surface-sunken)',
                    color: 'var(--color-ink-700)'
                  }}
                >
                  {selectedDateEvents.length} {selectedDateEvents.length === 1 ? 'item' : 'items'}
                </span>
              </div>
              <div style={{ fontFamily: 'var(--font-serif)', fontSize: '17px', fontWeight: 700, color: 'var(--color-ink-900)', marginTop: '4px' }}>
                {formatHumanDate(selectedDateStr)}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '320px', overflowY: 'auto' }}>
              {selectedDateEvents.length === 0 ? (
                <div style={{ padding: '24px 12px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                  <CalendarIcon size={24} style={{ opacity: 0.35, marginBottom: '6px' }} />
                  <p style={{ fontSize: '13px', margin: 0 }}>No hearings or statutory reminders for this date.</p>
                  <button
                    onClick={() => {
                      setNewEventData(prev => ({ ...prev, date: selectedDateStr }));
                      setShowAddModal(true);
                    }}
                    style={{
                      marginTop: '10px',
                      background: 'none',
                      border: '1px solid var(--color-border-default)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '5px 12px',
                      fontSize: '11px',
                      fontWeight: 600,
                      color: 'var(--color-accent-700)',
                      cursor: 'pointer'
                    }}
                  >
                    + Add Entry for this Date
                  </button>
                </div>
              ) : (
                selectedDateEvents.map((evt) => {
                  const isHearing = evt.eventType === 'hearing';
                  const isReminder = evt.eventType === 'reminder';
                  const isUrgent = evt.priority === 'urgent';

                  return (
                    <div
                      key={evt.id}
                      style={{
                        padding: '12px',
                        backgroundColor: isReminder ? (isUrgent ? '#FEF2F2' : '#FFFBEB') : 'var(--color-bg-surface-sunken)',
                        borderRadius: 'var(--radius-md, 8px)',
                        borderLeft: isUrgent 
                          ? '3px solid #DC2626' 
                          : isHearing 
                            ? '3px solid var(--color-ink-900)' 
                            : '3px solid #D97706',
                        borderTop: '1px solid var(--color-border-subtle)',
                        borderRight: '1px solid var(--color-border-subtle)',
                        borderBottom: '1px solid var(--color-border-subtle)'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          {renderEventMarker(evt.eventType, evt.priority)}
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: 700, color: 'var(--color-ink-900)' }}>
                            {evt.time}
                          </span>
                        </div>

                        {evt.priority === 'urgent' && (
                          <span
                            style={{
                              fontSize: '9.5px',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              padding: '1px 6px',
                              borderRadius: 'var(--radius-xs)',
                              backgroundColor: '#FEE2E2',
                              color: '#991B1B'
                            }}
                          >
                            Urgent
                          </span>
                        )}
                      </div>

                      <div style={{ fontWeight: 650, fontSize: '13.5px', color: 'var(--color-ink-900)', marginBottom: '3px' }}>
                        {evt.title}
                      </div>

                      {evt.caseNumber && (
                        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-accent-700)', fontWeight: 600, marginBottom: '4px' }}>
                          Docket: #{evt.caseNumber}
                        </div>
                      )}

                      {evt.location && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11.5px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>
                          <MapPin size={11} style={{ flexShrink: 0 }} />
                          <span>{evt.court ? `${evt.court} — ${evt.location}` : evt.location}</span>
                        </div>
                      )}

                      {evt.description && (
                        <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: 1.45, margin: 0 }}>
                          {evt.description}
                        </p>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* 2. Dedicated Upcoming Statutory Deadlines & Limitation Reminders Panel */}
          <div
            className="card-base"
            style={{
              padding: '16px',
              backgroundColor: 'var(--color-bg-surface)',
              borderRadius: 'var(--radius-lg, 10px)',
              border: '1px solid var(--color-border-subtle)',
              boxShadow: '0 1px 3px rgba(0,0,0,0.04)'
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
                marginBottom: '10px',
                borderBottom: '1px solid var(--color-border-subtle)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertTriangle size={14} style={{ color: '#D97706' }} />
                <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--color-ink-900)' }}>
                  Statutory Limitation & Deadlines
                </span>
              </div>
              <span
                style={{
                  fontSize: '10px',
                  fontWeight: 700,
                  padding: '2px 6px',
                  borderRadius: 'var(--radius-xs)',
                  backgroundColor: '#FEF3C7',
                  color: '#92400E'
                }}
              >
                {allReminders.length} Active
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '280px', overflowY: 'auto' }}>
              {allReminders.map((rem) => {
                const isSelected = rem.date === selectedDateStr;
                const isUrgent = rem.priority === 'urgent';

                return (
                  <div
                    key={rem.id}
                    onClick={() => setSelectedDateStr(rem.date)}
                    style={{
                      padding: '8px 10px',
                      backgroundColor: isSelected ? 'var(--color-accent-100)' : 'var(--color-bg-canvas)',
                      borderRadius: 'var(--radius-sm)',
                      borderLeft: isUrgent ? '3px solid #DC2626' : '3px solid #D97706',
                      borderTop: '1px solid var(--color-border-subtle)',
                      borderRight: '1px solid var(--color-border-subtle)',
                      borderBottom: '1px solid var(--color-border-subtle)',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10.5px', fontWeight: 700, color: '#92400E' }}>
                        {rem.date} • {rem.time}
                      </span>
                      {isUrgent && (
                        <span style={{ fontSize: '9px', fontWeight: 700, color: '#B91C1C', textTransform: 'uppercase' }}>
                          Urgent
                        </span>
                      )}
                    </div>

                    <div style={{ fontSize: '12px', fontWeight: 650, color: 'var(--color-ink-900)', lineHeight: 1.3 }}>
                      {rem.title}
                    </div>

                    {rem.caseNumber && (
                      <div style={{ fontSize: '10.5px', fontFamily: 'var(--font-mono)', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                        Matter #{rem.caseNumber}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

        </div>

      </div>

      {/* Schedule Event & Reminder Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Schedule Hearing, Deadline or Reminder"
        subtitle="Book court appearances, statutory limitation deadlines, client briefs, or chamber reminders"
      >
        <form onSubmit={handleCreateSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Title / Matter Event <span style={{ color: 'var(--color-error-text)' }}>*</span>
            </label>
            <input
              type="text"
              required
              value={newEventData.title}
              onChange={(e) => setNewEventData(p => ({ ...p, title: e.target.value }))}
              placeholder="e.g. Limitation Notice Expiry or Injunction Hearing"
              className="input-base"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Date (YYYY-MM-DD) <span style={{ color: 'var(--color-error-text)' }}>*</span>
              </label>
              <input
                type="date"
                required
                value={newEventData.date}
                onChange={(e) => setNewEventData(p => ({ ...p, date: e.target.value }))}
                className="input-base"
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
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

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Event Category
              </label>
              <select
                value={newEventData.eventType}
                onChange={(e) => setNewEventData(p => ({ ...p, eventType: e.target.value }))}
                className="input-base"
              >
                <option value="reminder">Statutory Limitation / Filing Reminder</option>
                <option value="hearing">Court Hearing / Tribunal Appearance</option>
                <option value="client_meeting">Client Meeting / Conference</option>
                <option value="visitor">Visitor Enquiry / Consultation</option>
                <option value="personal">Chambers Task / Personal Event</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Priority Level
              </label>
              <select
                value={newEventData.priority}
                onChange={(e) => setNewEventData(p => ({ ...p, priority: e.target.value }))}
                className="input-base"
              >
                <option value="urgent">Urgent / Critical Limitation</option>
                <option value="normal">Standard Priority</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Associated Case File
              </label>
              <select
                value={newEventData.caseNumber}
                onChange={(e) => setNewEventData(p => ({ ...p, caseNumber: e.target.value }))}
                className="input-base"
              >
                <option value="2024-CV-1187">2024-CV-1187 (Martinez v. Coastal)</option>
                <option value="2024-CR-0442">2024-CR-0442 (State v. Whitfield)</option>
                <option value="2024-CC-0120">2024-CC-0120 (Apex v. Horizon)</option>
                <option value="2024-CV-0998">2024-CV-0998 (Nguyen Estate Probate)</option>
                <option value="">No Specific Case (General Chambers)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Court / Forum / Venue
              </label>
              <input
                type="text"
                value={newEventData.court}
                onChange={(e) => setNewEventData(p => ({ ...p, court: e.target.value }))}
                placeholder="e.g. High Court Commercial Bench"
                className="input-base"
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Specific Room / Location / Registry Counter
            </label>
            <input
              type="text"
              value={newEventData.location}
              onChange={(e) => setNewEventData(p => ({ ...p, location: e.target.value }))}
              placeholder="e.g. Courtroom 14, 2nd Floor or E-Filing Portal"
              className="input-base"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Procedural Description & Instructions
            </label>
            <textarea
              rows={3}
              value={newEventData.description}
              onChange={(e) => setNewEventData(p => ({ ...p, description: e.target.value }))}
              placeholder="Enter procedural tasks, limitation rules, or witness briefs..."
              className="input-base"
              style={{ resize: 'vertical' }}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-sm)', marginTop: '4px' }}>
            <Button variant="secondary" onClick={() => setShowAddModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Save to Calendar & Reminders
            </Button>
          </div>
        </form>
      </Modal>

      <style>{`
        @media (max-width: 960px) {
          .calendar-layout {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};
