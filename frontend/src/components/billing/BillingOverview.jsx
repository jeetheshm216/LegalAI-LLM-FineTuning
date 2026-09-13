import React, { useState } from 'react';
import { 
  Plus, 
  Send, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  ArrowUpRight, 
  FileText,
  DollarSign,
  TrendingUp,
  Receipt
} from 'lucide-react';
import { Button } from '../common/Button';

export const BillingOverview = ({ 
  summary, 
  clientFinancials, 
  reminders, 
  invoices, 
  payments,
  onOpenCreateInvoice, 
  onOpenRecordPayment, 
  onOpenAddExpense,
  onNavigateTab
}) => {
  const [sentReminders, setSentReminders] = useState({});
  const [toastMessage, setToastMessage] = useState(null);

  const handleSendReminder = (remId, client) => {
    setSentReminders(prev => ({ ...prev, [remId]: true }));
    setToastMessage(`Payment reminder notification dispatched to ${client}.`);
    setTimeout(() => setToastMessage(null), 3500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Optional Toast Feedback */}
      {toastMessage && (
        <div
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            backgroundColor: 'var(--color-bg-surface-raised)',
            border: '1px solid var(--color-accent-500)',
            borderLeft: '4px solid var(--color-accent-500)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--elevation-2)',
            padding: '12px 16px',
            fontSize: 'var(--text-caption)',
            color: 'var(--color-text-primary)',
            zIndex: 'var(--z-toast)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            animation: 'fadeIn 0.2s ease-out'
          }}
        >
          <CheckCircle size={16} color="var(--color-accent-700)" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* 1. Summary Cards (4-up grid conforming to theme) */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 'var(--space-md)'
        }}
      >
        {/* Total Billed */}
        <div className="card-base" style={{ padding: 'var(--space-md)' }}>
          <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Total Fees Billed
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-display)', fontWeight: 600, color: 'var(--color-text-primary)', lineHeight: 1.1 }}>
            ₹{summary.totalBilled.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Across all chambers retainers
          </div>
        </div>

        {/* Total Received */}
        <div className="card-base" style={{ padding: 'var(--space-md)' }}>
          <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Total Received
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-display)', fontWeight: 600, color: 'var(--color-success-text)', lineHeight: 1.1 }}>
            ₹{summary.totalReceived.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            73% realization rate
          </div>
        </div>

        {/* Outstanding (Highlight with 4px left border per §9.1 theme rule!) */}
        <div
          className="card-base"
          style={{
            padding: 'var(--space-md)',
            borderLeft: '4px solid var(--color-case-urgent-text)'
          }}
        >
          <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Total Outstanding
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-display)', fontWeight: 600, color: 'var(--color-case-urgent-text)', lineHeight: 1.1 }}>
            ₹{summary.totalOutstanding.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-case-urgent-text)', marginTop: '4px', fontWeight: 500 }}>
            3 invoices require attention
          </div>
        </div>

        {/* Matter Disbursements / Expenses */}
        <div className="card-base" style={{ padding: 'var(--space-md)' }}>
          <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Matter Disbursements
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-display)', fontWeight: 600, color: 'var(--color-text-primary)', lineHeight: 1.1 }}>
            ₹{summary.totalExpenses.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Court fees & travel vouchers
          </div>
        </div>
      </div>

      {/* 2. Main Two-Column Split (65% Client Progress, 35% Payment Reminders) */}
      <div style={{ display: 'grid', gridTemplateColumns: '65% 35%', gap: 'var(--space-lg)' }} className="billing-overview-grid">
        
        {/* Left Column: Client Financial Summaries */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
              <div>
                <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)' }}>
                  Client Financial Accounts
                </h3>
                <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                  Payment realization progress and fee recovery status by client
                </p>
              </div>

              <Button
                variant="secondary"
                size="sm"
                icon={Plus}
                onClick={onOpenCreateInvoice}
              >
                New Invoice
              </Button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
              {clientFinancials.map((client) => (
                <div
                  key={client.clientId}
                  style={{
                    padding: 'var(--space-md)',
                    backgroundColor: 'var(--color-bg-surface-sunken)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--color-border-subtle)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                        {client.clientName}
                      </div>
                      <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                        {client.matter} &bull; <span style={{ fontFamily: 'var(--font-mono)' }}>{client.caseNumber}</span>
                      </div>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Outstanding: </span>
                      <strong style={{ fontFamily: 'var(--font-mono)', fontSize: '15px', color: client.outstanding > 0 ? 'var(--color-case-urgent-text)' : 'var(--color-success-text)' }}>
                        ₹{client.outstanding.toLocaleString('en-IN')}
                      </strong>
                    </div>
                  </div>

                  {/* Visual Payment Progress Indicator per Prompt */}
                  <div style={{ marginBottom: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--color-text-secondary)', marginBottom: '3px' }}>
                      <span>Paid: <strong style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-mono)' }}>₹{client.paid.toLocaleString('en-IN')}</strong> of ₹{client.totalBilled.toLocaleString('en-IN')}</span>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{client.progressPercentage}%</span>
                    </div>
                    <div style={{ height: '8px', backgroundColor: 'var(--color-bg-surface)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div
                        style={{
                          width: `${client.progressPercentage}%`,
                          height: '100%',
                          backgroundColor: 'var(--color-accent-500)',
                          transition: 'width 0.3s ease'
                        }}
                      />
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                    <span>Last tranche paid on: {client.lastPaymentDate}</span>
                    <button
                      onClick={() => onNavigateTab('invoices')}
                      style={{ background: 'none', border: 'none', color: 'var(--color-text-link)', cursor: 'pointer', fontSize: '11px' }}
                    >
                      View invoices &rarr;
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions Row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--space-md)' }}>
            <button
              onClick={onOpenCreateInvoice}
              className="card-interactive"
              style={{
                padding: 'var(--space-md)',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-sm)',
                textAlign: 'left'
              }}
            >
              <FileText size={20} color="var(--color-ink-700)" />
              <div>
                <div style={{ fontWeight: 600, fontSize: 'var(--text-caption)', color: 'var(--color-text-primary)' }}>Create Invoice</div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Itemized billing</div>
              </div>
            </button>

            <button
              onClick={onOpenRecordPayment}
              className="card-interactive"
              style={{
                padding: 'var(--space-md)',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-sm)',
                textAlign: 'left'
              }}
            >
              <CheckCircle size={20} color="var(--color-accent-700)" />
              <div>
                <div style={{ fontWeight: 600, fontSize: 'var(--text-caption)', color: 'var(--color-text-primary)' }}>Record Payment</div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Receipt voucher</div>
              </div>
            </button>

            <button
              onClick={onOpenAddExpense}
              className="card-interactive"
              style={{
                padding: 'var(--space-md)',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-sm)',
                textAlign: 'left'
              }}
            >
              <Receipt size={20} color="var(--color-information-text)" />
              <div>
                <div style={{ fontWeight: 600, fontSize: 'var(--text-caption)', color: 'var(--color-text-primary)' }}>Log Disbursement</div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Court fee challan</div>
              </div>
            </button>
          </div>
        </div>

        {/* Right Column: Payment Reminders (§ Payment Reminders requirement) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          
          <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-xs)' }}>
              <Clock size={18} color="var(--color-case-urgent-text)" />
              <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', color: 'var(--color-text-primary)' }}>
                Payment Reminders
              </h3>
            </div>
            <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-md)' }}>
              Pending and overdue fee invoices requiring follow-up
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              {reminders.map(rem => {
                const isSent = !!sentReminders[rem.id];
                return (
                  <div
                    key={rem.id}
                    style={{
                      padding: 'var(--space-sm)',
                      backgroundColor: 'var(--color-bg-surface-sunken)',
                      borderRadius: 'var(--radius-md)',
                      borderLeft: rem.isUrgent ? '3px solid var(--color-case-urgent-text)' : '1px solid var(--color-border-subtle)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                          {rem.client}
                        </div>
                        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                          Invoice {rem.invoiceNumber} &bull; Docket #{rem.caseNumber}
                        </div>
                      </div>

                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: '14px', color: 'var(--color-case-urgent-text)' }}>
                          ₹{rem.outstanding.toLocaleString('en-IN')}
                        </div>
                        <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
                          Due: {rem.dueDate}
                        </span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'var(--space-xs)', paddingTop: '6px', borderTop: '1px solid var(--color-border-subtle)' }}>
                      <span style={{ fontSize: '11px', color: rem.isUrgent ? 'var(--color-case-urgent-text)' : 'var(--color-text-muted)', fontWeight: 500 }}>
                        {rem.status}
                      </span>

                      <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => onNavigateTab('invoices')}
                        >
                          View
                        </Button>
                        <Button
                          variant={isSent ? "secondary" : "primary"}
                          size="sm"
                          disabled={isSent}
                          icon={Send}
                          onClick={() => handleSendReminder(rem.id, rem.client)}
                        >
                          {isSent ? "Dispatched" : "Send Reminder"}
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quick Realization Summary */}
          <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
            <h4 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', marginBottom: 'var(--space-xs)' }}>
              Practice Financial Health
            </h4>
            <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', lineHeight: 1.5, marginBottom: 'var(--space-sm)' }}>
              All professional fees are segregated from court disbursements. Reimbursable challans must be attached to monthly client statement.
            </div>
            <div style={{ borderTop: '1px solid var(--color-border-subtle)', paddingTop: 'var(--space-xs)', display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
              <span>Average recovery cycle:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>18 days</strong>
            </div>
          </div>

        </div>

      </div>

      <style>{`
        @media (max-width: 900px) {
          .billing-overview-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};
