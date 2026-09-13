import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Plus, 
  Flag, 
  LayoutList, 
  LayoutGrid, 
  SlidersHorizontal,
  ChevronDown
} from 'lucide-react';
import { Button } from '../common/Button';
import { CaseStatusBadge } from '../common/Badge';

export const CaseListView = ({ 
  cases, 
  onSelectCase, 
  onOpenAddCase 
}) => {
  const [viewMode, setViewMode] = useState('table'); // 'table' | 'card'
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('updated');

  const filteredCases = useMemo(() => {
    return cases.filter(c => {
      const matchesSearch = 
        c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.caseNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.court.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesStatus = statusFilter === 'ALL' || c.status.toLowerCase() === statusFilter.toLowerCase();
      const matchesPriority = priorityFilter === 'ALL' || c.priority === priorityFilter;

      return matchesSearch && matchesStatus && matchesPriority;
    });
  }, [cases, searchQuery, statusFilter, priorityFilter]);

  const statuses = ['ALL', 'Active', 'Urgent', 'Pending', 'Upcoming', 'Closed'];

  return (
    <div className="container" style={{ padding: 'var(--space-xl) var(--space-md)' }}>
      {/* Top Header Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h1)', color: 'var(--color-text-primary)' }}>
            Matters & Cases
          </h1>
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            {filteredCases.length} matters under active management
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

      {/* Toolbar: Search, Filters, View Mode (§10.4) */}
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
        {/* Left: Search input (320px desktop) */}
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
            placeholder="Search matters, numbers, clients, courts…"
            className="input-base"
            style={{
              paddingLeft: '34px',
              paddingTop: '6px',
              paddingBottom: '6px',
              fontSize: 'var(--text-caption)'
            }}
          />
        </div>

        {/* Center: Filter Chips (selected chip gets verdigris wash + accent border per §10.4) */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2xs)', overflowX: 'auto' }}>
          {statuses.map((st) => {
            const isSelected = statusFilter === st;
            return (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                style={{
                  padding: '4px 10px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-caption)',
                  fontWeight: isSelected ? 600 : 400,
                  cursor: 'pointer',
                  border: isSelected ? '1px solid var(--color-accent-500)' : '1px solid var(--color-border-default)',
                  backgroundColor: isSelected ? 'var(--color-accent-100)' : 'var(--color-bg-surface)',
                  color: isSelected ? 'var(--color-accent-700)' : 'var(--color-text-secondary)',
                  transition: 'all var(--duration-fast) var(--easing-standard)'
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
        /* Table View (§10.1): 56px row height, horizontal borders only, sentence-case column labels */
        <div className="card-base" style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface-sunken)' }}>
                <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                  Case number
                </th>
                <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                  Matter & Client
                </th>
                <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                  Status
                </th>
                <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                  Court & Division
                </th>
                <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                  Case type
                </th>
                <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', textAlign: 'center' }}>
                  Priority
                </th>
                <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', textAlign: 'right' }}>
                  Next hearing
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
                    height: '56px',
                    borderBottom: '1px solid var(--color-border-subtle)',
                    cursor: 'pointer',
                    transition: 'background-color var(--duration-instant) var(--easing-standard)'
                  }}
                >
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-mono)', color: 'var(--color-ink-700)', fontWeight: 500 }}>
                    {c.caseNumber}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                      {c.title}
                    </div>
                    <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                      Client: {c.client}
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <CaseStatusBadge status={c.status} />
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                    {c.court}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                    {c.caseType}
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                    {c.priority === 'urgent' ? (
                      <Flag size={15} color="var(--color-case-urgent-text)" title="Urgent Priority" />
                    ) : null}
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'right', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
                    {c.nextHearing || "None"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        /* Card View (§10.2) */
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 'var(--space-md)' }}>
          {filteredCases.map((c) => (
            <div
              key={c.id}
              onClick={() => onSelectCase(c)}
              className="card-interactive"
              style={{
                padding: 'var(--space-md)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                borderLeft: c.priority === 'urgent' ? '4px solid var(--color-case-urgent-text)' : '1px solid var(--color-border-subtle)'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-mono)', color: 'var(--color-text-muted)' }}>
                    {c.caseNumber}
                  </span>
                  <CaseStatusBadge status={c.status} />
                </div>
                <h3 style={{ fontFamily: 'var(--font-sans)', fontSize: 'var(--text-h3)', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '4px' }}>
                  {c.title}
                </h3>
                <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-xs)' }}>
                  Client: {c.client}
                </div>
                <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)', marginBottom: 'var(--space-sm)' }}>
                  {c.court}
                </div>
              </div>

              <div style={{ borderTop: '1px solid var(--color-border-subtle)', paddingTop: 'var(--space-xs)', display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-caption)' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>
                  Hearing: <strong style={{ color: 'var(--color-ink-700)' }}>{c.nextHearing?.split(' ')[0] || "None"}</strong>
                </span>
                <span style={{ color: 'var(--color-text-link)' }}>
                  View details &rarr;
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      <style>{`
        .legal-table-row:hover {
          background-color: var(--color-bg-surface-sunken) !important;
        }
      `}</style>
    </div>
  );
};
