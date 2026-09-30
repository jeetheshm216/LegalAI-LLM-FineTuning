import React, { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { Sparkles, ArrowRight, ArrowLeft, CheckSquare, Square as SquareOutline, FileText } from 'lucide-react';
import { DRAFT_CATEGORIES } from '../../mock/mockDrafting';

export const NewDraftModal = ({ isOpen, onClose, onDraftCreated, cases = [], targetCase = null }) => {
  const [step, setStep] = useState(targetCase ? 2 : 1); // 1: Select Case, 2: Select Document Type, 3: Context & AI Instructions
  
  const [selectedCaseId, setSelectedCaseId] = useState(targetCase?.id || cases[0]?.id || 'case-01');
  const [selectedDocType, setSelectedDocType] = useState('Legal Notice');
  const [draftTitle, setDraftTitle] = useState('');

  React.useEffect(() => {
    if (targetCase) {
      setSelectedCaseId(targetCase.id);
      setStep(2);
    } else {
      setStep(1);
    }
  }, [targetCase, isOpen]);
  
  // AI Context selections (§ Step 3)
  const [contextSettings, setContextSettings] = useState({
    includeCaseInfo: true,
    includeDocuments: true,
    includeTimeline: true,
    includeNotes: true,
    includeConversations: true,
    supportingCases: []
  });
  
  const [additionalInstructions, setAdditionalInstructions] = useState(
    'Prepare a formal legal notice demanding immediate release of cargo and suspension of demurrage based on port authority strike force majeure.'
  );

  const [loading, setLoading] = useState(false);

  const handleNext = () => {
    if (step < 3) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const selectedCase = cases.find(c => c.id === selectedCaseId);

  const handleGenerate = async (e) => {
    e?.preventDefault();
    setLoading(true);

    setTimeout(() => {
      setLoading(false);
      onDraftCreated({
        title: draftTitle || `${selectedDocType} — ${selectedCase ? selectedCase.title : "General Matter"}`,
        documentType: selectedDocType,
        caseId: selectedCase?.id || null,
        caseNumber: selectedCase?.caseNumber || null,
        caseTitle: selectedCase?.title || "General Legal Matter",
        client: selectedCase?.client || "Advocate Chambers",
        context: contextSettings,
        instructions: additionalInstructions
      });
      onClose();
      setStep(1);
    }, 450);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create New Legal Draft"
      subtitle={`Step ${step} of 3 — ${
        step === 1 ? "Select Associated Matter" : step === 2 ? "Select Document Type" : "Configure Context & AI Drafting Directive"
      }`}
      maxWidth="680px"
    >
      <div>
        {/* Step 1: Select Case (§ Step 1) */}
        {step === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
              Choose whether this document belongs to a specific active case or constitutes a general matter.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)', maxHeight: '280px', overflowY: 'auto' }}>
              {/* General / No Case option */}
              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-sm)',
                  padding: 'var(--space-sm)',
                  borderRadius: 'var(--radius-md)',
                  border: selectedCaseId === 'general' ? '1.5px solid var(--color-accent-500)' : '1px solid var(--color-border-subtle)',
                  backgroundColor: selectedCaseId === 'general' ? 'var(--color-accent-100)' : 'var(--color-bg-surface-sunken)',
                  cursor: 'pointer'
                }}
              >
                <input
                  type="radio"
                  name="caseSelect"
                  checked={selectedCaseId === 'general'}
                  onChange={() => setSelectedCaseId('general')}
                  style={{ accentColor: 'var(--color-accent-500)' }}
                />
                <div>
                  <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                    General / No Specific Case
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                    Draft a standard template, commercial agreement, or statutory advisory without specific matter file bounds.
                  </div>
                </div>
              </label>

              {/* Cases List */}
              {cases.map(c => (
                <label
                  key={c.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-sm)',
                    padding: 'var(--space-sm)',
                    borderRadius: 'var(--radius-md)',
                    border: selectedCaseId === c.id ? '1.5px solid var(--color-accent-500)' : '1px solid var(--color-border-subtle)',
                    backgroundColor: selectedCaseId === c.id ? 'var(--color-accent-100)' : 'var(--color-bg-surface-sunken)',
                    cursor: 'pointer'
                  }}
                >
                  <input
                    type="radio"
                    name="caseSelect"
                    checked={selectedCaseId === c.id}
                    onChange={() => setSelectedCaseId(c.id)}
                    style={{ accentColor: 'var(--color-accent-500)' }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: 600, color: 'var(--color-ink-700)' }}>
                        {c.caseNumber}
                      </span>
                      <strong style={{ fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                        {c.title}
                      </strong>
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                      Client: {c.client} &bull; {c.court}
                    </div>
                  </div>
                </label>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-sm)', marginTop: 'var(--space-xs)' }}>
              <Button variant="secondary" onClick={onClose}>
                Cancel
              </Button>
              <Button variant="primary" icon={ArrowRight} iconPosition="right" onClick={handleNext}>
                Continue to Document Type
              </Button>
            </div>
          </div>
        )}

        {/* Step 2: Select Document Type (§ Step 2) */}
        {step === 2 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
              Select the formal category for this document.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-xs)', maxHeight: '280px', overflowY: 'auto' }}>
              {DRAFT_CATEGORIES.map(cat => {
                const isSelected = selectedDocType === cat;
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setSelectedDocType(cat)}
                    style={{
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-md)',
                      border: isSelected ? '1.5px solid var(--color-accent-500)' : '1px solid var(--color-border-default)',
                      backgroundColor: isSelected ? 'var(--color-accent-100)' : 'var(--color-bg-surface-sunken)',
                      color: isSelected ? 'var(--color-accent-700)' : 'var(--color-text-primary)',
                      fontWeight: isSelected ? 600 : 500,
                      fontSize: 'var(--text-caption)',
                      textAlign: 'left',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <FileText size={14} />
                    <span>{cat}</span>
                  </button>
                );
              })}
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Draft Title / Matter Identifier [Optional]
              </label>
              <input
                type="text"
                value={draftTitle}
                onChange={(e) => setDraftTitle(e.target.value)}
                placeholder={`e.g. ${selectedDocType} for Freight Demurrage Dispute`}
                className="input-base"
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 'var(--space-xs)' }}>
              <Button variant="secondary" icon={ArrowLeft} onClick={handleBack}>
                Back
              </Button>
              <Button variant="primary" icon={ArrowRight} iconPosition="right" onClick={handleNext}>
                Configure AI Context
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Select AI Context & Directive (§ Step 3) */}
        {step === 3 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
            <div
              style={{
                padding: 'var(--space-sm) var(--space-md)',
                backgroundColor: 'var(--color-ai-100)',
                border: '1px solid var(--color-ai-border)',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--text-caption)',
                color: 'var(--color-ink-700)'
              }}
            >
              <strong>Context Target:</strong> {selectedCase ? `${selectedCase.caseNumber} — ${selectedCase.title}` : "General Chambers Corpus"} &bull; <strong>Document:</strong> {selectedDocType}
            </div>

            {/* Context Checkbox Controls matching § Step 3 requirement */}
            <div>
              <span style={{ fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-primary)', display: 'block', marginBottom: '6px' }}>
                Case Context Scope to Include in Synthesis:
              </span>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: 'var(--text-caption)' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={contextSettings.includeCaseInfo}
                    onChange={(e) => setContextSettings(p => ({ ...p, includeCaseInfo: e.target.checked }))}
                    style={{ accentColor: 'var(--color-accent-500)' }}
                  />
                  Case Docket Information
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={contextSettings.includeDocuments}
                    onChange={(e) => setContextSettings(p => ({ ...p, includeDocuments: e.target.checked }))}
                    style={{ accentColor: 'var(--color-accent-500)' }}
                  />
                  Uploaded Case Documents (PDF/DOCX)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={contextSettings.includeTimeline}
                    onChange={(e) => setContextSettings(p => ({ ...p, includeTimeline: e.target.checked }))}
                    style={{ accentColor: 'var(--color-accent-500)' }}
                  />
                  Procedural Case Timeline
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={contextSettings.includeNotes}
                    onChange={(e) => setContextSettings(p => ({ ...p, includeNotes: e.target.checked }))}
                    style={{ accentColor: 'var(--color-accent-500)' }}
                  />
                  Advocate Work Notes
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={contextSettings.includeConversations}
                    onChange={(e) => setContextSettings(p => ({ ...p, includeConversations: e.target.checked }))}
                    style={{ accentColor: 'var(--color-accent-500)' }}
                  />
                  Previous AI Research Conversations
                </label>
              </div>
            </div>

            {/* Additional Instructions / Prompt Directive */}
            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '4px' }}>
                Instructions for the AI Assistant:
              </label>
              <textarea
                rows={3}
                value={additionalInstructions}
                onChange={(e) => setAdditionalInstructions(e.target.value)}
                placeholder="e.g. Prepare a formal legal notice based on the case information and uploaded documents. Highlight breach of clause 19(b)..."
                className="input-base"
                style={{ resize: 'vertical' }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 'var(--space-xs)' }}>
              <Button variant="secondary" icon={ArrowLeft} onClick={handleBack}>
                Back
              </Button>
              <Button
                variant="primary"
                icon={Sparkles}
                loading={loading}
                onClick={handleGenerate}
              >
                Generate Draft in Studio
              </Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};
