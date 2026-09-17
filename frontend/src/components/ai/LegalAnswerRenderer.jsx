/**
 * LegalAnswerRenderer.jsx
 * 
 * Professional Lawyer-Oriented Legal AI Answer Presentation Component.
 * Transforms raw RAG outputs into structured, clear, and beautiful legal reports:
 * - Eliminates raw markdown artifacts (no stray '**', '##', or unparsed links)
 * - Resolves 'undefined' titles in statutory provision banners
 * - Renders dedicated, rich Statutory Authority Showcase Cards for Indian statutes
 * - Formats legislative clauses (sub-sections, clauses (a)/(b)) with legal indentation
 * - Renders executive section headings (FACTS, ANALYSIS, EVIDENCE GAPS, NEXT STEPS, SUMMARY)
 * - Calibrated reliability badges (Supported, Limited, Requires Verification)
 * - Distinct Out-of-Corpus & Temporal Law advisory notices
 * - Expandable authoritative source cards & verified repository citations
 * - Native React rendering (zero dangerouslySetInnerHTML)
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
  ExternalLink,
  Layers,
  Sparkles
} from 'lucide-react';

/**
 * Cleans stray asterisks or broken markdown formatting marks.
 */
function cleanStrayAsterisks(text) {
  if (!text) return '';
  return text.replace(/\*\*/g, '');
}

/**
 * Safe inline Markdown parser for links, bold, italic, code, and text spans.
 */
function renderInlineText(text) {
  if (!text) return null;

  // Split by links [label](url), bold **text**, italic *text*, code `code`
  const tokenRegex = /(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = tokenRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(cleanStrayAsterisks(text.substring(lastIndex, match.index)));
    }
    const token = match[0];

    if (token.startsWith('[') && token.includes('](') && token.endsWith(')')) {
      const linkMatch = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (linkMatch) {
        const [, label, url] = linkMatch;
        parts.push(
          <a
            key={`link-${match.index}`}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: 'var(--color-accent-700)',
              textDecoration: 'underline',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '3px',
              wordBreak: 'break-all'
            }}
          >
            <span>{label}</span>
            <ExternalLink size={10} style={{ opacity: 0.8, flexShrink: 0 }} />
          </a>
        );
      } else {
        parts.push(cleanStrayAsterisks(token));
      }
    } else if (token.startsWith('**') && token.endsWith('**')) {
      const boldText = token.slice(2, -2).trim();
      parts.push(
        <strong key={`bold-${match.index}`} style={{ fontWeight: 650, color: 'var(--color-ink-900)' }}>
          {boldText}
        </strong>
      );
    } else if (token.startsWith('*') && token.endsWith('*')) {
      const italicText = token.slice(1, -1).trim();
      parts.push(
        <em key={`italic-${match.index}`} style={{ fontStyle: 'italic', color: 'var(--color-text-secondary)' }}>
          {italicText}
        </em>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      const codeText = token.slice(1, -1);
      parts.push(
        <code
          key={`code-${match.index}`}
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
          {codeText}
        </code>
      );
    }
    lastIndex = tokenRegex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(cleanStrayAsterisks(text.substring(lastIndex)));
  }

  return parts.length > 0 ? parts : cleanStrayAsterisks(text);
}

/**
 * Dedicated Showcase Card for Cited Indian Statutory Authorities.
 */
const StatutoryAuthorityCard = ({ authorityData }) => {
  const {
    title,
    breadcrumb,
    legislativeText,
    type,
    hierarchy,
    temporalStatus,
    officialSource
  } = authorityData;

  const [expanded, setExpanded] = useState(true);

  // Format legislative text lines (e.g. sub-clauses (1), (a), etc.)
  const lines = (legislativeText || '').split('\n').map(l => l.trim()).filter(Boolean);

  return (
    <div
      style={{
        marginTop: '12px',
        marginBottom: '14px',
        backgroundColor: 'var(--color-bg-surface)',
        borderRadius: 'var(--radius-md, 8px)',
        border: '1px solid var(--color-border-subtle)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
        overflow: 'hidden'
      }}
    >
      {/* Authority Card Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 14px',
          backgroundColor: 'var(--color-bg-surface-sunken)',
          borderBottom: '1px solid var(--color-border-subtle)',
          cursor: 'pointer'
        }}
        onClick={() => setExpanded(prev => !prev)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: 0 }}>
          <div
            style={{
              width: '24px',
              height: '24px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-accent-100)',
              color: 'var(--color-accent-700)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}
          >
            <BookOpen size={13} />
          </div>
          <div style={{ minWidth: 0 }}>
            <h4
              style={{
                margin: 0,
                fontSize: '13.5px',
                fontWeight: 700,
                color: 'var(--color-ink-900)',
                lineHeight: 1.3
              }}
            >
              {cleanStrayAsterisks(title)}
            </h4>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0, marginLeft: '8px' }}>
          {type && (
            <span
              style={{
                fontSize: '10px',
                fontWeight: 600,
                fontFamily: 'var(--font-mono)',
                padding: '2px 6px',
                borderRadius: 'var(--radius-xs)',
                backgroundColor: 'var(--color-accent-100)',
                color: 'var(--color-accent-700)',
                textTransform: 'uppercase'
              }}
            >
              {type}
            </span>
          )}
          {expanded ? <ChevronUp size={14} style={{ color: 'var(--color-text-muted)' }} /> : <ChevronDown size={14} style={{ color: 'var(--color-text-muted)' }} />}
        </div>
      </div>

      {/* Authority Content */}
      {expanded && (
        <div style={{ padding: '12px 14px' }}>
          {/* Breadcrumb citation if present */}
          {breadcrumb && (
            <div
              style={{
                fontSize: '11px',
                color: 'var(--color-text-muted)',
                backgroundColor: 'var(--color-bg-canvas)',
                padding: '4px 8px',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '10px',
                borderLeft: '2px solid var(--color-ink-500)',
                lineHeight: 1.4
              }}
            >
              {cleanStrayAsterisks(breadcrumb.replace(/^\[|\]$/g, ''))}
            </div>
          )}

          {/* Statutory Legislative Text */}
          {lines.length > 0 && (
            <div
              style={{
                fontSize: '13px',
                color: 'var(--color-text-primary)',
                lineHeight: 1.6,
                backgroundColor: 'var(--color-bg-canvas)',
                padding: '10px 12px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border-subtle)',
                marginBottom: '10px'
              }}
            >
              {lines.map((line, idx) => {
                const isClause = /^(\([0-9a-z]+\)|\d+\.)/i.test(line);
                return (
                  <div
                    key={idx}
                    style={{
                      paddingLeft: isClause ? '16px' : '0',
                      marginBottom: idx < lines.length - 1 ? '6px' : 0,
                      fontWeight: isClause ? 450 : 400
                    }}
                  >
                    {renderInlineText(line)}
                  </div>
                );
              })}
            </div>
          )}

          {/* Statutory Metadata & Source Pill Bar */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '8px',
              paddingTop: '8px',
              borderTop: '1px dashed var(--color-border-subtle)',
              fontSize: '11px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
              {hierarchy && (
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '2px 6px',
                    borderRadius: 'var(--radius-xs)',
                    backgroundColor: 'var(--color-bg-surface-sunken)',
                    color: 'var(--color-ink-700)',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 600,
                    fontSize: '10px'
                  }}
                >
                  <Scale size={10} />
                  {hierarchy.replace(/_/g, ' ')}
                </span>
              )}
              {temporalStatus && (
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '2px 6px',
                    borderRadius: 'var(--radius-xs)',
                    backgroundColor: 'var(--color-success-wash)',
                    color: 'var(--color-success-text)',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 600,
                    fontSize: '10px'
                  }}
                >
                  <CheckCircle2 size={10} />
                  {temporalStatus}
                </span>
              )}
            </div>

            {officialSource && (
              <a
                href={officialSource}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  color: 'var(--color-accent-700)',
                  fontWeight: 600,
                  textDecoration: 'none',
                  fontSize: '11px',
                  padding: '2px 6px',
                  borderRadius: 'var(--radius-xs)',
                  backgroundColor: 'var(--color-accent-100)'
                }}
              >
                <span>IndiaCode Official Record</span>
                <ExternalLink size={10} />
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Parses raw text into semantic blocks:
 * - Headings (##, ###)
 * - Authority Cards (Sections with metadata)
 * - Key Lists (- or numbered)
 * - Standard text paragraphs
 */
function parseContentBlocks(rawContent) {
  if (!rawContent) return [];

  // Normalize line breaks and strip leading meta-prompts
  let cleaned = (rawContent || '')
    .replace(/\r\n/g, '\n')
    .replace(/^###\s*(Legal Answer|Legal Response|Answer|Response):?\s*/i, '')
    .trim();

  // Split by markdown ### section blocks
  const rawSections = cleaned.split(/(?=^###\s+)/m);
  const blocks = [];

  for (const chunk of rawSections) {
    const trimmedChunk = chunk.trim();
    if (!trimmedChunk) continue;

    // Check if this chunk is a Statutory Authority block with metadata
    const isStatutorySection = 
      trimmedChunk.startsWith('###') && 
      (trimmedChunk.includes('Authority:') || 
       trimmedChunk.includes('IndiaCode') || 
       trimmedChunk.includes('Official Source:') ||
       trimmedChunk.includes('TIER_1_PRIMARY') ||
       trimmedChunk.includes('ACT (CENTRAL)'));

    if (isStatutorySection) {
      const lines = trimmedChunk.split('\n');
      const titleLine = lines[0].replace(/^###\s+/, '').replace(/\*\*/g, '').trim();

      let breadcrumb = null;
      let legislativeLines = [];
      let type = 'ACT (CENTRAL)';
      let hierarchy = 'TIER_1_PRIMARY';
      let temporalStatus = 'CURRENT';
      let officialSource = null;

      let mode = 'legislative'; // 'legislative' or 'metadata'

      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        const cleanLine = line.replace(/\*\*/g, '').trim();

        if (line.startsWith('[') && line.endsWith(']') && line.includes('|')) {
          breadcrumb = line;
          continue;
        }

        if (cleanLine.startsWith('Authority:')) {
          mode = 'metadata';
          continue;
        }

        if (mode === 'metadata') {
          if (cleanLine.startsWith('- Type:') || cleanLine.startsWith('Type:')) {
            type = cleanLine.replace(/^-?\s*Type:\s*/, '').trim();
          } else if (cleanLine.startsWith('- Hierarchy:') || cleanLine.startsWith('Hierarchy:')) {
            hierarchy = cleanLine.replace(/^-?\s*Hierarchy:\s*/, '').trim();
          } else if (cleanLine.startsWith('- Temporal Status:') || cleanLine.startsWith('Temporal Status:')) {
            temporalStatus = cleanLine.replace(/^-?\s*Temporal Status:\s*/, '').trim();
          } else if (cleanLine.includes('Official Source:') || cleanLine.includes('IndiaCode') || cleanLine.includes('http')) {
            const urlMatch = line.match(/https?:\/\/[^\s)\]]+/);
            if (urlMatch) {
              officialSource = urlMatch[0];
            }
          }
        } else {
          if (cleanLine !== 'IndiaCode') {
            legislativeLines.push(line);
          }
        }
      }

      blocks.push({
        type: 'statutory_authority',
        data: {
          title: titleLine,
          breadcrumb,
          legislativeText: legislativeLines.join('\n'),
          type,
          hierarchy,
          temporalStatus,
          officialSource
        }
      });
    } else {
      // General markdown content: split by lines or paragraphs
      const paragraphs = trimmedChunk.split(/\n\s*\n/);

      for (const para of paragraphs) {
        const pTrimmed = para.trim();
        if (!pTrimmed) continue;

        // Level 2 Heading: ## Heading or Capitalized section titles
        if (/^##\s+/.test(pTrimmed)) {
          const headingText = pTrimmed.replace(/^##\s+/, '').trim();
          blocks.push({
            type: 'heading_2',
            text: headingText
          });
        }
        // Capitalized section headers like "FACTS", "ANALYSIS", "EVIDENCE GAPS:", "NEXT STEPS"
        else if (/^(FACTS|ANALYSIS|EVIDENCE GAPS|NEXT STEPS|SUMMARY|PROCEDURAL POSTURE):?$/i.test(pTrimmed)) {
          blocks.push({
            type: 'heading_2',
            text: pTrimmed.replace(/:$/, '')
          });
        }
        // Level 3 Heading: ### Heading
        else if (/^###\s+/.test(pTrimmed)) {
          const headingText = pTrimmed.replace(/^###\s+/, '').trim();
          blocks.push({
            type: 'heading_3',
            text: headingText
          });
        }
        // Bullet List: lines starting with - , * , •
        else if (pTrimmed.split('\n').some(l => /^\s*[-*•]\s+/.test(l))) {
          const listItems = pTrimmed
            .split('\n')
            .map(l => l.replace(/^\s*[-*•]\s+/, '').trim())
            .filter(Boolean);

          blocks.push({
            type: 'bullet_list',
            items: listItems
          });
        }
        // Standard Paragraph
        else {
          blocks.push({
            type: 'paragraph',
            text: pTrimmed
          });
        }
      }
    }
  }

  return blocks;
}

export const LegalAnswerRenderer = ({
  message = {},
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

  // Clean and parse content blocks
  const blocks = parseContentBlocks(content);

  // Check special advisory conditions
  const lowerContent = (content || '').toLowerCase();
  const isOutOfCorpus = 
    evidence_status === 'OUT_OF_CORPUS' ||
    lowerContent.includes('insufficient authoritative source coverage') ||
    lowerContent.includes('outside the current legalai statutory database');

  const isTemporal = 
    confidence_status === 'TEMPORAL_TRANSITION_APPLIED' ||
    lowerContent.includes('article 20(1)') ||
    lowerContent.includes('cannot be applied retrospectively') ||
    lowerContent.includes('temporal transition') ||
    lowerContent.includes('substantive criminal liability: strictly governed by the indian penal code');

  // Conversational / Scope boundary check
  const isConversational = 
    message.type === 'conversational' || 
    message.type === 'general' || 
    message.query_type === 'CONVERSATIONAL' || 
    message.query_type === 'OUT_OF_SCOPE' || 
    message.query_type === 'GENERAL_NON_LEGAL' || 
    message.query_type === 'AMBIGUOUS' || 
    confidence_status === 'CONVERSATIONAL' || 
    confidence_status === 'OUT_OF_SCOPE' || 
    confidence_status === 'GENERAL_NON_LEGAL' || 
    confidence_status === 'AMBIGUOUS' || 
    (sources.length === 0 && citations.length === 0 && !isOutOfCorpus && !isTemporal && !content.includes('Section'));

  // Clean Applicable Title without ANY "undefined"
  const primarySource = (sources && sources.length > 0) ? sources[0] : null;
  let applicableTitle = null;
  if (primarySource) {
    const rawTitle = primarySource.title && primarySource.title !== 'undefined' ? primarySource.title.trim() : '';
    const rawRef = primarySource.reference && primarySource.reference !== 'undefined' ? primarySource.reference.trim() : '';
    if (rawTitle && rawRef && rawTitle !== rawRef) {
      applicableTitle = `${rawTitle} — ${rawRef}`;
    } else {
      applicableTitle = rawRef || rawTitle || primarySource.statute || 'Primary Statutory Authority';
    }
  } else if (isTemporal) {
    applicableTitle = 'Indian Penal Code, 1860 vs. Bharatiya Nyaya Sanhita, 2023';
  } else if (isOutOfCorpus) {
    applicableTitle = 'Outside Indexed Corpus (Negotiable Instruments / Special Acts)';
  }

  // Handle Copy Synthesis
  const handleCopy = () => {
    // Strip raw formatting artifacts for clean clipboard text
    const cleanClipboard = content.replace(/\*\*/g, '').replace(/###\s*/g, '');
    navigator.clipboard.writeText(cleanClipboard);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Badge mapping
  const badgeConfig = {
    supported: {
      label: reliabilityLabel || 'Verified Indian Legal Authority',
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
              width: '22px',
              height: '22px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-ink-900)',
              color: 'var(--color-accent-100)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
            }}
          >
            <Scale size={13} />
          </div>
          <span style={{ fontSize: '12px', fontWeight: 700, letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--color-ink-900)' }}>
            Legal AI Synthesizer
          </span>
          {timestamp && (
            <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
              • {timestamp}
            </span>
          )}
        </div>

        {/* Reliability Pill Badge */}
        {!isStreaming && !isConversational && (
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '3px 10px',
              borderRadius: 'var(--radius-full, 9999px)',
              backgroundColor: badge.bg,
              border: `1px solid ${badge.border}`,
              color: badge.color,
              fontSize: '11px',
              fontWeight: 650
            }}
          >
            {badge.icon}
            <span>{badge.label}</span>
          </div>
        )}
      </div>

      {/* 2. Streaming View with Blinking Cursor */}
      {isStreaming && (
        <div style={{ whiteSpace: 'pre-line', color: 'var(--color-text-primary)', lineHeight: 1.65 }}>
          {renderInlineText(content)}
          <span
            style={{
              display: 'inline-block',
              width: '2px',
              height: '14px',
              backgroundColor: 'var(--color-accent-700)',
              marginLeft: '3px',
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
            padding: '14px 16px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--color-warning-wash)',
            border: '1px solid var(--color-warning-border)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-warning-text)', fontWeight: 650, fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <ShieldAlert size={15} />
            <span>Legal Coverage Advisory — Out of Corpus</span>
          </div>
          <div style={{ fontSize: 'var(--text-body)', color: 'var(--color-ink-900)', lineHeight: 1.55 }}>
            {renderInlineText(content)}
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-information-text)', fontWeight: 650, fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <Clock size={15} />
            <span>Temporal Law Transition Applied (Article 20(1))</span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
            The statutory analysis has been verified against the July 1, 2024 transition threshold. Pre-commencement substantive offences remain governed by the Indian Penal Code, 1860 without retrospective liability.
          </div>
        </div>
      )}

      {/* 5. Main Structured Legal Synthesis */}
      {!isStreaming && !isOutOfCorpus && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {/* Applicable Statutory Provision Banner (Without "undefined") */}
          {applicableTitle && (
            <div
              style={{
                padding: '9px 12px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                borderLeft: '3px solid var(--color-ink-900)',
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
                <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-ink-900)', marginTop: '2px' }}>
                  {cleanStrayAsterisks(applicableTitle)}
                </span>
              </div>
              {primarySource?.type && (
                <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--color-accent-700)', fontWeight: 650, fontFamily: 'var(--font-mono)' }}>
                  {primarySource.type}
                </span>
              )}
            </div>
          )}

          {/* Render Parsed Blocks */}
          {blocks.map((block, idx) => {
            if (block.type === 'statutory_authority') {
              return <StatutoryAuthorityCard key={idx} authorityData={block.data} />;
            }

            if (block.type === 'heading_2') {
              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginTop: idx > 0 ? '14px' : '4px',
                    marginBottom: '4px',
                    paddingBottom: '4px',
                    borderBottom: '1px solid var(--color-border-subtle)'
                  }}
                >
                  <div style={{ width: '4px', height: '14px', backgroundColor: 'var(--color-ink-700)', borderRadius: '2px' }} />
                  <h3
                    style={{
                      margin: 0,
                      fontSize: '14px',
                      fontWeight: 700,
                      color: 'var(--color-ink-900)',
                      letterSpacing: '0.02em',
                      textTransform: 'uppercase'
                    }}
                  >
                    {cleanStrayAsterisks(block.text)}
                  </h3>
                </div>
              );
            }

            if (block.type === 'heading_3') {
              return (
                <h4
                  key={idx}
                  style={{
                    margin: '10px 0 4px 0',
                    fontSize: '13.5px',
                    fontWeight: 700,
                    color: 'var(--color-ink-900)'
                  }}
                >
                  {cleanStrayAsterisks(block.text)}
                </h4>
              );
            }

            if (block.type === 'bullet_list') {
              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px',
                    margin: '4px 0 8px 0'
                  }}
                >
                  {block.items.map((item, itemIdx) => (
                    <div
                      key={itemIdx}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '8px',
                        fontSize: 'var(--text-body)',
                        lineHeight: 1.55
                      }}
                    >
                      <span
                        style={{
                          width: '5px',
                          height: '5px',
                          borderRadius: '50%',
                          backgroundColor: 'var(--color-accent-700)',
                          marginTop: '8px',
                          flexShrink: 0
                        }}
                      />
                      <div style={{ color: 'var(--color-text-primary)' }}>
                        {renderInlineText(item)}
                      </div>
                    </div>
                  ))}
                </div>
              );
            }

            // Standard Paragraph
            return (
              <div
                key={idx}
                style={{
                  fontSize: 'var(--text-body)',
                  color: 'var(--color-text-primary)',
                  lineHeight: 1.65,
                  margin: '2px 0'
                }}
              >
                {renderInlineText(block.text)}
              </div>
            );
          })}
        </div>
      )}

      {/* 6. Authoritative Sources Used Strip & Cards */}
      {!isStreaming && sources && sources.length > 0 && (
        <div
          style={{
            marginTop: '8px',
            paddingTop: '8px',
            borderTop: '1px solid var(--color-border-subtle)'
          }}
        >
          <button
            onClick={() => setSourcesExpanded(prev => !prev)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-accent-700)',
              fontSize: '11px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              fontWeight: 650,
              padding: '2px 0'
            }}
          >
            <BookOpen size={13} />
            <span>{sources.length} Authoritative {sources.length === 1 ? 'Source' : 'Sources'} Consulted</span>
            {sourcesExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>

          {/* Expandable Source Cards */}
          {sourcesExpanded && (
            <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {sources.map((src, idx) => {
                const srcTitle = src.title && src.title !== 'undefined' ? src.title : (src.reference || 'Statutory Source');
                const srcRef = src.reference && src.reference !== 'undefined' && src.reference !== srcTitle ? src.reference : '';

                return (
                  <div
                    key={src.id || idx}
                    style={{
                      padding: '8px 12px',
                      backgroundColor: 'var(--color-bg-surface)',
                      borderRadius: 'var(--radius-sm)',
                      borderLeft: `3px solid var(--color-accent-500)`,
                      borderTop: '1px solid var(--color-border-subtle)',
                      borderRight: '1px solid var(--color-border-subtle)',
                      borderBottom: '1px solid var(--color-border-subtle)',
                      fontSize: 'var(--text-caption)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '8px' }}>
                      <div style={{ fontWeight: 650, color: 'var(--color-ink-900)' }}>
                        {srcTitle}
                      </div>
                      {srcRef && (
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: 600, color: 'var(--color-accent-700)', flexShrink: 0 }}>
                          {srcRef}
                        </span>
                      )}
                    </div>
                    {src.excerpt && (
                      <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '4px', fontStyle: 'italic', lineHeight: 1.45 }}>
                        "{src.excerpt}"
                      </div>
                    )}
                  </div>
                );
              })}
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
