import React, { useState } from 'react';
import { Search, Plus, Eye, Printer, Download, X, FileText } from 'lucide-react';
import { Button } from '../common/Button';

export const InvoicesView = ({ invoices, onOpenCreateInvoice }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [viewInvoice, setViewInvoice] = useState(null);

  const statuses = ['ALL', 'Paid', 'Partially Paid', 'Overdue', 'Sent', 'Draft'];

  const filteredInvoices = invoices.filter(inv => {
    const matchesSearch = 
      inv.invoiceNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.caseNumber.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || inv.status.toLowerCase() === statusFilter.toLowerCase();
    return matchesSearch && matchesStatus;
  });

  const getStatusBadgeStyle = (status) => {
    switch (status.toLowerCase()) {
      case 'paid':
        return { color: 'var(--color-success-text)', bg: 'var(--color-success-wash)' };
      case 'partially paid':
        return { color: 'var(--color-information-text)', bg: 'var(--color-information-wash)' };
      case 'overdue':
        return { color: 'var(--color-error-text)', bg: 'var(--color-error-wash)' };
      default:
        return { color: 'var(--color-text-secondary)', bg: 'var(--color-bg-surface-sunken)' };
    }
  };

  return (
    <div>
      {/* Action & Filter Toolbar */}
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
        <div style={{ position: 'relative', width: '300px', maxWidth: '100%' }}>
          <Search size={15} color="var(--color-text-muted)" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search invoices, clients, docket #…"
            className="input-base"
            style={{ paddingLeft: '32px', paddingTop: '4px', paddingBottom: '4px', fontSize: 'var(--text-caption)' }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2xs)', overflowX: 'auto' }}>
          {statuses.map(st => {
            const isSelected = statusFilter === st;
            return (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
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
                {st}
              </button>
            );
          })}
        </div>

        <Button
          variant="primary"
          size="sm"
          icon={Plus}
          onClick={onOpenCreateInvoice}
        >
          Create Invoice
        </Button>
      </div>

      {/* Invoices Register Table */}
      <div className="card-base" style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface-sunken)' }}>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Invoice #</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Client & Matter</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Invoice Date</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Due Date</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Total Amount</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Outstanding</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Status</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredInvoices.map((inv) => {
              const badge = getStatusBadgeStyle(inv.status);
              return (
                <tr
                  key={inv.id}
                  style={{
                    height: '56px',
                    borderBottom: '1px solid var(--color-border-subtle)'
                  }}
                >
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-mono)', fontWeight: 600, color: 'var(--color-ink-700)' }}>
                    {inv.invoiceNumber}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                      {inv.client}
                    </div>
                    <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                      {inv.caseNumber} &bull; {inv.caseTitle}
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
                    {inv.invoiceDate}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
                    {inv.dueDate}
                  </td>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-body)', fontWeight: 600 }}>
                    ₹{inv.amount.toLocaleString('en-IN')}
                  </td>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-body)', fontWeight: 600, color: inv.outstandingAmount > 0 ? 'var(--color-case-urgent-text)' : 'var(--color-success-text)' }}>
                    ₹{inv.outstandingAmount.toLocaleString('en-IN')}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: 'var(--text-caption)',
                        fontWeight: 500,
                        color: badge.color,
                        backgroundColor: badge.bg
                      }}
                    >
                      {inv.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                    <Button
                      variant="secondary"
                      size="sm"
                      icon={Eye}
                      onClick={() => setViewInvoice(inv)}
                    >
                      View
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Invoice Detail Slide-Over Preview Modal */}
      {viewInvoice && (
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
          onClick={() => setViewInvoice(null)}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '520px',
              backgroundColor: 'var(--color-bg-surface-raised)',
              height: '100%',
              boxShadow: 'var(--elevation-3)',
              display: 'flex',
              flexDirection: 'column'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div style={{ padding: 'var(--space-md) var(--space-lg)', borderBottom: '1px solid var(--color-border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: 'var(--text-h3)' }}>Invoice Details</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                  {viewInvoice.invoiceNumber}
                </div>
              </div>
              <button onClick={() => setViewInvoice(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}>
                <X size={18} />
              </button>
            </div>

            {/* Invoice Printable View */}
            <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-lg)', backgroundColor: 'var(--color-bg-canvas)' }}>
              <div
                style={{
                  backgroundColor: 'var(--color-doc-page)',
                  color: '#171E26',
                  padding: 'var(--space-xl)',
                  borderRadius: 'var(--radius-sm)',
                  boxShadow: 'var(--elevation-1)',
                  border: '1px solid var(--color-border-subtle)'
                }}
              >
                {/* Chambers Wordmark */}
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '2px solid #1B2836', paddingBottom: 'var(--space-sm)', marginBottom: 'var(--space-md)' }}>
                  <div>
                    <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: '20px', color: '#1B2836' }}>Vance & Associates</h3>
                    <p style={{ fontSize: '11px', color: '#5C7086' }}>Advocates & Legal Consultants &bull; High Court Chambers</p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: 600 }}>{viewInvoice.invoiceNumber}</div>
                    <div style={{ fontSize: '11px', color: '#5C7086' }}>Date: {viewInvoice.invoiceDate}</div>
                  </div>
                </div>

                <div style={{ marginBottom: 'var(--space-md)', fontSize: '12px' }}>
                  <strong>Billed To:</strong> {viewInvoice.client}<br/>
                  <strong>Matter Reference:</strong> {viewInvoice.caseNumber} &mdash; {viewInvoice.caseTitle}
                </div>

                {/* Line Items */}
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', marginBottom: 'var(--space-md)' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #D3CFC5', textAlign: 'left' }}>
                      <th style={{ padding: '6px 0' }}>Description</th>
                      <th style={{ padding: '6px 0', textAlign: 'right' }}>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {viewInvoice.items?.map((item, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid #E4E1DA' }}>
                        <td style={{ padding: '6px 0' }}>{item.description}</td>
                        <td style={{ padding: '6px 0', textAlign: 'right', fontFamily: 'var(--font-mono)' }}>₹{item.amount.toLocaleString('en-IN')}</td>
                      </tr>
                    ))}
                    {viewInvoice.expensesSubtotal > 0 && (
                      <tr style={{ borderBottom: '1px solid #E4E1DA' }}>
                        <td style={{ padding: '6px 0', color: '#5C7086' }}>Reimbursable Matter Expenses</td>
                        <td style={{ padding: '6px 0', textAlign: 'right', fontFamily: 'var(--font-mono)' }}>₹{viewInvoice.expensesSubtotal.toLocaleString('en-IN')}</td>
                      </tr>
                    )}
                  </tbody>
                </table>

                {/* Totals */}
                <div style={{ textAlign: 'right', fontSize: '13px', display: 'flex', flexDirection: 'column', gap: '3px' }}>
                  <div>Total Billed: <strong style={{ fontFamily: 'var(--font-mono)' }}>₹{viewInvoice.amount.toLocaleString('en-IN')}</strong></div>
                  <div style={{ color: '#1E6B45' }}>Paid to Date: <strong style={{ fontFamily: 'var(--font-mono)' }}>₹{viewInvoice.paidAmount.toLocaleString('en-IN')}</strong></div>
                  <div style={{ fontSize: '15px', color: '#9B3B2C', borderTop: '1px solid #D3CFC5', paddingTop: '4px' }}>
                    Outstanding: <strong style={{ fontFamily: 'var(--font-mono)' }}>₹{viewInvoice.outstandingAmount.toLocaleString('en-IN')}</strong>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer Actions */}
            <div style={{ padding: 'var(--space-md)', borderTop: '1px solid var(--color-border-subtle)', display: 'flex', justifyContent: 'space-between', backgroundColor: 'var(--color-bg-surface)' }}>
              <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
                <Button variant="secondary" size="sm" icon={Printer} onClick={() => alert("Printing invoice copy...")}>
                  Print
                </Button>
                <Button variant="secondary" size="sm" icon={Download} onClick={() => alert("Downloading PDF...")}>
                  PDF
                </Button>
              </div>
              <Button variant="primary" size="sm" onClick={() => setViewInvoice(null)}>
                Done
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
