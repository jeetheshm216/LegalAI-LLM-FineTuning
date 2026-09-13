import React, { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';

export const RecordPaymentModal = ({ isOpen, onClose, onPaymentRecorded, invoices = [] }) => {
  const [formData, setFormData] = useState({
    invoiceNumber: invoices[0]?.invoiceNumber || 'INV-0012',
    client: invoices[0]?.client || 'Arun Kumar',
    amount: invoices[0]?.outstandingAmount || 15000,
    paymentDate: new Date().toISOString().split('T')[0],
    paymentMethod: 'Bank transfer',
    reference: '',
    notes: 'Tranche settlement received.'
  });

  const handleInvoiceChange = (e) => {
    const inv = invoices.find(i => i.invoiceNumber === e.target.value);
    if (inv) {
      setFormData(prev => ({
        ...prev,
        invoiceNumber: inv.invoiceNumber,
        client: inv.client,
        amount: inv.outstandingAmount || inv.amount,
        caseId: inv.caseId,
        caseNumber: inv.caseNumber
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onPaymentRecorded(formData);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Record Client Payment"
      subtitle="Register fee tranches, retainers, and expense reimbursements"
      maxWidth="560px"
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
        <div>
          <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Associated Invoice
          </label>
          <select
            value={formData.invoiceNumber}
            onChange={handleInvoiceChange}
            className="input-base"
          >
            {invoices.map(inv => (
              <option key={inv.id} value={inv.invoiceNumber}>
                {inv.invoiceNumber} — {inv.client} (₹{inv.outstandingAmount.toLocaleString('en-IN')} outstanding)
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Client Name
            </label>
            <input
              type="text"
              readOnly
              value={formData.client}
              className="input-base"
              style={{ backgroundColor: 'var(--color-bg-canvas)' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Amount Received (₹) <span style={{ color: 'var(--color-error-text)' }}>*</span>
            </label>
            <input
              type="number"
              required
              value={formData.amount}
              onChange={(e) => setFormData(p => ({ ...p, amount: e.target.value }))}
              className="input-base"
              style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Payment Method
            </label>
            <select
              value={formData.paymentMethod}
              onChange={(e) => setFormData(p => ({ ...p, paymentMethod: e.target.value }))}
              className="input-base"
            >
              <option value="Bank transfer">Bank Transfer (NEFT/RTGS)</option>
              <option value="UPI">UPI / Instant Pay</option>
              <option value="Cheque">Cheque Deposit</option>
              <option value="Cash">Cash Receipt</option>
              <option value="Other">Other Escrow</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Payment Date
            </label>
            <input
              type="date"
              value={formData.paymentDate}
              onChange={(e) => setFormData(p => ({ ...p, paymentDate: e.target.value }))}
              className="input-base"
            />
          </div>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Transaction Reference / UTR / Cheque Number
          </label>
          <input
            type="text"
            placeholder="e.g. UTR-SBI-8819203 or Cheque #441920"
            value={formData.reference}
            onChange={(e) => setFormData(p => ({ ...p, reference: e.target.value }))}
            className="input-base"
            style={{ fontFamily: 'var(--font-mono)' }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-sm)' }}>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Confirm Payment Entry
          </Button>
        </div>
      </form>
    </Modal>
  );
};
