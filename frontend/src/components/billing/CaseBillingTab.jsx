import React from 'react';
import { Plus, CreditCard, Receipt, FileText } from 'lucide-react';
import { Button } from '../common/Button';

export const CaseBillingTab = ({ 
  currentCase, 
  caseFinances, 
  onOpenCreateInvoice, 
  onOpenRecordPayment,
  onOpenAddExpense 
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
      {/* Top Summary Card */}
      <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
          <div>
            <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)' }}>
              Matter Financial Ledger — {currentCase.caseNumber}
            </h3>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
              Client: <strong>{currentCase.client}</strong> &bull; {currentCase.title}
            </p>
          </div>

          <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
            <Button variant="secondary" size="sm" onClick={onOpenAddExpense}>
              Log Disbursement
            </Button>
            <Button variant="secondary" size="sm" onClick={onOpenRecordPayment}>
              Record Payment
            </Button>
            <Button variant="primary" size="sm" icon={Plus} onClick={onOpenCreateInvoice}>
              New Invoice
            </Button>
          </div>
        </div>

        {/* Financial Breakdown Grid matching User prompt example */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: 'var(--space-md)',
            padding: 'var(--space-md)',
            backgroundColor: 'var(--color-bg-surface-sunken)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 'var(--space-md)'
          }}
        >
          <div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>Professional Fees</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '18px', fontWeight: 600, color: 'var(--color-ink-700)' }}>
              ₹40,000
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>Court Fees & Stamps</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '18px', fontWeight: 600, color: 'var(--color-ink-700)' }}>
              ₹5,000
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>Travel & Inspection</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '18px', fontWeight: 600, color: 'var(--color-ink-700)' }}>
              ₹3,000
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>Other Expenses</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '18px', fontWeight: 600, color: 'var(--color-ink-700)' }}>
              ₹2,000
            </div>
          </div>
        </div>

        {/* Realization Progress Bar */}
        <div style={{ padding: 'var(--space-sm) 0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
            <div>
              <span>Total Case Dues: <strong style={{ fontFamily: 'var(--font-mono)' }}>₹50,000</strong></span>
              <span style={{ margin: '0 8px', color: 'var(--color-text-muted)' }}>&bull;</span>
              <span>Paid: <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-success-text)' }}>₹35,000</strong></span>
            </div>
            <div>
              <span>Outstanding: <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-case-urgent-text)' }}>₹15,000</strong></span>
            </div>
          </div>

          <div style={{ height: '8px', backgroundColor: 'var(--color-bg-surface-sunken)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: '70%', height: '100%', backgroundColor: 'var(--color-accent-500)' }} />
          </div>
        </div>
      </div>

      {/* Invoices & Disbursements Sub-Sections */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }} className="case-finance-split">
        {/* Matter Invoices */}
        <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
          <h4 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', marginBottom: 'var(--space-sm)' }}>
            Matter Invoices
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
            {caseFinances?.invoices?.map(inv => (
              <div
                key={inv.id}
                style={{
                  padding: 'var(--space-sm)',
                  backgroundColor: 'var(--color-bg-surface-sunken)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: '12px' }}>{inv.invoiceNumber}</div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Due: {inv.dueDate} &bull; {inv.status}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>₹{inv.amount.toLocaleString('en-IN')}</div>
                  <div style={{ fontSize: '11px', color: 'var(--color-case-urgent-text)' }}>₹{inv.outstandingAmount.toLocaleString('en-IN')} due</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Matter Disbursements */}
        <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
          <h4 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', marginBottom: 'var(--space-sm)' }}>
            Recorded Matter Disbursements
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
            {caseFinances?.expenses?.map(exp => (
              <div
                key={exp.id}
                style={{
                  padding: 'var(--space-sm)',
                  backgroundColor: 'var(--color-bg-surface-sunken)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <div style={{ fontWeight: 500, fontSize: '12px' }}>{exp.description}</div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>{exp.category} &bull; {exp.date}</div>
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                  ₹{exp.amount.toLocaleString('en-IN')}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 800px) {
          .case-finance-split {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};
