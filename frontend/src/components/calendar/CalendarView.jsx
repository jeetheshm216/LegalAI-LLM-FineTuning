import React, { useState } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon, 
  Clock, 
  MapPin, 
  Plus,
  AlertCircle
} from 'lucide-react';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';

export const CalendarView = ({ events, onAddEvent }) => {
  const [currentMonthDate, setCurrentMonthDate] = useState(new Date(2026, 8, 1)); // September 2026
  const [selectedDateStr, setSelectedDateStr] = useState('2026-09-17');
  const [viewMode, setViewMode] = useState('month'); // 'month' | 'week'
  const [showAddModal, setShowAddModal] = useState(false);
  const [newEventData, setNewEventData] = useState({
    title: '',
    date: '2026-09-22',
    time: '10:00 AM',
    eventType: 'hearing',
    court: '',
    location: '',
    priority: 'normal'
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

  // Calendar Grid Generation for 35 or 42 cells
  const firstDayIndex = new Date(year, month, 1).getDay(); // 0 = Sun
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();

  const calendarCells = [];
  // Prev month padding
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    const day = daysInPrevMonth - i;
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    calendarCells.push({ day, isCurrentMonth: false, dateStr });
  }
  // Current month days
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    calendarCells.push({ day: d, isCurrentMonth: true, dateStr });
  }
  // Next month padding
  const remaining = 35 - calendarCells.length;
  for (let n = 1; n <= (remaining > 0 ? remaining : 42 - calendarCells.length); n++) {
    const dateStr = `${year}-${String(month + 2).padStart(2, '0')}-${String(n).padStart(2, '0')}`;
    calendarCells.push({ day: n, isCurrentMonth: false, dateStr });
  }

  // Marker Render helper matching §13.1
  const renderShapeMarker = (type) => {
    switch (type) {
      case 'hearing':
        // Solid filled square marker, --color-ink-700
        return (
          <span
            style={{
              width: '8px',
              height: '8px',
              backgroundColor: 'var(--color-ink-700)',
              borderRadius: '0px',
              display: 'inline-block',
              flexShrink: 0
            }}
            title="Court Hearing / Court Date"
          />
        );
      case 'client_meeting':
        // Solid filled circle marker, --color-ai-500
        return (
          <span
            style={{
              width: '8px',
              height: '8px',
              backgroundColor: 'var(--color-ai-500)',
              borderRadius: '50%',
              display: 'inline-block',
              flexShrink: 0
            }}
            title="Client Meeting"
          />
        );
      case 'visitor':
        // Outline circle marker, --color-information
        return (
          <span
            style={{
              width: '8px',
              height: '8px',
              border: '1.5px solid var(--color-information-text)',
              borderRadius: '50%',
              display: 'inline-block',
              flexShrink: 0
            }}
            title="Visitor / Enquiry"
          />
        );
      case 'personal':
        // Outline square marker, --color-text-muted
        return (
          <span
            style={{
              width: '8px',
              height: '8px',
              border: '1.5px solid var(--color-text-muted)',
              borderRadius: '0px',
              display: 'inline-block',
              flexShrink: 0
            }}
            title="Personal Event"
          />
        );
      case 'reminder':
      default:
        // Small diamond marker, --color-warning
        return (
          <span
            style={{
              width: '7px',
              height: '7px',
              backgroundColor: 'var(--color-warning-text)',
              transform: 'rotate(45deg)',
              display: 'inline-block',
              flexShrink: 0
            }}
            title="Deadline Reminder"
          />
        );
    }
  };

  const selectedDateEvents = events.filter(e => e.date === selectedDateStr);

  const handleCreateSubmit = (e) => {
    e.preventDefault();
    if (!newEventData.title) return;
    onAddEvent(newEventData);
    setShowAddModal(false);
  };

  return (
    <div className="container" style={{ padding: 'var(--space-xl) var(--space-md)' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 'var(--space-md)', marginBottom: 'var(--space-lg)' }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h1)', color: 'var(--color-text-primary)' }}>
            Chambers Court & Hearing Calendar
          </h1>
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            Multi-tribunal hearing lists, depositions, client sessions, and statutory limitation deadlines
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
          {/* Legend Summary */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', paddingRight: 'var(--space-sm)' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              {renderShapeMarker('hearing')} Hearing
            </span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              {renderShapeMarker('client_meeting')} Client
            </span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              {renderShapeMarker('reminder')} Reminder
            </span>
          </div>

          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() => setShowAddModal(true)}
          >
            Schedule
          </Button>
        </div>
      </div>

      {/* Main Grid: Calendar (70%) and Day Inspector (30%) */}
      <div style={{ display: 'grid', gridTemplateColumns: '68% 32%', gap: 'var(--space-lg)' }} className="calendar-layout">
        
        {/* Left: Monthly Calendar Chrome (§13.2) */}
        <div className="card-base" style={{ padding: 'var(--space-md)' }}>
          {/* Month Bar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
              <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)' }}>
                {monthNames[month]} {year}
              </h2>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <button
                onClick={handlePrevMonth}
                aria-label="Previous month"
                style={{
                  background: 'none',
                  border: '1px solid var(--color-border-default)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '4px 8px',
                  cursor: 'pointer',
                  color: 'var(--color-text-primary)'
                }}
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={() => {
                  setCurrentMonthDate(new Date(2026, 8, 1));
                  setSelectedDateStr('2026-09-13');
                }}
                style={{
                  background: 'none',
                  border: '1px solid var(--color-border-default)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '4px 10px',
                  cursor: 'pointer',
                  fontSize: 'var(--text-caption)',
                  color: 'var(--color-text-secondary)'
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
                  padding: '4px 8px',
                  cursor: 'pointer',
                  color: 'var(--color-text-primary)'
                }}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>

          {/* Days of Week Header */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', textAlign: 'center', marginBottom: '8px' }}>
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d) => (
              <div key={d} style={{ fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', padding: '4px 0' }}>
                {d}
              </div>
            ))}
          </div>

          {/* Month Cells Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '1px', backgroundColor: 'var(--color-border-subtle)', border: '1px solid var(--color-border-subtle)', borderRadius: 'var(--radius-sm)', overflow: 'hidden' }}>
            {calendarCells.map((cell, idx) => {
              const cellEvents = events.filter(e => e.date === cell.dateStr);
              const isToday = cell.dateStr === '2026-09-13'; // Today per timeline context
              const isSelected = cell.dateStr === selectedDateStr;

              return (
                <div
                  key={idx}
                  onClick={() => setSelectedDateStr(cell.dateStr)}
                  style={{
                    minHeight: '84px',
                    padding: '6px',
                    backgroundColor: isToday 
                      ? 'var(--color-accent-100)' // Today: --color-accent-100 wash (§13.2)
                      : cell.isCurrentMonth 
                        ? 'var(--color-bg-surface)' 
                        : 'var(--color-bg-surface-sunken)',
                    border: isSelected ? '2px solid var(--color-ink-700)' : 'none', // Selected date border (§13.2)
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '12px',
                        fontWeight: isToday ? 700 : 500,
                        color: isToday 
                          ? 'var(--color-accent-700)' // Today number: --color-accent-700 (§13.2)
                          : cell.isCurrentMonth 
                            ? 'var(--color-text-primary)' 
                            : 'var(--color-text-muted)'
                      }}
                    >
                      {cell.day}
                    </span>
                    {cellEvents.length > 0 && (
                      <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
                        {cellEvents.length}
                      </span>
                    )}
                  </div>

                  {/* Event indicator preview */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', marginTop: '4px' }}>
                    {cellEvents.slice(0, 2).map((ev) => (
                      <div
                        key={ev.id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '11px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          color: 'var(--color-text-primary)',
                          backgroundColor: 'var(--color-bg-surface-sunken)',
                          padding: '1px 4px',
                          borderRadius: 'var(--radius-sm)'
                        }}
                      >
                        {renderShapeMarker(ev.eventType)}
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{ev.title}</span>
                      </div>
                    ))}
                    {cellEvents.length > 2 && (
                      <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
                        +{cellEvents.length - 2} more
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Selected Date Event Inspector */}
        <div className="card-base" style={{ padding: 'var(--space-md)', display: 'flex', flexDirection: 'column' }}>
          <div style={{ borderBottom: '1px solid var(--color-border-subtle)', paddingBottom: 'var(--space-sm)', marginBottom: 'var(--space-md)' }}>
            <span style={{ fontSize: 'var(--text-label)', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Day Docket
            </span>
            <div style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)', marginTop: '2px' }}>
              {selectedDateStr}
            </div>
            <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
              {selectedDateEvents.length} item{selectedDateEvents.length === 1 ? '' : 's'} scheduled
            </div>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
            {selectedDateEvents.length === 0 ? (
              <div style={{ padding: 'var(--space-xl) 0', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: 'var(--text-caption)' }}>
                No hearings or meetings recorded for this date.
              </div>
            ) : (
              selectedDateEvents.map((evt) => {
                const isUrgent = evt.priority === 'urgent';
                return (
                  <div
                    key={evt.id}
                    style={{
                      padding: 'var(--space-sm)',
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      borderRadius: 'var(--radius-md)',
                      borderLeft: isUrgent ? '3px solid var(--color-case-urgent-text)' : '1px solid var(--color-border-subtle)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                      {renderShapeMarker(evt.eventType)}
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: 600, color: 'var(--color-ink-700)' }}>
                        {evt.time}
                      </span>
                    </div>

                    <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)', marginBottom: '2px' }}>
                      {evt.title}
                    </div>

                    {evt.caseNumber && (
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
                        Docket: #{evt.caseNumber}
                      </div>
                    )}

                    {evt.location && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                        <MapPin size={12} />
                        <span>{evt.court ? `${evt.court} — ${evt.location}` : evt.location}</span>
                      </div>
                    )}

                    <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
                      {evt.description}
                    </p>
                  </div>
                );
              })
            )}
          </div>
        </div>

      </div>

      {/* Schedule Event Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Schedule Hearing or Conference"
        subtitle="Book court appearances, client briefs, or statutory limitation reminders"
      >
        <form onSubmit={handleCreateSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Title / Matter Event <span style={{ color: 'var(--color-error-text)' }}>*</span>
            </label>
            <input
              type="text"
              required
              value={newEventData.title}
              onChange={(e) => setNewEventData(p => ({ ...p, title: e.target.value }))}
              placeholder="e.g. Cross-examination of Attesting Witness"
              className="input-base"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Date (YYYY-MM-DD)
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
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
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
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Event Category
              </label>
              <select
                value={newEventData.eventType}
                onChange={(e) => setNewEventData(p => ({ ...p, eventType: e.target.value }))}
                className="input-base"
              >
                <option value="hearing">Court Hearing (Square Marker)</option>
                <option value="client_meeting">Client Meeting (Circle Marker)</option>
                <option value="visitor">Visitor Enquiry (Outline Circle)</option>
                <option value="reminder">Statutory Deadline (Diamond Marker)</option>
                <option value="personal">Personal / Bar Assoc (Outline Square)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Priority
              </label>
              <select
                value={newEventData.priority}
                onChange={(e) => setNewEventData(p => ({ ...p, priority: e.target.value }))}
                className="input-base"
              >
                <option value="normal">Standard</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Courtroom / Location
            </label>
            <input
              type="text"
              value={newEventData.location}
              onChange={(e) => setNewEventData(p => ({ ...p, location: e.target.value }))}
              placeholder="e.g. Courtroom 14, Commercial Division"
              className="input-base"
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-sm)' }}>
            <Button variant="secondary" onClick={() => setShowAddModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Save Entry
            </Button>
          </div>
        </form>
      </Modal>

      <style>{`
        @media (max-width: 900px) {
          .calendar-layout {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};
