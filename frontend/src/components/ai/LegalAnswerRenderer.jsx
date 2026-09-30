/**
 * LegalAnswerRenderer.jsx
 * 
 * Professional Lawyer-Oriented Legal AI Answer Presentation Component.
 * Transforms raw RAG outputs into structured, clear, and visually rich legal reports:
 * - Dynamic Mixed Formats: Plain-English Takeaways, Visual Procedural Flowcharts,
 *   Essential Ingredients, Practical Courtroom Realities, and Comparison Tables.
 * - Dedicated Visual Roadmap container for ASCII/text procedural flowcharts.
 * - Native Markdown Table rendering for statutory concordance and legal matrices.
 * - Isolates statutory citations at the bottom so legal analysis is never swallowed.
 * - Distinct executive section badges for effortless skimming by advocates.
 * - Official IndiaCode records and authoritative source cards.
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
  Sparkles,
  GitFork,
  Table as TableIcon,
  HelpCircle
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

  const [expanded, setExpanded] = useState(false);

  // Format legislative text lines (e.g. sub-clauses (1), (a), etc.)
  const lines = (legislativeText || '').split('\n').map(l => l.trim()).filter(Boolean);

  return (
    <div
      style={{
        marginTop: '12px',
        marginBottom: '10px',
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
          borderBottom: expanded ? '1px solid var(--color-border-subtle)' : 'none',
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
                fontSize: '13px',
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
                fontWeight: 650,
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
                fontSize: '12.5px',
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
 * Dedicated Visual Roadmap & Flowchart Renderer.
 * High-contrast, clean, responsive visualization for procedural legal workflows.
 */
const VisualFlowchartBlock = ({ code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      style={{
        margin: '14px 0',
        borderRadius: '8px',
        overflow: 'hidden',
        border: '1px solid rgba(59, 130, 246, 0.35)',
        backgroundColor: '#0a0f1d',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.25)'
      }}
    >
      {/* Top Banner */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '8px 14px',
          backgroundColor: '#111827',
          borderBottom: '1px solid #1f2937'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              width: '20px',
              height: '20px',
              borderRadius: '4px',
              backgroundColor: 'rgba(56, 189, 248, 0.15)',
              color: '#38bdf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <GitFork size={13} />
          </div>
          <span
            style={{
              fontSize: '11.5px',
              fontWeight: 700,
              color: '#f1f5f9',
              letterSpacing: '0.04em',
              textTransform: 'uppercase'
            }}
          >
            Visual Legal Roadmap & Procedural Flowchart
          </span>
        </div>

        <button
          type="button"
          onClick={handleCopy}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: copied ? '#4ade80' : '#94a3b8',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '11px',
            padding: '2px 8px',
            borderRadius: '4px',
            backgroundColor: 'rgba(255, 255, 255, 0.05)'
          }}
        >
          {copied ? <Check size={12} /> : <Copy size={12} />}
          <span>{copied ? 'Copied' : 'Copy Flowchart'}</span>
        </button>
      </div>

      {/* Flowchart Monospace Canvas */}
      <pre
        style={{
          margin: 0,
          padding: '16px 18px',
          overflowX: 'auto',
          whiteSpace: 'pre',
          fontFamily: "'Fira Code', 'Cascadia Code', 'Consolas', 'Courier New', monospace",
          fontSize: '12.5px',
          lineHeight: '1.65',
          color: '#38bdf8',
          letterSpacing: '0.02em'
        }}
      >
        <code>{code}</code>
      </pre>
    </div>
  );
};

/**
 * Dedicated Code Block Renderer for standard code/text.
 */
const CodeBlock = ({ language, code }) => {
  const [copiedCode, setCopiedCode] = useState(false);

  const handleCopyCode = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(code);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div
      style={{
        margin: '12px 0',
        borderRadius: 'var(--radius-md, 6px)',
        overflow: 'hidden',
        border: '1px solid var(--color-border-subtle)',
        backgroundColor: '#0f172a',
        color: '#f8fafc',
        fontFamily: 'var(--font-mono, monospace)',
        fontSize: '12px',
        lineHeight: 1.5
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '6px 12px',
          backgroundColor: '#1e293b',
          borderBottom: '1px solid #334155',
          fontSize: '11px',
          color: '#94a3b8',
          textTransform: 'uppercase',
          fontWeight: 600,
          letterSpacing: '0.05em'
        }}
      >
        <span>{language || 'TEXT'}</span>
        <button
          type="button"
          onClick={handleCopyCode}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: copiedCode ? '#4ade80' : '#cbd5e1',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '11px',
            padding: '2px 6px',
            borderRadius: '4px'
          }}
        >
          {copiedCode ? <Check size={12} /> : <Copy size={12} />}
          <span>{copiedCode ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
      <pre
        style={{
          margin: 0,
          padding: '12px',
          overflowX: 'auto',
          whiteSpace: 'pre',
          fontFamily: 'inherit'
        }}
      >
        <code>{code}</code>
      </pre>
    </div>
  );
};

/**
 * Dedicated Markdown Table Renderer for legal concordance and comparison matrices.
 */
const MarkdownTable = ({ headers, rows }) => {
  return (
    <div
      style={{
        margin: '14px 0',
        borderRadius: '8px',
        border: '1px solid var(--color-border-subtle)',
        overflowX: 'auto',
        boxShadow: '0 1px 3px rgba(0,0,0,0.03)'
      }}
    >
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '13px',
          textAlign: 'left'
        }}
      >
        <thead>
          <tr
            style={{
              backgroundColor: 'var(--color-bg-surface-sunken)',
              borderBottom: '2px solid var(--color-border-subtle)'
            }}
          >
            {headers.map((h, i) => (
              <th
                key={i}
                style={{
                  padding: '9px 12px',
                  fontWeight: 700,
                  color: 'var(--color-ink-900)',
                  fontSize: '12px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.03em'
                }}
              >
                {renderInlineText(h)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rIdx) => (
            <tr
              key={rIdx}
              style={{
                borderBottom: rIdx < rows.length - 1 ? '1px solid var(--color-border-subtle)' : 'none',
                backgroundColor: rIdx % 2 === 0 ? 'var(--color-bg-surface)' : 'var(--color-bg-canvas)'
              }}
            >
              {row.map((cell, cIdx) => (
                <td
                  key={cIdx}
                  style={{
                    padding: '9px 12px',
                    color: 'var(--color-text-primary)',
                    lineHeight: 1.5,
                    verticalAlign: 'top'
                  }}
                >
                  {renderInlineText(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

/**
 * Section Header Badge Renderer for Executive Sections.
 */
const ExecutiveSectionHeader = ({ title }) => {
  const cleanTitle = cleanStrayAsterisks(title).trim();
  const lower = cleanTitle.toLowerCase();

  let icon = <Layers size={14} />;
  let color = 'var(--color-ink-900)';
  let bg = 'var(--color-bg-surface-sunken)';

  if (lower.includes('executive') || lower.includes('takeaway') || lower.includes('summary')) {
    icon = <Sparkles size={14} style={{ color: 'var(--color-accent-700)' }} />;
    color = 'var(--color-accent-700)';
    bg = 'var(--color-accent-100)';
  } else if (lower.includes('roadmap') || lower.includes('flowchart') || lower.includes('procedural')) {
    icon = <GitFork size={14} style={{ color: '#38bdf8' }} />;
    color = '#38bdf8';
    bg = 'rgba(2, 132, 199, 0.18)';
  } else if (lower.includes('ingredient') || lower.includes('essential') || lower.includes('elements')) {
    icon = <CheckCircle2 size={14} style={{ color: '#34d399' }} />;
    color = '#34d399';
    bg = 'rgba(5, 150, 105, 0.18)';
  } else if (lower.includes('courtroom') || lower.includes('litigation') || lower.includes('practical') || lower.includes('reality')) {
    icon = <Scale size={14} style={{ color: '#fbbf24' }} />;
    color = '#fbbf24';
    bg = 'rgba(217, 119, 6, 0.18)';
  } else if (lower.includes('concordance') || lower.includes('old law') || lower.includes('table') || lower.includes('comparison')) {
    icon = <TableIcon size={14} style={{ color: '#2dd4bf' }} />;
    color = '#2dd4bf';
    bg = 'rgba(13, 148, 136, 0.18)';
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginTop: '16px',
        marginBottom: '6px'
      }}
    >
      <div
        style={{
          width: '24px',
          height: '24px',
          borderRadius: '4px',
          backgroundColor: bg,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}
      >
        {icon}
      </div>
      <h3
        style={{
          margin: 0,
          fontSize: '14.5px',
          fontWeight: 750,
          color: 'var(--color-ink-900)',
          letterSpacing: '0.01em'
        }}
      >
        {cleanTitle}
      </h3>
    </div>
  );
};

/**
 * Sanitizes unintended raw SVG markup.
 */
function sanitizeUnintendedMarkup(text) {
  if (!text) return '';
  return text
    .replace(/<svg[^>]*>[\s\S]*?<\/svg>/gi, '')
    .replace(/<\/?svg[^>]*>/gi, '')
    .replace(/^\s*svg\s*$/gmi, '')
    .replace(/\r\n/g, '\n');
}

/**
 * Checks if code contains visual flowchart connectors or arrows.
 */
function isVisualFlowchart(code, language) {
  if (!code) return false;
  const lang = (language || '').toLowerCase();
  if (['flowchart', 'mermaid', 'roadmap', 'ascii', 'diagram'].includes(lang)) {
    return true;
  }
  return (
    code.includes('──►') ||
    code.includes('──>') ||
    code.includes('->') ||
    code.includes('-->') ||
    code.includes('◄──') ||
    (code.includes('┌') && code.includes('┘')) ||
    (code.includes('[') && code.includes(']') && (code.includes('▼') || code.includes('|')))
  );
}

/**
 * Checks and parses markdown table lines into headers and rows.
 */
function tryParseMarkdownTable(lines) {
  if (!lines || lines.length < 2) return null;
  const tableLines = lines.map(l => l.trim()).filter(l => l.startsWith('|') && l.endsWith('|'));
  if (tableLines.length < 2) return null;

  // Header line
  const headerCells = tableLines[0]
    .split('|')
    .slice(1, -1)
    .map(c => c.trim());

  // Second line should be delimiter (e.g. |---|---|)
  const delimiterLine = tableLines[1];
  if (!/^\|[\s\-:]+(\|[\s\-:]+)+\|$/.test(delimiterLine)) {
    return null;
  }

  // Row lines
  const rows = [];
  for (let i = 2; i < tableLines.length; i++) {
    const cells = tableLines[i]
      .split('|')
      .slice(1, -1)
      .map(c => c.trim());
    rows.push(cells);
  }

  return { headers: headerCells, rows };
}

/**
 * Parses raw text into structured semantic blocks.
 * Separates legal analysis completely from statutory citation cards at the bottom.
 */
function parseContentBlocks(rawContent) {
  if (!rawContent) return [];

  // Normalize line breaks and sanitize
  let cleaned = sanitizeUnintendedMarkup(rawContent)
    .replace(/^###\s*(Legal Answer|Legal Response|Answer|Response):?\s*/i, '')
    .trim();

  // Split synthesis from authoritative reference section
  const authorityDividerRegex = /\n(?:---\s*\n+)?##\s*Authoritative Indian Legal Authorities/i;
  let synthesisText = cleaned;
  let authoritiesText = '';

  const dividerMatch = cleaned.match(authorityDividerRegex);
  if (dividerMatch) {
    synthesisText = cleaned.substring(0, dividerMatch.index).trim();
    authoritiesText = cleaned.substring(dividerMatch.index + dividerMatch[0].length).trim();
  }

  const blocks = [];

  // --- Parse Main Synthesis ---
  const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
  const segments = [];
  let lastIdx = 0;
  let codeMatch;

  while ((codeMatch = codeBlockRegex.exec(synthesisText)) !== null) {
    if (codeMatch.index > lastIdx) {
      segments.push({ type: 'text', content: synthesisText.substring(lastIdx, codeMatch.index) });
    }
    segments.push({
      type: 'code',
      language: codeMatch[1] || 'text',
      code: codeMatch[2].trimEnd()
    });
    lastIdx = codeBlockRegex.lastIndex;
  }
  if (lastIdx < synthesisText.length) {
    segments.push({ type: 'text', content: synthesisText.substring(lastIdx) });
  }

  for (const seg of segments) {
    if (seg.type === 'code') {
      if (isVisualFlowchart(seg.code, seg.language)) {
        blocks.push({
          type: 'flowchart_block',
          code: seg.code
        });
      } else {
        blocks.push({
          type: 'code_block',
          language: seg.language,
          code: seg.code
        });
      }
      continue;
    }

    const textContent = seg.content.trim();
    if (!textContent) continue;

    // Parse paragraphs, tables, lists, and headings
    const paragraphs = textContent.split(/\n\s*\n/);

    for (const para of paragraphs) {
      const pTrimmed = para.trim();
      if (!pTrimmed) continue;

      const lines = pTrimmed.split('\n').map(l => l.trim()).filter(Boolean);

      // Check if this paragraph is a Markdown Table
      const tableData = tryParseMarkdownTable(lines);
      if (tableData) {
        blocks.push({
          type: 'table_block',
          headers: tableData.headers,
          rows: tableData.rows
        });
        continue;
      }

      let lineIdx = 0;
      while (lineIdx < lines.length) {
        const line = lines[lineIdx];

        // Level 1 Heading: # Heading
        if (/^#\s+/.test(line)) {
          blocks.push({
            type: 'heading_1',
            text: line.replace(/^#\s+/, '').replace(/\*\*/g, '').trim()
          });
          lineIdx++;
          continue;
        }

        // Level 2 Heading: ## Heading
        if (/^##\s+/.test(line)) {
          blocks.push({
            type: 'heading_2',
            text: line.replace(/^##\s+/, '').replace(/\*\*/g, '').trim()
          });
          lineIdx++;
          continue;
        }

        // Level 3 Heading: ### Heading (Executive sections)
        if (/^###\s+/.test(line)) {
          blocks.push({
            type: 'heading_3',
            text: line.replace(/^###\s+/, '').replace(/\*\*/g, '').trim()
          });
          lineIdx++;
          continue;
        }

        // Level 4 Heading: #### Heading
        if (/^####\s+/.test(line)) {
          blocks.push({
            type: 'heading_4',
            text: line.replace(/^####\s+/, '').replace(/\*\*/g, '').trim()
          });
          lineIdx++;
          continue;
        }

        // Horizontal Divider: --- or *** or ___
        if (/^([-*_]){3,}$/.test(line)) {
          blocks.push({ type: 'divider' });
          lineIdx++;
          continue;
        }

        // Numbered List Items
        if (/^\d+\.\s+/.test(line)) {
          const numItems = [];
          while (lineIdx < lines.length && /^\d+\.\s+/.test(lines[lineIdx])) {
            numItems.push(lines[lineIdx].replace(/^\d+\.\s+/, '').trim());
            lineIdx++;
          }
          blocks.push({
            type: 'numbered_list',
            items: numItems
          });
          continue;
        }

        // Bullet List Items
        if (/^[-*•]\s+/.test(line)) {
          const bulletItems = [];
          while (lineIdx < lines.length && /^[-*•]\s+/.test(lines[lineIdx])) {
            bulletItems.push(lines[lineIdx].replace(/^[-*•]\s+/, '').trim());
            lineIdx++;
          }
          blocks.push({
            type: 'bullet_list',
            items: bulletItems
          });
          continue;
        }

        // Standard Paragraph
        const proseLines = [];
        while (
          lineIdx < lines.length &&
          !/^#{1,4}\s+/.test(lines[lineIdx]) &&
          !/^\d+\.\s+/.test(lines[lineIdx]) &&
          !/^[-*•]\s+/.test(lines[lineIdx]) &&
          !/^([-*_]){3,}$/.test(lines[lineIdx])
        ) {
          proseLines.push(lines[lineIdx]);
          lineIdx++;
        }

        if (proseLines.length > 0) {
          blocks.push({
            type: 'paragraph',
            text: proseLines.join('\n')
          });
        }
      }
    }
  }

  // --- Parse Authoritative Reference Section (if any) ---
  if (authoritiesText) {
    blocks.push({
      type: 'authorities_header',
      text: 'Verified Statutory Authorities & Citations'
    });

    const authorityChunks = authoritiesText.split(/(?=\n###\s+)/).map(c => c.trim()).filter(Boolean);

    for (const chunk of authorityChunks) {
      const lines = chunk.split('\n');
      const titleLine = lines[0].replace(/^###\s+/, '').replace(/\*\*/g, '').trim();

      let breadcrumb = null;
      let legislativeLines = [];
      let type = 'ACT (CENTRAL)';
      let hierarchy = 'TIER_1_PRIMARY';
      let temporalStatus = 'CURRENT';
      let officialSource = null;

      let mode = 'legislative';

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

        {/* Reliability Pill Badge & Copy Action on Right */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
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

          {!isStreaming && (
            <button
              onClick={handleCopy}
              title="Copy synthesized response"
              type="button"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                padding: '3px 9px',
                borderRadius: 'var(--radius-sm, 6px)',
                backgroundColor: copied ? 'var(--color-success-wash)' : 'var(--color-bg-surface-raised, #f8fafc)',
                border: copied ? '1px solid var(--color-success-border)' : '1px solid var(--color-border-subtle)',
                color: copied ? 'var(--color-success-text)' : 'var(--color-text-secondary)',
                fontSize: '11.5px',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => {
                if (!copied) {
                  e.currentTarget.style.backgroundColor = 'var(--color-bg-subtle, #f1f5f9)';
                  e.currentTarget.style.color = 'var(--color-text-primary)';
                }
              }}
              onMouseLeave={(e) => {
                if (!copied) {
                  e.currentTarget.style.backgroundColor = 'var(--color-bg-surface-raised, #f8fafc)';
                  e.currentTarget.style.color = 'var(--color-text-secondary)';
                }
              }}
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          )}
        </div>
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
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {/* Applicable Statutory Provision Banner */}
          {!isConversational && applicableTitle && (
            <div
              style={{
                padding: '9px 12px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--color-bg-surface-sunken)',
                borderLeft: '3px solid var(--color-ink-900)',
                display: 'flex',
                alignItems: 'baseline',
                justifyContent: 'space-between',
                gap: '8px',
                marginBottom: '4px'
              }}
            >
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)' }}>
                  {message?.query_type === 'CASE_DRAFTING' || message?.type === 'legal_drafting' ? 'Legal Pleading / Court Petition' :
                   message?.query_type === 'CASE_QUERY' || message?.type === 'case_analysis' ? 'Case Record & Pleadings' :
                   message?.query_type === 'TECHNICAL_AI' || message?.type === 'technical' ? 'Technical Architecture' :
                   message?.query_type === 'GENERAL' || message?.type === 'general' ? 'Legal & Conceptual Analysis' :
                   'Applicable Statutory Authority'}
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
            // Visual Procedural Flowchart Block
            if (block.type === 'flowchart_block') {
              return <VisualFlowchartBlock key={idx} code={block.code} />;
            }

            // Standard Code Block
            if (block.type === 'code_block') {
              return (
                <CodeBlock
                  key={idx}
                  language={block.language}
                  code={block.code}
                />
              );
            }

            // Markdown Table Block
            if (block.type === 'table_block') {
              return (
                <MarkdownTable
                  key={idx}
                  headers={block.headers}
                  rows={block.rows}
                />
              );
            }

            // Statutory Authority Showcase Card (at bottom)
            if (block.type === 'statutory_authority') {
              return <StatutoryAuthorityCard key={idx} authorityData={block.data} />;
            }

            // Authorities Section Divider Header
            if (block.type === 'authorities_header') {
              return (
                <div
                  key={idx}
                  style={{
                    marginTop: '20px',
                    paddingTop: '12px',
                    borderTop: '2px dashed var(--color-border-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <BookOpen size={15} style={{ color: 'var(--color-accent-700)' }} />
                  <span
                    style={{
                      fontSize: '12px',
                      fontWeight: 750,
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                      color: 'var(--color-ink-900)'
                    }}
                  >
                    {block.text}
                  </span>
                </div>
              );
            }

            // Headings
            if (block.type === 'heading_1') {
              return (
                <h2
                  key={idx}
                  style={{
                    margin: idx > 0 ? '20px 0 10px 0' : '6px 0 10px 0',
                    fontSize: '16px',
                    fontWeight: 800,
                    color: 'var(--color-ink-900)',
                    letterSpacing: '0.02em',
                    borderBottom: '2px solid var(--color-ink-900)',
                    paddingBottom: '6px'
                  }}
                >
                  {cleanStrayAsterisks(block.text)}
                </h2>
              );
            }

            if (block.type === 'heading_2') {
              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginTop: idx > 0 ? '16px' : '6px',
                    marginBottom: '6px',
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

            // Executive Section Headings (Level 3)
            if (block.type === 'heading_3') {
              return <ExecutiveSectionHeader key={idx} title={block.text} />;
            }

            if (block.type === 'heading_4') {
              return (
                <h5
                  key={idx}
                  style={{
                    margin: '12px 0 4px 0',
                    fontSize: '13px',
                    fontWeight: 700,
                    color: 'var(--color-ink-900)',
                    letterSpacing: '0.02em'
                  }}
                >
                  {cleanStrayAsterisks(block.text)}
                </h5>
              );
            }

            if (block.type === 'divider') {
              return (
                <hr
                  key={idx}
                  style={{
                    margin: '12px 0',
                    border: 'none',
                    borderTop: '1px solid var(--color-border-subtle)'
                  }}
                />
              );
            }

            if (block.type === 'numbered_list') {
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
                          fontWeight: 700,
                          fontSize: '11px',
                          color: 'var(--color-accent-700)',
                          backgroundColor: 'var(--color-accent-100)',
                          borderRadius: '50%',
                          width: '18px',
                          height: '18px',
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                          marginTop: '3px'
                        }}
                      >
                        {itemIdx + 1}
                      </span>
                      <div style={{ color: 'var(--color-text-primary)' }}>
                        {renderInlineText(item)}
                      </div>
                    </div>
                  ))}
                </div>
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
                  margin: '4px 0',
                  whiteSpace: 'pre-wrap'
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

    </div>
  );
};
