import React from 'react';
import { Plus, FileText, ChevronRight } from 'lucide-react';
import { Button } from '../common/Button';

export const CaseDraftsTab = ({ 
  currentCase, 
  drafts = [], 
  onOpenNewDraft, 
  onSelectDraft 
}) => {
  const caseDrafts = drafts.filter(d => d.caseId === currentCase.id);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
      <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
          <div>
            <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)' }}>
              Matter Pleadings & Legal Drafts
            </h3>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
              Notices, affidavits, and written arguments prepared for {currentCase.caseNumber}
            </p>
          </div>

          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={onOpenNewDraft}
          >
            New Draft for Matter
          </Button>
        </div>

        {caseDrafts.length === 0 ? (
          <div style={{ padding: 'var(--space-xl)', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: 'var(--text-caption)' }}>
            No legal drafts initiated for this matter yet. Click above to generate a notice, bail petition, or rejoinder.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
            {caseDrafts.map(draft => (
              <div
                key={draft.id}
                onClick={() => onSelectDraft(draft)}
                className="card-interactive"
                style={{
                  padding: 'var(--space-sm) var(--space-md)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                  <FileText size={18} color="var(--color-ink-500)" />
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                      {draft.title}
                    </div>
                    <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                      {draft.documentType} &bull; {draft.version} &bull; {draft.wordCount} words &bull; Modified {draft.lastModified}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-text-link)', fontSize: 'var(--text-caption)' }}>
                  <span>Edit in Studio</span>
                  <ChevronRight size={14} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
