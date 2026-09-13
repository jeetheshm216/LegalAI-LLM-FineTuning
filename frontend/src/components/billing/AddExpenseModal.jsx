import React, { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { Paperclip } from 'lucide-react';

export const AddExpenseModal = ({ isOpen, onClose, onExpenseAdded, cases = [] }) => {
  const [formData, setFormData] = useState({
    caseId: cases[0]?.id || 'case-01',
    caseNumber: cases[0]?.caseNumber || '2024-CV-1187',
    caseTitle: cases[0]?.title || 'Legal Matter',
    category: 'Court fees',
    description: '',
    amount: '',
    date: new Date().toISOString().split('T')[0],
    notes: '',
    receiptAttached: true
  });

  const handleCaseChange = (e) => {
    const selected = cases.find(c => c.id === e.target.value);
    if (selected) {
      setFormData(prev => ({
        ...prev,
        caseId: selected.id,
        caseNumber: selected.caseNumber,
        caseTitle: selected.title
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.description || !formData.amount) return;
    onExpenseAdded(formData);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Record Matter Disbursement / Expense"
      subtitle="Log court fees, filing challans, travel, or external expert costs"
      maxWidth="560px"
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
        <div>
          <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Associated Matter / Docket <span style={{ color: 'var(--color-error-text)' }}>*</span>
          </label>
          <select
            value={formData.caseId}
            onChange={handleCaseChange}
            className="input-base"
          >
            {cases.map(c => (
              <option key={c.id} value={c.id}>
                {c.caseNumber} — {c.title}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Expense Category
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData(p => ({ ...p, category: e.target.value }))}
              className="input-base"
            >
              <option value="Court fees">Court fees</option>
              <option value="Filing fees">Filing fees</option>
              <option value="Travel">Travel</option>
              <option value="Documentation">Documentation</option>
              <option value="Printing">Printing</option>
              <option value="Professional services">Professional services</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Amount (₹) <span style={{ color: 'var(--color-error-text)' }}>*</span>
            </label>
            <input
              type="number"
              required
              placeholder="e.g. 5000"
              value={formData.amount}
              onChange={(e) => setFormData(p => ({ ...p, amount: e.target.value }))}
              className="input-base"
              style={{ fontFamily: 'var(--font-mono)' }}
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Expense Date
            </label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData(p => ({ ...p, date: e.target.value }))}
              className="input-base"
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Receipt Attachment
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
              <input
                type="checkbox"
                checked={formData.receiptAttached}
                onChange={(e) => setFormData(p => ({ ...p, receiptAttached: e.target.checked }))}
                style={{ accentColor: 'var(--color-accent-500)', cursor: 'pointer' }}
              />
              <span>Voucher / Challan receipt on file</span>
            </div>
          </div>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Description <span style={{ color: 'var(--color-error-text)' }}>*</span>
          </label>
          <input
            type="text"
            required
            placeholder="e.g. Commercial Division registry court fee stamp"
            value={formData.description}
            onChange={(e) => setFormData(p => ({ ...p, description: e.target.value }))}
            className="input-base"
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Internal Notes / Challan Number
          </label>
          <textarea
            rows={2}
            placeholder="e.g. Challan No. HC-COM-2026-881 attached."
            value={formData.notes}
            onChange={(e) => setFormData(p => ({ ...p, notes: e.target.value }))}
            className="input-base"
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-sm)' }}>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Record Expense
          </Button>
        </div>
      </form>
    </Modal>
  );
};
