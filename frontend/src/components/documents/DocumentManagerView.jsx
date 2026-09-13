import React, { useState } from 'react';
import { 
  Upload, 
  FileText, 
  Search, 
  Filter, 
  RotateCw, 
  Eye, 
  Download, 
  Trash2, 
  X,
  FileCode,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { Button } from '../common/Button';
import { DocumentStatusDot } from '../common/Badge';

export const DocumentManagerView = ({ 
  caseId, 
  caseNumber, 
  documents, 
  onUploadDocument 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [previewDoc, setPreviewDoc] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const categories = ['ALL', 'Court Order', 'Contract', 'Pleadings', 'Evidence', 'Deposition'];

  const filteredDocs = documents.filter(doc => {
    const matchesSearch = doc.filename.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'ALL' || doc.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      onUploadDocument({
        caseId,
        caseNumber,
        file,
        category: 'Evidence'
      });
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      onUploadDocument({
        caseId,
        caseNumber,
        file,
        category: 'Pleadings'
      });
    }
  };

  return (
    <div>
      {/* 1. Drag & Drop Upload Zone (§12.1) */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          border: isDragOver ? '2px solid var(--color-accent-500)' : '2px dashed var(--color-border-default)',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: isDragOver ? 'var(--color-accent-100)' : 'var(--color-bg-surface-sunken)',
          padding: 'var(--space-xl) var(--space-md)',
          textAlign: 'center',
          marginBottom: 'var(--space-lg)',
          transition: 'all var(--duration-fast) var(--easing-standard)',
          cursor: 'pointer'
        }}
        onClick={() => document.getElementById('legal-doc-upload-input')?.click()}
      >
        <input
          id="legal-doc-upload-input"
          type="file"
          accept=".pdf,.docx,.jpg,.png"
          style={{ display: 'none' }}
          onChange={handleFileInput}
        />
        <div style={{ color: isDragOver ? 'var(--color-accent-700)' : 'var(--color-ink-500)', marginBottom: 'var(--space-xs)' }}>
          <Upload size={28} style={{ margin: '0 auto' }} />
        </div>
        <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
          Drag case documents here or click to browse
        </div>
        <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
          Accepted file types: PDF, DOCX, JPG, PNG &bull; Automatic OCR & Vector Ingestion
        </div>
      </div>

      {/* 2. Search and Category Filter Toolbar */}
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
        <div style={{ position: 'relative', width: '280px', maxWidth: '100%' }}>
          <Search size={15} color="var(--color-text-muted)" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents by name…"
            className="input-base"
            style={{ paddingLeft: '32px', paddingTop: '4px', paddingBottom: '4px', fontSize: 'var(--text-caption)' }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2xs)', overflowX: 'auto' }}>
          {categories.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                style={{
                  padding: '3px 8px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-caption)',
                  cursor: 'pointer',
                  border: isSelected ? '1px solid var(--color-accent-500)' : '1px solid var(--color-border-default)',
                  backgroundColor: isSelected ? 'var(--color-accent-100)' : 'var(--color-bg-surface)',
                  color: isSelected ? 'var(--color-accent-700)' : 'var(--color-text-secondary)'
                }}
              >
                {cat}
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Document Rows List (§12.2) */}
      <div className="card-base" style={{ overflow: 'hidden' }}>
        {filteredDocs.length === 0 ? (
          <div style={{ padding: 'var(--space-xl)', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
            No documents matching the selected filters.
          </div>
        ) : (
          filteredDocs.map((doc) => (
            <div
              key={doc.id}
              style={{
                padding: 'var(--space-sm) var(--space-md)',
                borderBottom: '1px solid var(--color-border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 'var(--space-md)',
                backgroundColor: 'var(--color-bg-surface)'
              }}
            >
              {/* Left info */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', flex: 1, minWidth: 0 }}>
                <div style={{ color: 'var(--color-ink-500)', flexShrink: 0 }}>
                  <FileText size={20} strokeWidth={1.5} />
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
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
                      {doc.filename}
                    </span>
                    <span
                      style={{
                        fontSize: '11px',
                        backgroundColor: 'var(--color-bg-surface-sunken)',
                        padding: '1px 6px',
                        borderRadius: 'var(--radius-sm)',
                        color: 'var(--color-text-secondary)'
                      }}
                    >
                      {doc.category}
                    </span>
                  </div>

                  {/* Uploading progress bar state per §12.2 */}
                  {doc.status === 'uploading' ? (
                    <div style={{ marginTop: '4px', maxWidth: '280px' }}>
                      <div style={{ height: '4px', backgroundColor: 'var(--color-bg-surface-sunken)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{ width: `${doc.progress || 64}%`, height: '100%', backgroundColor: 'var(--color-ink-500)' }} />
                      </div>
                      <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>{doc.statusLabel}</span>
                    </div>
                  ) : (
                    <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                      {doc.fileSize} &bull; {doc.pages} pages &bull; Uploaded {doc.uploadedDate}
                    </div>
                  )}
                </div>
              </div>

              {/* Status indicator & Actions */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)', flexShrink: 0 }}>
                <DocumentStatusDot status={doc.status} label={doc.statusLabel} />

                {doc.status === 'failed' && (
                  <button
                    onClick={() => alert(`Retrying OCR indexing for ${doc.filename}...`)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--color-error-text)',
                      fontSize: 'var(--text-caption)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <RotateCw size={13} />
                    Retry
                  </button>
                )}

                <Button
                  variant="secondary"
                  size="sm"
                  icon={Eye}
                  onClick={() => setPreviewDoc(doc)}
                >
                  Preview
                </Button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 4. Document Preview Slide-Over (§12.2) — 480px wide desktop slide-over */}
      {previewDoc && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 32, 0.35)',
            zIndex: 'var(--z-slide-over)',
            display: 'flex',
            justifyContent: 'flex-end',
            animation: 'fadeIn var(--duration-fast) var(--easing-decelerate)'
          }}
          onClick={() => setPreviewDoc(null)}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '480px',
              backgroundColor: 'var(--color-bg-surface-raised)',
              height: '100%',
              boxShadow: 'var(--elevation-3)',
              display: 'flex',
              flexDirection: 'column'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div
              style={{
                padding: 'var(--space-md) var(--space-lg)',
                borderBottom: '1px solid var(--color-border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: 'var(--text-h3)', color: 'var(--color-text-primary)' }}>
                  Document Viewer
                </div>
                <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
                  {previewDoc.filename}
                </div>
              </div>

              <button
                onClick={() => setPreviewDoc(null)}
                aria-label="Close document preview"
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  color: 'var(--color-text-muted)'
                }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Document Content Paper Area (§2.8: stays light paper even in dark mode chrome!) */}
            <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-md)', backgroundColor: 'var(--color-bg-canvas)' }}>
              <div
                style={{
                  backgroundColor: 'var(--color-doc-page)',
                  color: '#171E26',
                  padding: 'var(--space-xl)',
                  borderRadius: 'var(--radius-sm)',
                  boxShadow: 'var(--elevation-1)',
                  minHeight: '400px',
                  fontFamily: 'var(--font-serif)',
                  fontSize: '15px',
                  lineHeight: '1.7',
                  border: '1px solid var(--color-border-subtle)'
                }}
              >
                <div style={{ textAlign: 'center', marginBottom: 'var(--space-lg)', borderBottom: '1px solid #D3CFC5', paddingBottom: 'var(--space-sm)' }}>
                  <div style={{ fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#5C7086' }}>
                    Chambers Record &bull; Exhibit Copy
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 700, color: '#0F1720', marginTop: '4px' }}>
                    {previewDoc.filename.replace(/_/g, ' ').replace('.pdf', '')}
                  </div>
                </div>

                <p style={{ marginBottom: 'var(--space-md)' }}>
                  {previewDoc.excerpt || "Certified legal record ingested into chambers vector database. Electronic signatures validated."}
                </p>

                {previewDoc.citablePassages?.map((pass, i) => (
                  <div
                    key={i}
                    style={{
                      backgroundColor: 'var(--color-doc-ai-highlight)',
                      borderLeft: '3px solid var(--color-ai-500)',
                      padding: 'var(--space-xs) var(--space-sm)',
                      margin: 'var(--space-md) 0',
                      fontFamily: 'var(--font-sans)',
                      fontSize: '14px',
                      color: '#1B2836'
                    }}
                  >
                    <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-ai-500)', textTransform: 'uppercase' }}>
                      Cited Passage &bull; Page {pass.page} ({pass.section})
                    </div>
                    <div>"{pass.text}"</div>
                  </div>
                ))}

                <p style={{ marginTop: 'var(--space-md)', color: '#4B5563', fontSize: '14px' }}>
                  [End of preview extract &bull; Total {previewDoc.pages} pages indexed for legal citation synthesis]
                </p>
              </div>
            </div>

            {/* Slide-over Footer */}
            <div
              style={{
                padding: 'var(--space-md)',
                borderTop: '1px solid var(--color-border-subtle)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                backgroundColor: 'var(--color-bg-surface)'
              }}
            >
              <DocumentStatusDot status={previewDoc.status} label={previewDoc.statusLabel} />
              <Button
                variant="primary"
                size="sm"
                icon={Download}
                onClick={() => alert(`Downloading verified copy of ${previewDoc.filename}`)}
              >
                Download PDF
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
