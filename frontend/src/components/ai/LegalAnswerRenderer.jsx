/**
 * LegalAnswerRenderer.jsx
 * 
 * Professional Lawyer-Oriented Legal AI Answer Presentation Component.
 * Transforms raw RAG outputs into structured legal synthesis:
 * - Clear statutory hierarchy (Summary, Applicable Provision, Key Points, Analysis)
 * - Calibrated reliability badges (Supported, Limited, Requires Verification)
 * - Distinct Out-of-Corpus & Temporal Law advisory notices
 * - Structured expandable source cards & verified citations
 * - Safe native React Markdown parsing (no dangerouslySetInnerHTML)
 */

import React, { useState } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  AlertCircle, 
  Scale, 
  BookOpen, 
  Clock, 
  FileText, 
  ChevronDown, 
  ChevronUp, 
  Copy, 
  Check, 
  ShieldAlert,
  ExternalLink
} from 'lucide-react';

/**
 * Safe inline Markdown parser for bold, italic, code, and text spans.
 */
function renderInlineText(text) {
  if (!text) return null;

  // Split by inline formatting tokens: **bold**, *italic*, `code`
  const parts = [];
  const regex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith('**') && token.endsWith('**')) {
      parts.push(
        <strong key={match.index} style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('*') && token.endsWith('*')) {
      parts.push(
        <em key={match.index} style={{ fontStyle: 'italic', color: 'var(--color-text-secondary)' }}>
          {token.slice(1, -1)}
        </em>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(
        <code
          key={match.index}
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.85em',
            backgroundColor: 'var(--color-bg-surface-sunken)',
            padding: '2px 5px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--color-border-subtle)',
            color: 'var(--color-ink-900)'
          }}
        >
          {token.slice(1, -1)}
        </code>
      );
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}

/**
 * Parses raw text into semantic legal sections.
 */
function parseLegalContent(rawContent) {
  if (!rawContent) {
    return {
      title: null,
      summary: '',
      applicableProvision: null,
      keyPoints: [],
      analysis: '',
      caveats: null,
      paragraphs: []
    };
  }

  // Strip leading headers like "### Legal Answer:", "### Answer:", etc.
  let cleaned = rawContent
    .replace(/^###\s*(Legal Answer|Legal Response|Answer|Response):?\s*/i, '')
    .trim();

  // Check for Out of Corpus condition
  const isOutOfCorpus = 
    cleaned.toLowerCase().includes('insufficient authoritative source coverage') ||
    cleaned.toLowerCase().includes('outside the current legalai statutory database');

  // Check for Temporal Law condition
  const isTemporal = 
    cleaned.toLowerCase().includes('article 20(1)') ||
    cleaned.toLowerCase().includes('cannot be applied retrospectively') ||
    cleaned.toLowerCase().includes('temporal transition') ||
    cleaned.toLowerCase().includes('substantive criminal liability: strictly governed by the indian penal code');

  // Separate paragraphs
  const rawParagraphs = cleaned
    .split(/\n\s*\n/)
    .map(p => p.trim())
    .filter(Boolean);

  // If already structured with numbered items (e.g. "1. ...", "(a) ...", etc.)
  const keyPoints = [];
  const bodyParagraphs = [];

  for (const para of rawParagraphs) {
    // Check if paragraph contains conditions or numbered list
    const listMatch = para.match(/^(\d+\.|\([a-z]\)|\([0-9]+\))\s*(.*)/);
    if (listMatch) {
      keyPoints.push({
        num: listMatch[1],
        text: listMatch[2]
      });
    } else if (para.includes('(a)') && para.includes('(b)')) {
      // Split inline conditions like "(a) ... (b) ... (c) ..."
      const subParts = para.split(/(\([a-z]\)\s*)/).filter(Boolean);
      let intro = '';
      for (let i = 0; i < subParts.length; i++) {
        if (/^\([a-z]\)\s*$/.test(subParts[i]) && i + 1 < subParts.length) {
          keyPoints.push({
            num: subParts[i].trim(),
            text: subParts[i + 1].trim().replace(/[;,]\s*$/, '')
          });
          i++; // Skip content part
        } else if (keyPoints.length === 0) {
          intro += subParts[i];
        }
      }
      if (intro.trim()) {
        bodyParagraphs.push(intro.trim());
      }
    } else {
      bodyParagraphs.push(para);
    }
  }

  // Extract Summary: first substantive sentence or paragraph
  let summary = '';
  let analysis = '';

  if (bodyParagraphs.length > 0) {
    summary = bodyParagraphs[0];
    if (bodyParagraphs.length > 1) {
      analysis = bodyParagraphs.slice(1).join('\n\n');
    }
  }

  return {
    isOutOfCorpus,
    isTemporal,
    summary,
    keyPoints,
    analysis,
    rawText: cleaned
  };
}

export const LegalAnswerRenderer = ({
  message,
  isStreaming = false,
  compact = false
}) => {
  const [copied, setCopied] = useState(false);
  const [sourcesExpanded, setSourcesExpanded] = useState(true);
  const [citationsExpanded, setCitationsExpanded] = useState(false);

  const {
    content = '',
    reliability = 'supported',
    reliabilityLabel,
    sources = [],
    citations = [],
    confidence_status,
    evidence_status,
    timestamp
  } = message;

  const parsed = parseLegalContent(content);
  const isOutOfCorpus = parsed.isOutOfCorpus || evidence_status === 'OUT_OF_CORPUS';
  const isTemporal = parsed.isTemporal || confidence_status === 'TEMPORAL_TRANSITION_APPLIED';

  // Handle Copy
  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Badge mapping
  const badgeConfig = {
    supported: {
      label: reliabilityLabel || 'Supported by sources',
      icon: <CheckCircle2 size={13} style={{ color: 'var(--color-success-text)' }} />,
      bg: 'var(--color-success-wash)',
      color: 'var(--color-success-text)',
      border: 'var(--color-success-border)'
    },
    limited: {
      label: reliabilityLabel || (isTemporal ? 'Temporal transition applied' : 'Limited evidence'),
      icon: <AlertTriangle size={13} style={{ color: 'var(--color-warning-text)' }} />,
      bg: 'var(--color-warning-wash)',
      color: 'var(--color-warning-text)',
      border: 'var(--color-warning-border)'
    },
    verify: {
      label: reliabilityLabel || (isOutOfCorpus ? 'Out-of-corpus statutory matter' : 'Requires verification'),
      icon: <AlertCircle size={13} style={{ color: 'var(--color-error-text)' }} />,
      bg: 'var(--color-error-wash)',
      color: 'var(--color-error-text)',
      border: 'var(--color-error-border)'
    }
  };

  const badge = badgeConfig[reliability] || badgeConfig.supported;

  // Primary applicable provision detection from sources
  const primarySource = sources.length > 0 ? sources[0] : null;
  const applicableTitle = primarySource 
    ? `${primarySource.title} — ${primarySource.reference}`
    : isTemporal 
      ? 'Indian Penal Code, 1860 vs. Bharatiya Nyaya Sanhita, 2023'
      : isOutOfCorpus
        ? 'Outside Indexed Corpus (Negotiable Instruments / Special Acts)'
        : null;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-sm)',
        width: '100%',
        maxWidth: '100%',
        color: 'var(--color-text-primary)',
        fontFamily: 'var(--font-sans)',
        fontSize: compact ? 'var(--text-body)' : 'var(--text-body-lg)',
        lineHeight: 1.65
      }}
    >
      {/* 1. Header: Synthesizer Brand, Timestamp & Reliability Badge */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '8px',
          paddingBottom: '8px',
          borderBottom: '1px solid var(--color-border-subtle)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              width: '20px',
              height: '20px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-ai-100)',
              color: 'var(--color-ai-500)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid var(--color-ai-border)'
            }}
          >
            <Scale size={12} />
          </div>
          <span style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--color-ink-700)' }}>
            Legal AI Synthesizer
          </span>
          {timestamp && (
            <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
              • {timestamp}
            </span>
          )}
        </div>

        {/* Reliability Pill Badge */}
        {!isStreaming && (
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '2px 8px',
              borderRadius: 'var(--radius-full, 9999px)',
              backgroundColor: badge.bg,
              border: `1px solid ${badge.border}`,
              color: badge.color,
              fontSize: '11px',
              fontWeight: 600
            }}
          >
            {badge.icon}
            <span>{badge.label}</span>
          </div>
        )}
      </div>

      {/* 2. Streaming View with Blinking Cursor */}
      {isStreaming && (
        <div style={{ whiteSpace: 'pre-line', color: 'var(--color-text-primary)' }}>
          {renderInlineText(content)}
          <span
            style={{
              display: 'inline-block',
              width: '2px',
              height: '14px',
              backgroundColor: 'var(--color-ai-500)',
              marginLeft: '2px',
              verticalAlign: 'text-bottom',
              animation: 'blink 1s step-start infinite'
            }}
          />
        </div>
      )}

      {/* 3. Special Notice: Out-of-Corpus Advisory */}
      {!isStreaming && isOutOfCorpus && (
        <div
          style={{
            padding: '12px 14px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--color-warning-wash)',
            border: '1px solid var(--color-warning-border)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-warning-text)', fontWeight: 600, fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <ShieldAlert size={15} />
            <span>Legal Coverage Advisory — Out of Corpus</span>
          </div>
          <div style={{ fontSize: 'var(--text-body)', color: 'var(--color-ink-900)', lineHeight: 1.55 }}>
            {renderInlineText(parsed.rawText)}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', paddingTop: '4px', borderTop: '1px dashed var(--color-warning-border)' }}>
            <strong>Authoritative Indexed Coverage:</strong> Bharatiya Nyaya Sanhita, 2023 • Bharatiya Nagarik Suraksha Sanhita, 2023 • Bharatiya Sakshya Adhiniyam, 2023.
          </div>
        </div>
      )}

      {/* 4. Special Notice: Temporal Law Guard Advisory */}
      {!isStreaming && !isOutOfCorpus && isTemporal && (
        <div
          style={{
            padding: '12px 14px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--color-information-wash)',
            border: '1px solid var(--color-information-border)',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-information-text)', fontWeight: 600, fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <Clock size={15} />
            <span>Temporal Law Transition Applied (Article 20(1))</span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
            The statutory analysis has been verified against the July 1, 2024 transition threshold. Pre-commencement substantive offences remain governed by the Indian Penal Code, 1860 without retrospective liability.
          </div>
        </div>
      )}

      {/* 5. Main Structured Legal Answer (Only for non-out-of-corpus answers) */}
      {!isStreaming && !isOutOfCorpus && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          {/* Applicable Provision Banner */}
          {applicableTitle && (
            <div
              style={{
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                borderLeft: '3px solid var(--color-ink-700)',
                display: 'flex',
                alignItems: 'baseline',
                justifyContent: 'space-between',
                gap: '8px'
              }}
            >
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)' }}>
                  Applicable Statutory Provision
                </span>
                <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-ink-900)' }}>
                  {applicableTitle}
                </span>
              </div>
              {primarySource?.type && (
                <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--color-accent-700)', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                  {primarySource.type}
                </span>
              )}
            </div>
          )}

          {/* Section: SUMMARY */}
          {parsed.summary && (
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
                Summary
              </div>
              <div style={{ fontSize: 'var(--text-body-lg)', color: 'var(--color-text-primary)', lineHeight: 1.6 }}>
                {renderInlineText(parsed.summary)}
              </div>
            </div>
          )}

          {/* Section: KEY POINTS / STATUTORY REQUIREMENTS */}
          {parsed.keyPoints.length > 0 && (
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)', marginBottom: '6px' }}>
                Key Points & Statutory Conditions
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {parsed.keyPoints.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '8px',
                      padding: '6px 10px',
                      backgroundColor: 'var(--color-bg-surface)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-border-subtle)',
                      fontSize: 'var(--text-body)'
                    }}
                  >
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '11px',
                        fontWeight: 700,
                        color: 'var(--color-ai-500)',
                        minWidth: '20px',
                        paddingTop: '2px'
                      }}
                    >
                      {item.num}
                    </span>
                    <div style={{ color: 'var(--color-text-primary)', lineHeight: 1.5 }}>
                      {renderInlineText(item.text)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section: ANALYSIS / ADDITIONAL APPLICATION */}
          {parsed.analysis && (
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
                Legal Analysis & Procedural Application
              </div>
              <div style={{ fontSize: 'var(--text-body)', color: 'var(--color-text-secondary)', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                {renderInlineText(parsed.analysis)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 6. Authoritative Sources Used Strip & Cards */}
      {!isStreaming && sources && sources.length > 0 && (
        <div
          style={{
            marginTop: 'var(--space-xs)',
            paddingTop: 'var(--space-xs)',
            borderTop: '1px solid var(--color-ai-border)'
          }}
        >
          <button
            onClick={() => setSourcesExpanded(prev => !prev)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-text-link)',
              fontSize: 'var(--text-caption)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              fontWeight: 600,
              padding: '2px 0'
            }}
          >
            <BookOpen size={13} />
            <span>{sources.length} Authoritative {sources.length === 1 ? 'Source' : 'Sources'} Used</span>
            {sourcesExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>

          {/* Expandable Source Cards */}
          {sourcesExpanded && (
            <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {sources.map((src, idx) => (
                <div
                  key={src.id || idx}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: 'var(--color-bg-surface)',
                    borderRadius: 'var(--radius-sm)',
                    borderLeft: `3px solid ${badge.border}`,
                    borderTop: '1px solid var(--color-border-subtle)',
                    borderRight: '1px solid var(--color-border-subtle)',
                    borderBottom: '1px solid var(--color-border-subtle)',
                    fontSize: 'var(--text-caption)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                    <div style={{ fontWeight: 600, color: 'var(--color-ink-900)' }}>
                      {src.title}
                    </div>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: 600, color: 'var(--color-accent-700)' }}>
                      {src.reference}
                    </span>
                  </div>
                  {src.excerpt && (
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '4px', fontStyle: 'italic', lineHeight: 1.45 }}>
                      "{src.excerpt}"
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 7. Verified Citations Section */}
      {!isStreaming && citations && citations.length > 0 && (
        <div style={{ marginTop: '4px' }}>
          <button
            onClick={() => setCitationsExpanded(prev => !prev)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-text-muted)',
              fontSize: '11px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontWeight: 500,
              padding: 0
            }}
          >
            <FileText size={11} />
            <span>Verified Gazette & Repository Citations ({citations.length})</span>
            {citationsExpanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
          </button>

          {citationsExpanded && (
            <div
              style={{
                marginTop: '6px',
                padding: '8px 10px',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border-subtle)',
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                color: 'var(--color-text-secondary)',
                lineHeight: 1.5
              }}
            >
              {citations.map((c, i) => (
                <div key={i} style={{ marginBottom: i < citations.length - 1 ? '6px' : 0 }}>
                  • {c}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 8. Quick Actions Toolbar */}
      {!isStreaming && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-md)',
            marginTop: '6px',
            paddingTop: '6px',
            borderTop: '1px solid var(--color-border-subtle)',
            fontSize: '11px',
            color: 'var(--color-text-muted)'
          }}
        >
          <button
            onClick={handleCopy}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: copied ? 'var(--color-success-text)' : 'var(--color-text-muted)',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
              padding: '2px 4px',
              borderRadius: 'var(--radius-xs)'
            }}
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy Synthesis'}</span>
          </button>
        </div>
      )}
    </div>
  );
};
