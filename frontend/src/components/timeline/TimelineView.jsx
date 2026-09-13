import React, { useState } from 'react';
import { 
  Plus, 
  ChevronDown, 
  ChevronUp, 
  FileText, 
  Calendar as CalendarIcon, 
  Sparkles, 
  MessageSquare,
  Award,
  Clock
} from 'lucide-react';
import { Button } from '../common/Button';

export const TimelineView = ({ 
  caseId, 
  timelineEvents, 
  onAddTimelineEvent 
}) => {
  const [expandedNodes, setExpandedNodes] = useState({ 'time-01': true }); // First node open by default
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEventTitle, setNewEventTitle] = useState('');
  const [newEventType, setNewEventType] = useState('note');
  const [newEventSummary, setNewEventSummary] = useState('');

  const toggleNode = (id) => {
    setExpandedNodes(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleAddSubmit = (e) => {
    e.preventDefault();
    if (!newEventTitle.trim()) return;

    onAddTimelineEvent({
      caseId,
      title: newEventTitle,
      eventType: newEventType,
      summary: newEventSummary,
      details: newEventSummary,
      isAI: false
    });

    setNewEventTitle('');
    setNewEventSummary('');
    setShowAddForm(false);
  };

  const getEventIcon = (type, isAI) => {
    if (isAI) return <Sparkles size={12} color="#FFFFFF" />;
    switch (type) {
      case 'hearing':
        return <CalendarIcon size={12} color="#FFFFFF" />;
      case 'order':
        return <Award size={12} color="#FFFFFF" />;
      case 'document':
        return <FileText size={12} color="#FFFFFF" />;
      case 'meeting':
        return <MessageSquare size={12} color="#FFFFFF" />;
      default:
        return <Clock size={12} color="#FFFFFF" />;
    }
  };

  return (
    <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xl)' }}>
        <div>
          <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)' }}>
            Procedural & Case Timeline
          </h3>
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            Verified sequence of orders, filings, conferences, and AI synthesized analyses
          </p>
        </div>

        <Button
          variant="secondary"
          size="sm"
          icon={Plus}
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? "Cancel" : "Add Event"}
        </Button>
      </div>

      {/* Optional Add Event Mini-Form */}
      {showAddForm && (
        <form
          onSubmit={handleAddSubmit}
          style={{
            marginBottom: 'var(--space-xl)',
            padding: 'var(--space-md)',
            backgroundColor: 'var(--color-bg-surface-sunken)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-border-default)'
          }}
        >
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-sm)', marginBottom: 'var(--space-sm)' }}>
            <input
              type="text"
              value={newEventTitle}
              onChange={(e) => setNewEventTitle(e.target.value)}
              placeholder="Event title (e.g. Received Cross-Affidavit)"
              className="input-base"
              required
            />
            <select
              value={newEventType}
              onChange={(e) => setNewEventType(e.target.value)}
              className="input-base"
            >
              <option value="note">Internal Note</option>
              <option value="hearing">Court Hearing</option>
              <option value="order">Judicial Order</option>
              <option value="document">Pleading / Filing</option>
              <option value="meeting">Client Meeting</option>
            </select>
          </div>
          <textarea
            rows={2}
            value={newEventSummary}
            onChange={(e) => setNewEventSummary(e.target.value)}
            placeholder="Details, observations, or next procedural action…"
            className="input-base"
            style={{ marginBottom: 'var(--space-sm)', resize: 'vertical' }}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-xs)' }}>
            <Button variant="primary" size="sm" type="submit">
              Save to Timeline
            </Button>
          </div>
        </form>
      )}

      {/* Timeline Stream (§14) */}
      <div style={{ position: 'relative', paddingLeft: '180px' }} className="timeline-container">
        {/* Continuous 1px Vertical Connector Line */}
        <div
          style={{
            position: 'absolute',
            left: '180px',
            top: '8px',
            bottom: '12px',
            width: '1px',
            backgroundColor: 'var(--color-border-default)',
            transform: 'translateX(-50%)'
          }}
          className="timeline-vertical-line"
        />

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
          {timelineEvents.map((event) => {
            const isExpanded = !!expandedNodes[event.id];
            const isAI = event.isAI;

            return (
              <div key={event.id} style={{ position: 'relative' }}>
                {/* Monospace Timestamp (§14) positioned left of the connector */}
                <div
                  className="timeline-timestamp"
                  style={{
                    position: 'absolute',
                    right: 'calc(100% + var(--space-lg))',
                    top: '0px',
                    width: '160px',
                    textAlign: 'right',
                    fontFamily: 'var(--font-mono)',
                    fontSize: 'var(--text-caption)',
                    color: 'var(--color-text-muted)',
                    lineHeight: '1.3'
                  }}
                >
                  <div style={{ color: 'var(--color-text-secondary)', fontWeight: 500 }}>
                    {event.timestamp.split(' ')[0]}
                  </div>
                  <div style={{ fontSize: '11px' }}>
                    {event.relativeTime}
                  </div>
                </div>

                {/* Square 12px Node Marker (§14) */}
                <div
                  onClick={() => toggleNode(event.id)}
                  style={{
                    position: 'absolute',
                    left: '-6px',
                    top: '4px',
                    width: '14px',
                    height: '14px',
                    borderRadius: '0px', // Square-cornered per §14!
                    backgroundColor: isAI ? 'var(--color-ai-500)' : 'var(--color-ink-500)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 0 0 3px var(--color-bg-surface)',
                    zIndex: 2
                  }}
                  title={isAI ? "AI Synthesis Entry" : "Chambers Entry"}
                />

                {/* Content Box */}
                <div style={{ marginLeft: 'var(--space-md)' }}>
                  <div
                    onClick={() => toggleNode(event.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'baseline',
                      justifyContent: 'space-between',
                      cursor: 'pointer'
                    }}
                  >
                    <div>
                      <span style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                        {event.title}
                      </span>
                      {isAI && (
                        <span
                          style={{
                            marginLeft: 'var(--space-xs)',
                            fontSize: '11px',
                            backgroundColor: 'var(--color-ai-100)',
                            color: 'var(--color-ai-500)',
                            padding: '1px 6px',
                            borderRadius: 'var(--radius-sm)',
                            fontWeight: 500
                          }}
                        >
                          AI Synthesis
                        </span>
                      )}
                    </div>
                    <button
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--color-text-muted)',
                        cursor: 'pointer',
                        padding: '2px'
                      }}
                      aria-label="Expand event details"
                    >
                      {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                    </button>
                  </div>

                  <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px', lineHeight: 1.5 }}>
                    {event.summary}
                  </p>

                  {/* Expandable Panel (§14: AI analysis gets --color-ai-border left accent) */}
                  {isExpanded && (
                    <div
                      style={{
                        marginTop: 'var(--space-xs)',
                        padding: 'var(--space-sm)',
                        backgroundColor: 'var(--color-bg-surface-sunken)',
                        borderRadius: 'var(--radius-md)',
                        borderLeft: isAI ? '2px solid var(--color-ai-border)' : '1px solid var(--color-border-subtle)',
                        fontSize: 'var(--text-caption)',
                        color: 'var(--color-text-primary)',
                        lineHeight: 1.6
                      }}
                    >
                      <div style={{ marginBottom: event.relatedDocument ? 'var(--space-xs)' : 0 }}>
                        {event.details}
                      </div>

                      {event.relatedDocument && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--color-text-link)', marginTop: '6px' }}>
                          <FileText size={12} />
                          <span>Related file: <strong>{event.relatedDocument}</strong></span>
                        </div>
                      )}
                    </div>
                  )}
                </div>

              </div>
            );
          })}
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .timeline-container {
            padding-left: 20px !important;
          }
          .timeline-vertical-line {
            left: 20px !important;
          }
          .timeline-timestamp {
            position: static !important;
            width: auto !important;
            text-align: left !important;
            margin-bottom: 4px;
          }
        }
      `}</style>
    </div>
  );
};
