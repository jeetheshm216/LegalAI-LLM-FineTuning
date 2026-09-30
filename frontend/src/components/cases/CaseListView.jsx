import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Plus, 
  Flag, 
  LayoutList, 
  LayoutGrid, 
  SlidersHorizontal,
  ChevronDown,
  Scale,
  Calendar,
  AlertCircle,
  TrendingUp,
  ShieldAlert,
  Zap,
  Clock,
  Sparkles,
  Info
} from 'lucide-react';
import { Button } from '../common/Button';
import { CaseStatusBadge } from '../common/Badge';

export const CaseListView = ({ 
  cases = [], 
  onSelectCase, 
  onOpenAddCase 
}) => {
  const [viewMode, setViewMode] = useState('table'); // 'table' | 'card'
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  const filteredCases = useMemo(() => {
    return cases.filter(c => {
      const q = searchQuery.toLowerCase();
      const matchesSearch = 
        c.title.toLowerCase().includes(q) ||
        (c.caseNumber && c.caseNumber.toLowerCase().includes(q)) ||
        (c.client && c.client.toLowerCase().includes(q)) ||
        (c.court && c.court.toLowerCase().includes(q)) ||
        (c.claimAmount && c.claimAmount.toLowerCase().includes(q));

      const matchesStatus = statusFilter === 'ALL' || (c.status && c.status.toLowerCase() === statusFilter.toLowerCase());
      const matchesPriority = priorityFilter === 'ALL' || 
        (c.priority && c.priority.toLowerCase() === priorityFilter.toLowerCase()) ||
        (c.calculatedPriority && c.calculatedPriority.toLowerCase().includes(priorityFilter.toLowerCase()));

      return matchesSearch && matchesStatus && matchesPriority;
    });
  }, [cases, searchQuery, statusFilter, priorityFilter]);

  const statuses = ['ALL', 'Active', 'Urgent', 'Pending', 'Upcoming'];

  const getPriorityBadge = (c) => {
    const score = c.priorityScore || (c.priority === 'urgent' ? 90 : 50);
    const tier = c.calculatedPriority || (score >= 75 ? 'P1 - Critical' : score >= 55 ? 'P2 - High' : 'P3 - Medium');

    if (score >= 75) {
      return (
        <span 
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '3px 8px',
            borderRadius: '12px',
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.35)',
            color: '#F87171',
            fontSize: '11px',
            fontWeight: 700,
            letterSpacing: '0.02em',
            whiteSpace: 'nowrap'
          }}
          title={c.urgencyFactors?.keyReason || `Multi-Factor Score: ${score}/100. Critical proximity & high relief risk.`}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#EF4444' }} />
          P1 Critical · {score}
        </span>
      );
    } else if (score >= 55) {
      return (
        <span 
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '3px 8px',
            borderRadius: '12px',
            backgroundColor: 'rgba(245, 158, 11, 0.15)',
            border: '1px solid rgba(245, 158, 11, 0.35)',
            color: '#FBBF24',
            fontSize: '11px',
            fontWeight: 700,
            whiteSpace: 'nowrap'
          }}
          title={c.urgencyFactors?.keyReason || `Multi-Factor Score: ${score}/100. High financial exposure.`}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#F59E0B' }} />
          P2 High · {score}
        </span>
      );
    } else {
      return (
        <span 
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '3px 8px',
            borderRadius: '12px',
            backgroundColor: 'rgba(14, 165, 233, 0.12)',
            border: '1px solid rgba(14, 165, 233, 0.3)',
            color: '#38BDF8',
            fontSize: '11px',
            fontWeight: 650,
            whiteSpace: 'nowrap'
          }}
          title={c.urgencyFactors?.keyReason || `Multi-Factor Score: ${score}/100.`}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#0284C7' }} />
          P3 Medium · {score}
        </span>
      );
    }
  };

  return (
    <div className="container" style={{ paddingTop: 'var(--space-xl)', paddingBottom: 'var(--space-2xl)' }}>
      {/* Top Header Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h1)', color: 'var(--color-text-primary)', margin: 0 }}>
              Matters & Cases
            </h1>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '2px 8px',
              borderRadius: '10px',
              fontSize: '11px',
              fontWeight: 600,
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              color: '#34D399',
              border: '1px solid rgba(16, 185, 129, 0.3)'
            }}>
              <Sparkles size={11} /> AI Priority Engine Active
            </span>
          </div>
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '4px', marginBottom: 0 }}>
            {filteredCases.length} matters prioritized dynamically by hearing proximity, financial stake, and relief urgency
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          icon={Plus}
          onClick={onOpenAddCase}
        >
          Add Case
        </Button>
      </div>

      {/* Toolbar: Search, Filters, View Mode */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 'var(--space-md)',
          marginBottom: 'var(--space-md)',
          padding: 'var(--space-sm) var(--space-md)',
          backgroundColor: 'var(--color-bg-surface)',
          border: '1px solid var(--color-border-subtle)',
          borderRadius: 'var(--radius-lg)'
        }}
      >
        {/* Left: Search input */}
        <div style={{ position: 'relative', width: '320px', maxWidth: '100%' }}>
          <Search 
            size={16} 
            color="var(--color-text-muted)" 
            style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} 
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search matters, numbers, clients, stakes…"
            className="input-base"
            style={{
              paddingLeft: '34px',
              paddingTop: '6px',
              paddingBottom: '6px',
              fontSize: 'var(--text-caption)'
            }}
          />
        </div>

        {/* Center: Status filter pills */}
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
          {statuses.map((st) => {
            const isSelected = statusFilter === st;
            return (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                style={{
                  padding: '5px 12px',
                  borderRadius: 'var(--radius-md)',
                  border: isSelected ? '1px solid var(--color-ink-700)' : '1px solid transparent',
                  backgroundColor: isSelected ? 'var(--color-bg-surface-sunken)' : 'transparent',
                  color: isSelected ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                  fontWeight: isSelected ? 600 : 400,
                  fontSize: 'var(--text-caption)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {st === 'ALL' ? 'All Statuses' : st}
              </button>
            );
          })}
        </div>

        {/* Right: Table vs Card View Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button
            onClick={() => setViewMode('table')}
            aria-label="Table view"
            style={{
              padding: '6px',
              borderRadius: 'var(--radius-sm)',
              border: viewMode === 'table' ? '1px solid var(--color-ink-700)' : '1px solid transparent',
              backgroundColor: viewMode === 'table' ? 'var(--color-bg-surface-sunken)' : 'transparent',
              color: 'var(--color-text-primary)',
              cursor: 'pointer'
            }}
          >
            <LayoutList size={16} />
          </button>
          <button
            onClick={() => setViewMode('card')}
            aria-label="Card view"
            style={{
              padding: '6px',
              borderRadius: 'var(--radius-sm)',
              border: viewMode === 'card' ? '1px solid var(--color-ink-700)' : '1px solid transparent',
              backgroundColor: viewMode === 'card' ? 'var(--color-bg-surface-sunken)' : 'transparent',
              color: 'var(--color-text-primary)',
              cursor: 'pointer'
            }}
          >
            <LayoutGrid size={16} />
          </button>
        </div>
      </div>

      {/* Main Content: Table or Cards */}
      {filteredCases.length === 0 ? (
        <div className="card-base" style={{ padding: 'var(--space-2xl) var(--space-md)', textAlign: 'center' }}>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-body)' }}>
            No results found matching your search or filters.
          </p>
          <button
            onClick={() => { setSearchQuery(''); setStatusFilter('ALL'); }}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-text-link)',
              marginTop: 'var(--space-xs)',
              cursor: 'pointer',
              fontSize: 'var(--text-caption)'
            }}
          >
            Clear filters
          </button>
        </div>
      ) : viewMode === 'table' ? (
        /* Table View */
        <div className="card-base" style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface-sunken)' }}>
                <th style={{ padding: '12px 14px', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                  Case Docket
                </th>
                <th style={{ padding: '12px 14px', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                  Matter & Client
                </th>
                <th style={{ padding: '12px 14px', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                  Financial Stakes / Claim
                </th>
                <th style={{ padding: '12px 14px', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                  Forum / Court
                </th>
                <th style={{ padding: '12px 14px', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                  Lawyer Status
                </th>
                <th style={{ padding: '12px 14px', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', textAlign: 'center' }}>
                  AI Priority Intelligence
                </th>
                <th style={{ padding: '12px 14px', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', textAlign: 'right' }}>
                  Next Hearing
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredCases.map((c) => (
                <tr
                  key={c.id}
                  onClick={() => onSelectCase(c)}
                  className="legal-table-row"
                  style={{
                    height: '58px',
                    borderBottom: '1px solid var(--color-border-subtle)',
                    cursor: 'pointer',
                    transition: 'background-color 0.15s ease'
                  }}
                >
                  <td style={{ padding: '12px 14px', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--color-ink-700)', fontWeight: 600, whiteSpace: 'nowrap' }}>
                    {c.caseNumber}
                  </td>
                  <td style={{ padding: '12px 14px', minWidth: '220px' }}>
                    <div style={{ fontWeight: 600, fontSize: '13.5px', color: 'var(--color-text-primary)' }}>
                      {c.title}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                      Client: {c.client}
                    </div>
                  </td>
                  <td style={{ padding: '12px 14px', whiteSpace: 'nowrap' }}>
                    <div style={{ fontWeight: 700, fontSize: '12.5px', color: 'var(--color-text-primary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      {c.claimAmount || 'Unspecified'}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {c.reliefSought || c.caseType}
                    </div>
                  </td>
                  <td style={{ padding: '12px 14px', fontSize: '12px', color: 'var(--color-text-secondary)', maxWidth: '190px' }}>
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={c.court}>
                      {c.court}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      {c.caseType}
                    </div>
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <CaseStatusBadge status={c.status} />
                  </td>
                  <td style={{ padding: '12px 14px', textAlign: 'center' }}>
                    {getPriorityBadge(c)}
                  </td>
                  <td style={{ padding: '12px 14px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                    <div style={{
                      fontWeight: c.hearingCountdownDays <= 2 ? 700 : 500,
                      color: c.hearingCountdownDays <= 2 ? '#EF4444' : 'var(--color-text-primary)',
                      fontSize: '12px'
                    }}>
                      {c.nextHearing || 'None scheduled'}
                    </div>
                    {c.hearingCountdownDays !== null && c.hearingCountdownDays !== undefined && (
                      <span style={{
                        fontSize: '10.5px',
                        padding: '1px 6px',
                        borderRadius: '4px',
                        backgroundColor: c.hearingCountdownDays <= 2 ? 'rgba(239, 68, 68, 0.15)' : 'var(--color-bg-surface-sunken)',
                        color: c.hearingCountdownDays <= 2 ? '#F87171' : 'var(--color-text-muted)',
                        display: 'inline-block',
                        marginTop: '2px'
                      }}>
                        {c.hearingCountdownDays === 1 ? 'Tomorrow' : `in ${c.hearingCountdownDays}d`}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        /* Card Grid View */
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 'var(--space-md)' }}>
          {filteredCases.map((c) => (
            <div
              key={c.id}
              onClick={() => onSelectCase(c)}
              className="card-base"
              style={{
                padding: 'var(--space-md)',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11.5px', color: 'var(--color-ink-700)', fontWeight: 600 }}>
                    {c.caseNumber}
                  </span>
                  {getPriorityBadge(c)}
                </div>

                <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--color-text-primary)', margin: '0 0 6px 0', lineHeight: 1.3 }}>
                  {c.title}
                </h3>

                <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', margin: '0 0 12px 0' }}>
                  Client: <strong style={{ color: 'var(--color-text-primary)' }}>{c.client}</strong>
                </p>

                <div style={{
                  padding: '8px 10px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--color-bg-surface-sunken)',
                  marginBottom: '12px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', display: 'block' }}>
                      Claim / Stakes
                    </span>
                    <strong style={{ fontSize: '12.5px', color: 'var(--color-text-primary)' }}>
                      {c.claimAmount || 'Unspecified'}
                    </strong>
                  </div>
                  <CaseStatusBadge status={c.status} />
                </div>

                <div style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '3px' }}>
                    <Scale size={13} color="var(--color-text-muted)" />
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.court}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <Calendar size={13} color="var(--color-text-muted)" />
                    <span>Next: <strong>{c.nextHearing || 'None scheduled'}</strong></span>
                  </div>
                </div>
              </div>

              <div style={{
                borderTop: '1px solid var(--color-border-subtle)',
                paddingTop: '8px',
                marginTop: '8px',
                fontSize: '11px',
                color: 'var(--color-text-muted)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span>{c.caseType}</span>
                <span style={{ color: 'var(--color-text-link)', fontWeight: 600 }}>Open File →</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
