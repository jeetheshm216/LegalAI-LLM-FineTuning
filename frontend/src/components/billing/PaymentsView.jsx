import React, { useState } from 'react';
import { Search, Plus, Eye, Download, Printer, CheckCircle, X } from 'lucide-react';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';

export const PaymentsView = ({ payments, onOpenRecordPayment }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [methodFilter, setMethodFilter] = useState('ALL');
  const [viewReceipt, setViewReceipt] = useState(null);

  const methods = ['ALL', 'Bank transfer', 'UPI', 'Cheque', 'Cash'];

  const filteredPayments = payments.filter(pay => {
    const matchesSearch = 
      pay.receiptNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pay.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pay.reference.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesMethod = methodFilter === 'ALL' || pay.paymentMethod.toLowerCase() === methodFilter.toLowerCase();
    return matchesSearch && matchesMethod;
  });

  return (
    <div>
      {/* Toolbar */}
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
            placeholder="Search payments, receipts, reference…"
            className="input-base"
            style={{ paddingLeft: '32px', paddingTop: '4px', paddingBottom: '4px', fontSize: 'var(--text-caption)' }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2xs)', overflowX: 'auto' }}>
          {methods.map(m => {
            const isSelected = methodFilter === m;
            return (
              <button
                key={m}
                onClick={() => setMethodFilter(m)}
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
                {m}
              </button>
            );
          })}
        </div>

        <Button
          variant="primary"
          size="sm"
          icon={Plus}
          onClick={onOpenRecordPayment}
        >
          Record Payment
        </Button>
      </div>

      {/* Payments Register Table */}
      <div className="card-base" style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface-sunken)' }}>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Receipt #</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Payment Date</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Client & Matter</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Invoice Ref</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Method</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Amount</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', textAlign: 'right' }}>Receipt</th>
            </tr>
          </thead>
          <tbody>
            {filteredPayments.map(pay => (
              <tr key={pay.id} style={{ height: '56px', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-mono)', fontWeight: 600, color: 'var(--color-ink-700)' }}>
                  {pay.receiptNumber}
                </td>
                <td style={{ padding: '12px 16px', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
                  {pay.paymentDate}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <div style={{ fontWeight: 600, fontSize: 'var(--text-body)', color: 'var(--color-text-primary)' }}>
                    {pay.client}
                  </div>
                  <div style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-muted)' }}>
                    {pay.caseNumber}
                  </div>
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                  {pay.invoiceNumber}
                </td>
                <td style={{ padding: '12px 16px', fontSize: 'var(--text-caption)' }}>
                  <span style={{ padding: '2px 6px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--color-bg-surface-sunken)', color: 'var(--color-text-secondary)' }}>
                    {pay.paymentMethod}
                  </span>
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-body)', fontWeight: 600, color: 'var(--color-success-text)' }}>
                  ₹{pay.amount.toLocaleString('en-IN')}
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                  <Button
                    variant="secondary"
                    size="sm"
                    icon={Eye}
                    onClick={() => setViewReceipt(pay)}
                  >
                    Receipt
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Receipt Modal */}
      {viewReceipt && (
        <Modal
          isOpen={!!viewReceipt}
          onClose={() => setViewReceipt(null)}
          title="Official Receipt Voucher"
          subtitle="Chambers official acknowledgment of fee settlement"
          maxWidth="480px"
        >
          <div
            style={{
              backgroundColor: 'var(--color-doc-page)',
              color: '#171E26',
              padding: 'var(--space-lg)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border-subtle)',
              fontFamily: 'var(--font-serif)',
              marginBottom: 'var(--space-md)'
            }}
          >
            <div style={{ textAlign: 'center', borderBottom: '1px solid #D3CFC5', paddingBottom: '8px', marginBottom: '12px' }}>
              <div style={{ fontSize: '16px', fontWeight: 700, color: '#1B2836' }}>Vance & Associates</div>
              <div style={{ fontSize: '11px', color: '#5C7086' }}>OFFICIAL FEE RECEIPT VOUCHER</div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '8px' }}>
              <span>Receipt No: <strong>{viewReceipt.receiptNumber}</strong></span>
              <span>Date: {viewReceipt.paymentDate}</span>
            </div>

            <div style={{ fontSize: '13px', lineHeight: 1.6, marginBottom: '12px', fontFamily: 'var(--font-sans)' }}>
              Received with thanks from <strong>{viewReceipt.client}</strong> the sum of:
              <div style={{ fontSize: '18px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#1E6B45', margin: '4px 0' }}>
                ₹{viewReceipt.amount.toLocaleString('en-IN')}
              </div>
              toward satisfaction of Invoice #{viewReceipt.invoiceNumber} (Docket #{viewReceipt.caseNumber}).
            </div>

            <div style={{ fontSize: '11px', color: '#5C7086', borderTop: '1px solid #E4E1DA', paddingTop: '8px' }}>
              Payment Mode: {viewReceipt.paymentMethod} &bull; Ref: {viewReceipt.reference}
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
              <Button variant="secondary" size="sm" icon={Printer} onClick={() => alert("Printing receipt...")}>
                Print
              </Button>
              <Button variant="secondary" size="sm" icon={Download} onClick={() => alert("Downloading receipt PDF...")}>
                PDF
              </Button>
            </div>
            <Button variant="primary" size="sm" onClick={() => setViewReceipt(null)}>
              Close
            </Button>
          </div>
        </Modal>
      )}
    </div>
  );
};
