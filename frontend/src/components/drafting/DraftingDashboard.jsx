import React, { useState } from 'react';
import { 
  Plus, 
  Search, 
  FileText, 
  Folder, 
  Clock, 
  ChevronRight,
  Filter
} from 'lucide-react';
import { Button } from '../common/Button';
import { DRAFT_CATEGORIES } from '../../mock/mockDrafting';

export const DraftingDashboard = ({ 
  drafts, 
  onOpenNewDraft, 
  onSelectDraft 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  const filteredDrafts = drafts.filter(d => {
    const matchesSearch = 
      d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (d.caseNumber && d.caseNumber.toLowerCase().includes(searchQuery.toLowerCase())) ||
      d.documentType.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'ALL' || d.documentType === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Final':
        return { color: 'var(--color-success-text)', bg: 'var(--color-success-wash)' };
      case 'In Review':
        return { color: 'var(--color-information-text)', bg: 'var(--color-information-wash)' };
      case 'Archived':
        return { color: 'var(--color-text-muted)', bg: 'var(--color-bg-surface-sunken)' };
      case 'Draft':
      default:
        return { color: 'var(--color-text-secondary)', bg: 'var(--color-bg-surface-sunken)' };
    }
  };

  return (
    <div className="container" style={{ padding: 'var(--space-xl) var(--space-md)' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h1)', color: 'var(--color-text-primary)' }}>
            Legal Drafting Studio
          </h1>
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            Context-aware pleadings, notices, affidavits, and contractual drafting with statutory AI assistance
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          icon={Plus}
          onClick={onOpenNewDraft}
        >
          New Draft
        </Button>
      </div>

      {/* 1. Category Tiles Grid (§ DRAFT CATEGORIES) */}
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
          <span style={{ fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Document Categories
          </span>
          {selectedCategory !== 'ALL' && (
            <button
              onClick={() => setSelectedCategory('ALL')}
              style={{ background: 'none', border: 'none', color: 'var(--color-text-link)', fontSize: '11px', cursor: 'pointer' }}
            >
              Clear filter
            </button>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(170px, 1fr))', gap: '8px' }}>
          {DRAFT_CATEGORIES.map(cat => {
            const count = drafts.filter(d => d.documentType === cat).length;
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(isSelected ? 'ALL' : cat)}
                style={{
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-md)',
                  border: isSelected ? '1.5px solid var(--color-accent-500)' : '1px solid var(--color-border-subtle)',
                  backgroundColor: isSelected ? 'var(--color-accent-100)' : 'var(--color-bg-surface)',
                  color: isSelected ? 'var(--color-accent-700)' : 'var(--color-text-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all var(--duration-fast) var(--easing-standard)'
                }}
              >
                <span style={{ fontSize: 'var(--text-caption)', fontWeight: 500 }}>
                  {cat}
                </span>
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    color: isSelected ? 'var(--color-accent-700)' : 'var(--color-text-muted)',
                    backgroundColor: isSelected ? 'transparent' : 'var(--color-bg-surface-sunken)',
                    padding: '1px 6px',
                    borderRadius: 'var(--radius-sm)'
                  }}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Recent Drafts Section (§ RECENT DRAFTS) */}
      <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 'var(--space-md)', marginBottom: 'var(--space-md)' }}>
          <div>
            <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)' }}>
              Recent Chambers Drafts
            </h3>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
              {filteredDrafts.length} drafts currently active or in review
            </p>
          </div>

          <div style={{ position: 'relative', width: '280px', maxWidth: '100%' }}>
            <Search size={15} color="var(--color-text-muted)" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search drafts, dockets…"
              className="input-base"
              style={{ paddingLeft: '32px', paddingTop: '4px', paddingBottom: '4px', fontSize: 'var(--text-caption)' }}
            />
          </div>
        </div>

        {/* Draft List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
          {filteredDrafts.length === 0 ? (
            <div style={{ padding: 'var(--space-xl)', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: 'var(--text-caption)' }}>
              No drafts matching the filter. Start a new draft using the button above.
            </div>
          ) : (
            filteredDrafts.map(draft => {
              const badge = getStatusBadge(draft.status);
              return (
                <div
                  key={draft.id}
                  onClick={() => onSelectDraft(draft)}
                  className="card-interactive"
                  style={{
                    padding: 'var(--space-sm) var(--space-md)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: 'var(--space-md)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', flex: 1, minWidth: 0 }}>
                    <FileText size={20} color="var(--color-ink-500)" style={{ flexShrink: 0 }} />

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                        <span
                          style={{
                            fontWeight: 600,
                            fontSize: 'var(--text-body)',
                            color: 'var(--color-text-primary)',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {draft.title}
                        </span>
                        <span
                          style={{
                            fontSize: '11px',
                            padding: '1px 6px',
                            borderRadius: 'var(--radius-sm)',
                            color: badge.color,
                            backgroundColor: badge.bg,
                            fontWeight: 500,
                            flexShrink: 0
                          }}
                        >
                          {draft.status}
                        </span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-ink-700)' }}>
                          {draft.caseNumber || "General Matter"}
                        </span>
                        <span>{draft.documentType}</span>
                        <span>&bull;</span>
                        <span>{draft.version}</span>
                        <span>&bull;</span>
                        <span>{draft.wordCount} words</span>
                        <span>&bull;</span>
                        <span>Modified {draft.lastModified}</span>
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-text-link)', fontSize: 'var(--text-caption)', flexShrink: 0 }}>
                    <span>Open in Editor</span>
                    <ChevronRight size={14} />
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
