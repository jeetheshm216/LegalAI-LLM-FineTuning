import React, { useState } from 'react';
import { 
  Plus, 
  Search, 
  FileText, 
  Folder, 
  Clock, 
  ChevronRight,
  Filter,
  Sparkles,
  Zap,
  Scale,
  ShieldAlert,
  Send,
  CheckCircle2,
  FileCheck,
  BookOpen
} from 'lucide-react';
import { Button } from '../common/Button';

// High-utility courtroom templates heavily utilized by litigation advocates
export const COURT_TEMPLATES = [
  {
    id: 'tmpl-bail',
    title: 'Regular Bail Petition (BNSS §480)',
    statute: 'Bharatiya Nagarik Suraksha Sanhita, 2023',
    courtType: 'Sessions Court / High Court',
    badge: 'Criminal Defense',
    color: '#EF4444',
    bg: 'rgba(239, 68, 68, 0.12)',
    description: 'Pre-formatted petition asserting personal liberty, absence of flight risk, and challenging electronic evidence under Section 63 BSA.',
    defaultContent: `IN THE COURT OF THE DISTRICT & SESSIONS JUDGE AT NEW DELHI
CRIMINAL MISC. (BAIL) APPLICATION NO. _______ OF 2026

IN THE MATTER OF:
State (NCT of Delhi)                                     ... Prosecution
                                VERSUS
Arthur Whitfield, S/o J. Whitfield                      ... Applicant / Accused

APPLICATION UNDER SECTION 480 READ WITH SECTION 479 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA (BNSS), 2023 FOR GRANT OF REGULAR BAIL

MOST RESPECTFULLY SHOWETH:

1. That the Applicant has been falsely implicated in FIR No. 442/2024 registered at Police Station Special Cell, and has been in judicial custody since 22nd January 2024.

2. That the investigation in the matter stands concluded and the Police have submitted the final report/chargesheet under Section 193 BNSS, 2023. No custodial interrogation of the Applicant is required.

3. GROUNDS FOR BAIL:
   A. PRIMA FACIE INNOCENCE: The allegations against the Applicant are entirely documentary and digital in nature. The mandatory certificate under Section 63 of Bharatiya Sakshya Adhiniyam, 2023 was never obtained at the time of electronic drive seizure.
   B. PARITY & PRE-TRIAL DETENTION: The Applicant satisfies the statutory safeguards under Section 479 BNSS, having completed substantial detention as an under-trial prisoner.
   C. NO FLIGHT RISK: The Applicant is a permanent resident, has deep roots in society, and has surrendered his passport to the Investigating Officer.

PRAYER:
It is therefore respectfully prayed that this Hon'ble Court may be pleased to:
a) Grant regular bail to the Applicant in FIR No. 442/2024 on furnishing of reasonable personal bond and local surety;
b) Pass any other relief as this Hon'ble Court deems fit in the interest of justice.

AND FOR THIS ACT OF KINDNESS, THE APPLICANT SHALL EVER PRAY.

Filed by:
Elena Vance
Advocate for Applicant`
  },
  {
    id: 'tmpl-injunction',
    title: 'Ad-Interim Injunction App (O. XXXIX R. 1 & 2 CPC)',
    statute: 'Code of Civil Procedure, 1908',
    courtType: 'Commercial Division, High Court',
    badge: 'Commercial Litigation',
    color: '#0D9488',
    bg: 'rgba(13, 148, 136, 0.12)',
    description: 'Notice of Motion satisfying threefold test: prima facie case, balance of convenience, and irreparable injury.',
    defaultContent: `IN THE HIGH COURT OF JUDICATURE AT BOMBAY
COMMERCIAL DIVISION
NOTICE OF MOTION NO. _______ OF 2026
IN
COMMERCIAL SUIT NO. 1187 OF 2024

Julian Martinez                                          ... Plaintiff
                                VERSUS
Coastal Holdings Ltd. & Anr.                             ... Defendants

APPLICATION UNDER ORDER XXXIX RULES 1 & 2 READ WITH SECTION 151 OF THE CODE OF CIVIL PROCEDURE, 1908 FOR AD-INTERIM EX-PARTE INJUNCTION

THE PLAINTIFF RESPECTFULLY STATES AS UNDER:

1. That the Plaintiff has instituted the accompanying Commercial Suit seeking a permanent decree of injunction restraining the Defendants from alienating or asserting an unlawful maritime possessory lien over 14,000 MT catalytic cargo.

2. THREEFOLD STATUTORY TRIGGER:
   A. PRIMA FACIE CASE: Clause 19(b) of the Charterparty expressly suspends demurrage accrual during official port authority strikes. The Port Authority directive dated August 14, 2026 conclusively establishes the strike interval.
   B. BALANCE OF CONVENIENCE: The cargo consists of sensitive industrial catalysts that suffer rapid degradation. The balance of convenience tilts overwhelmingly in favour of status quo.
   C. IRREPARABLE INJURY: If the cargo is liquidated at auction, the Plaintiff will suffer permanent financial and commercial annihilation incapable of restitution in monetary terms.

PRAYER:
The Plaintiff respectfully prays that this Hon'ble Court may be pleased to:
a) Pass an ad-interim ex-parte order of injunction restraining Defendant No. 1 and their agents from disposing of or auctioning the catalytic cargo at Berth 9;
b) Direct unconditional release of gate passes upon deposit of disputed bunker dues into the Registry.`
  },
  {
    id: 'tmpl-ni138',
    title: 'Section 138 NI Act Statutory Demand Notice',
    statute: 'Negotiable Instruments Act, 1881',
    courtType: 'Pre-Litigation Statutory Demand',
    badge: 'Cheque Dishonour',
    color: '#F59E0B',
    bg: 'rgba(245, 158, 11, 0.12)',
    description: 'Mandatory 15-day notice with precise statutory formula regarding cheque presentation, memo of dishonour, and penal consequences.',
    defaultContent: `REGISTERED A.D. / SPEED POST / LEGAL NOTICE
DATED: 29th September 2026

To,
Horizon Freight Services Pvt. Ltd.,
Represented by its Managing Director,
B-44, Logistics Hub, Sector 62, Gurgaon.

SUBJECT: STATUTORY DEMAND NOTICE UNDER SECTION 138 READ WITH SECTION 141 OF THE NEGOTIABLE INSTRUMENTS ACT, 1881 FOR DISHONOUR OF CHEQUE NO. 004812 FOR INR 6,40,00,000/-

Under instructions from our client, Apex Logistics Corp., we hereby serve upon you this Statutory Demand Notice:

1. That towards discharge of admitted contractual liabilities under the Master Fleet Lease, you issued Cheque No. 004812 dated 10th September 2026 for INR 6,40,00,000/- drawn on State Bank of India.

2. That our client presented the said cheque for encashment, which was returned unpaid on 22nd September 2026 with bank return memo stating "FUNDS INSUFFICIENT / PAYMENT STOPPED".

3. That you have failed to maintain sufficient balance to honor your statutory commitment.

WE HEREBY CALL UPON YOU to pay the said sum of INR 6,40,00,000/- within fifteen (15) days of the receipt of this notice, failing which our client shall initiate criminal prosecution under Section 138 of the Negotiable Instruments Act without further reference, wherein you and your directors shall be liable for imprisonment up to two years and fine up to twice the cheque amount.

Elena Vance
Advocate for the Complainant`
  },
  {
    id: 'tmpl-sec9',
    title: 'Section 9 Arbitration Petition (Protective Measures)',
    statute: 'Arbitration & Conciliation Act, 1996',
    courtType: 'Commercial Appellate Court',
    badge: 'Arbitration',
    color: '#6366F1',
    bg: 'rgba(99, 102, 241, 0.12)',
    description: 'Urgent petition restraining encashment of unconditional bank guarantee and preserving subject matter assets.',
    defaultContent: `IN THE COMMERCIAL APPELLATE TRIBUNAL / HIGH COURT
COMMERCIAL ARBITRATION PETITION NO. _______ OF 2026

IN THE MATTER OF:
Apex Logistics Corp.                                     ... Petitioner
                                VERSUS
Horizon Freight Services Pvt. Ltd.                       ... Respondent

PETITION UNDER SECTION 9 OF THE ARBITRATION AND CONCILIATION ACT, 1996 FOR AD-INTERIM PROTECTIVE MEASURES

1. That there exists a valid arbitration agreement between the parties under Clause 28 of the Master Fleet Lease Agreement.

2. That the Respondent has issued an arbitrary invocation letter for Bank Guarantee No. BG-2023-889 worth INR 6.40 Crores, without fulfilling precedent notice conditions.

3. That the law is well-settled in Svenska Handelsbanken and Hindustan Construction Co. that fraud of an egregious nature and special irretrievable injustice warrants interim interdiction of bank guarantees.

PRAYER:
Restrain the Respondent from encashing or receiving proceeds of Bank Guarantee No. BG-2023-889 pending constitution of the arbitral tribunal.`
  }
];

export const DraftingDashboard = ({ 
  drafts = [], 
  onOpenNewDraft, 
  onSelectDraft 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('ALL');

  // Filter tabs that reflect actual active categories without cluttering with 0s
  const activeCategories = [
    { id: 'ALL', label: 'All Active Drafts', count: drafts.length },
    { id: 'Legal Notice', label: 'Legal Notices', count: drafts.filter(d => d.documentType === 'Legal Notice').length },
    { id: 'Application', label: 'Petitions & Bail', count: drafts.filter(d => d.documentType === 'Application' || d.documentType === 'Petition').length },
    { id: 'Client Letter', label: 'Client Opinions', count: drafts.filter(d => d.documentType === 'Client Letter').length }
  ];

  const filteredDrafts = drafts.filter(d => {
    const q = searchQuery.toLowerCase();
    const matchesSearch = 
      d.title.toLowerCase().includes(q) ||
      (d.caseNumber && d.caseNumber.toLowerCase().includes(q)) ||
      d.documentType.toLowerCase().includes(q);
    
    if (selectedFilter === 'ALL') return matchesSearch;
    if (selectedFilter === 'Application') {
      return matchesSearch && (d.documentType === 'Application' || d.documentType === 'Petition');
    }
    return matchesSearch && d.documentType === selectedFilter;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Final':
        return { color: '#34D399', bg: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)' };
      case 'In Review':
        return { color: '#38BDF8', bg: 'rgba(14, 165, 233, 0.15)', border: '1px solid rgba(14, 165, 233, 0.3)' };
      case 'Draft':
      default:
        return { color: 'var(--color-text-secondary)', bg: 'var(--color-bg-surface-sunken)', border: '1px solid var(--color-border-subtle)' };
    }
  };

  const handleLaunchTemplate = (tmpl) => {
    const newDraftObj = {
      id: `draft-${Date.now()}`,
      title: `${tmpl.title} — New Draft`,
      documentType: tmpl.badge === 'Criminal Defense' ? 'Application' : (tmpl.badge === 'Cheque Dishonour' ? 'Legal Notice' : 'Petition'),
      caseId: 'case-01',
      caseNumber: '2024-CV-1187',
      caseTitle: 'Julian Martinez v. Coastal Holdings Ltd.',
      status: 'Draft',
      version: 'Version 1',
      wordCount: tmpl.defaultContent.split(/\s+/).length,
      createdAt: 'Today, Just now',
      lastModified: 'Just now',
      author: 'Adv. Elena Vance',
      content: tmpl.defaultContent,
      versions: [
        {
          id: `v-${Date.now()}`,
          versionNumber: 'Version 1',
          savedAt: 'Just now',
          wordCount: tmpl.defaultContent.split(/\s+/).length,
          author: 'Adv. Elena Vance',
          changeDescription: `Generated from ${tmpl.title} template`
        }
      ]
    };
    onSelectDraft(newDraftObj);
  };

  return (
    <div className="container" style={{ padding: 'var(--space-xl) var(--space-md)' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h1)', color: 'var(--color-text-primary)', margin: 0 }}>
              Legal Drafting Studio
            </h1>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '2px 8px',
              borderRadius: '10px',
              fontSize: '11px',
              fontWeight: 600,
              backgroundColor: 'rgba(20, 184, 166, 0.15)',
              color: '#2DD4BF',
              border: '1px solid rgba(20, 184, 166, 0.3)'
            }}>
              <Sparkles size={11} /> AI Statutory Assistant Active
            </span>
          </div>
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '4px', marginBottom: 0 }}>
            Court pleadings, ad-interim petitions, statutory notices, and legal briefs with verified Indian law synthesis
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

      {/* 1. Quick-Start Court-Ready Templates Section (What Advocates Actually Use!) */}
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
          <Zap size={14} color="#F59E0B" />
          <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Quick-Start Court-Ready Templates
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '12px' }}>
          {COURT_TEMPLATES.map(tmpl => (
            <div
              key={tmpl.id}
              onClick={() => handleLaunchTemplate(tmpl)}
              className="card-base"
              style={{
                padding: '14px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, border-color 0.15s ease',
                position: 'relative'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{
                    fontSize: '10.5px',
                    fontWeight: 700,
                    padding: '2px 7px',
                    borderRadius: '4px',
                    backgroundColor: tmpl.bg,
                    color: tmpl.color,
                    border: `1px solid ${tmpl.color}40`
                  }}>
                    {tmpl.badge}
                  </span>
                  <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                    {tmpl.courtType}
                  </span>
                </div>

                <h3 style={{ fontSize: '13.5px', fontWeight: 650, color: 'var(--color-text-primary)', margin: '0 0 6px 0', lineHeight: 1.3 }}>
                  {tmpl.title}
                </h3>
                <p style={{ fontSize: '11.5px', color: 'var(--color-text-secondary)', margin: '0 0 10px 0', lineHeight: 1.4 }}>
                  {tmpl.description}
                </p>
              </div>

              <div style={{
                borderTop: '1px solid var(--color-border-subtle)',
                paddingTop: '8px',
                fontSize: '11px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                color: 'var(--color-text-link)',
                fontWeight: 600
              }}>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '10.5px' }}>{tmpl.statute}</span>
                <span>Open & Edit →</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Filter Bar & Search */}
      <div style={{
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
      }}>
        {/* Category Filter Pills */}
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {activeCategories.map(cat => {
            const isSelected = selectedFilter === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedFilter(cat.id)}
                style={{
                  padding: '6px 14px',
                  borderRadius: 'var(--radius-md)',
                  border: isSelected ? '1px solid var(--color-ink-700)' : '1px solid transparent',
                  backgroundColor: isSelected ? 'var(--color-bg-surface-sunken)' : 'transparent',
                  color: isSelected ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                  fontWeight: isSelected ? 650 : 450,
                  fontSize: 'var(--text-caption)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'all 0.15s ease'
                }}
              >
                <span>{cat.label}</span>
                <span style={{
                  fontSize: '10px',
                  fontWeight: 700,
                  padding: '1px 6px',
                  borderRadius: '10px',
                  backgroundColor: isSelected ? 'var(--color-ink-900)' : 'var(--color-bg-surface-sunken)',
                  color: isSelected ? '#FFFFFF' : 'var(--color-text-muted)'
                }}>
                  {cat.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search */}
        <div style={{ position: 'relative', width: '280px', maxWidth: '100%' }}>
          <Search 
            size={15} 
            color="var(--color-text-muted)" 
            style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} 
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search active drafts, dockets…"
            className="input-base"
            style={{
              paddingLeft: '32px',
              paddingTop: '6px',
              paddingBottom: '6px',
              fontSize: 'var(--text-caption)'
            }}
          />
        </div>
      </div>

      {/* 3. Recent Chambers Drafts List */}
      <div className="card-base" style={{ overflow: 'hidden' }}>
        <div style={{
          padding: '12px 16px',
          borderBottom: '1px solid var(--color-border-subtle)',
          backgroundColor: 'var(--color-bg-surface-sunken)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Active Chambers Drafts ({filteredDrafts.length})
          </span>
          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
            Autosaved with full version audit trail
          </span>
        </div>

        {filteredDrafts.length === 0 ? (
          <div style={{ padding: 'var(--space-2xl) var(--space-md)', textAlign: 'center' }}>
            <FileText size={32} color="var(--color-text-muted)" style={{ margin: '0 auto 8px auto', opacity: 0.5 }} />
            <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-body)', margin: 0 }}>
              No drafts found matching your search.
            </p>
          </div>
        ) : (
          <div>
            {filteredDrafts.map((d, index) => {
              const badgeStyle = getStatusBadge(d.status);
              return (
                <div
                  key={d.id}
                  onClick={() => onSelectDraft(d)}
                  style={{
                    padding: '14px 18px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    borderBottom: index < filteredDrafts.length - 1 ? '1px solid var(--color-border-subtle)' : 'none',
                    cursor: 'pointer',
                    transition: 'background-color 0.15s ease'
                  }}
                  className="legal-table-row"
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px', minWidth: 0 }}>
                    <div style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '8px',
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      <FileText size={18} color="var(--color-ink-700)" />
                    </div>

                    <div style={{ minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
                        <span style={{ fontWeight: 650, fontSize: '14px', color: 'var(--color-text-primary)' }}>
                          {d.title}
                        </span>
                        <span style={{
                          fontSize: '10px',
                          fontWeight: 700,
                          padding: '1px 6px',
                          borderRadius: '4px',
                          backgroundColor: badgeStyle.bg,
                          color: badgeStyle.color,
                          border: badgeStyle.border
                        }}>
                          {d.status}
                        </span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: 'var(--color-text-secondary)', flexWrap: 'wrap' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-ink-700)' }}>
                          {d.caseNumber}
                        </span>
                        <span>&bull;</span>
                        <span>{d.documentType}</span>
                        <span>&bull;</span>
                        <span>{d.version}</span>
                        <span>&bull;</span>
                        <span>{d.wordCount} words</span>
                        <span>&bull;</span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-text-muted)' }}>
                          <Clock size={12} /> Modified {d.lastModified}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-text-link)', fontSize: '12.5px', fontWeight: 600, flexShrink: 0 }}>
                    <span>Open in Editor</span>
                    <ChevronRight size={15} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
