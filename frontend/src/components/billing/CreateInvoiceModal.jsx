import React, { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { Plus, Trash2 } from 'lucide-react';

export const CreateInvoiceModal = ({ isOpen, onClose, onInvoiceCreated, cases = [] }) => {
  const [formData, setFormData] = useState({
    client: 'Arun Kumar',
    caseId: cases[0]?.id || 'case-01',
    caseNumber: cases[0]?.caseNumber || '2024-CV-1187',
    caseTitle: cases[0]?.title || 'Legal Matter',
    invoiceNumber: `INV-${Math.floor(1000 + Math.random() * 9000)}`,
    invoiceDate: new Date().toISOString().split('T')[0],
    dueDate: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
    expensesSubtotal: 0,
    taxPercentage: 0,
    paidAmount: 0,
    notes: 'Professional fee bill for interlocutory proceedings.'
  });

  const [items, setItems] = useState([
    { id: 1, description: 'Legal Consultation & Statutory Advisory', quantity: 1, rate: 10000, amount: 10000 },
    { id: 2, description: 'Drafting Notice of Motion / Pleadings', quantity: 1, rate: 15000, amount: 15000 }
  ]);

  const handleCaseChange = (e) => {
    const selected = cases.find(c => c.id === e.target.value);
    if (selected) {
      setFormData(prev => ({
        ...prev,
        caseId: selected.id,
        caseNumber: selected.caseNumber,
        caseTitle: selected.title,
        client: selected.client
      }));
    }
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...items];
    newItems[index][field] = value;
    if (field === 'quantity' || field === 'rate') {
      const q = Number(newItems[index].quantity) || 0;
      const r = Number(newItems[index].rate) || 0;
      newItems[index].amount = q * r;
    }
    setItems(newItems);
  };

  const handleAddItem = () => {
    setItems([
      ...items,
      { id: Date.now(), description: '', quantity: 1, rate: 5000, amount: 5000 }
    ]);
  };

  const handleRemoveItem = (index) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const subtotal = items.reduce((sum, item) => sum + (Number(item.amount) || 0), 0);
  const expenses = Number(formData.expensesSubtotal) || 0;
  const tax = Math.round((subtotal + expenses) * (Number(formData.taxPercentage) / 100));
  const total = subtotal + expenses + tax;
  const paid = Number(formData.paidAmount) || 0;
  const outstanding = Math.max(0, total - paid);

  const handleSubmit = (e) => {
    e.preventDefault();
    onInvoiceCreated({
      ...formData,
      items,
      amount: total,
      paidAmount: paid,
      outstandingAmount: outstanding
    });
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create Professional Fee Invoice"
      subtitle="Generate case fee billing with itemized professional legal services"
      maxWidth="720px"
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
        
        {/* Top Details Row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Associated Matter
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

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Client Name
            </label>
            <input
              type="text"
              value={formData.client}
              onChange={(e) => setFormData(p => ({ ...p, client: e.target.value }))}
              required
              className="input-base"
            />
          </div>
        </div>

        {/* Invoice Number & Dates */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Invoice Number
            </label>
            <input
              type="text"
              value={formData.invoiceNumber}
              onChange={(e) => setFormData(p => ({ ...p, invoiceNumber: e.target.value }))}
              className="input-base"
              style={{ fontFamily: 'var(--font-mono)' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Invoice Date
            </label>
            <input
              type="date"
              value={formData.invoiceDate}
              onChange={(e) => setFormData(p => ({ ...p, invoiceDate: e.target.value }))}
              className="input-base"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Due Date
            </label>
            <input
              type="date"
              value={formData.dueDate}
              onChange={(e) => setFormData(p => ({ ...p, dueDate: e.target.value }))}
              className="input-base"
            />
          </div>
        </div>

        {/* Line Items Section */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: 'var(--text-label)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              Professional Fee Line Items
            </span>
            <button
              type="button"
              onClick={handleAddItem}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--color-text-link)',
                fontSize: '12px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <Plus size={13} /> Add Line Item
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {items.map((item, idx) => (
              <div
                key={item.id}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '3fr 1fr 1.5fr 1.5fr 36px',
                  gap: '8px',
                  alignItems: 'center'
                }}
              >
                <input
                  type="text"
                  placeholder="Service description"
                  value={item.description}
                  onChange={(e) => handleItemChange(idx, 'description', e.target.value)}
                  className="input-base"
                  style={{ fontSize: '13px' }}
                  required
                />
                <input
                  type="number"
                  min="1"
                  placeholder="Qty"
                  value={item.quantity}
                  onChange={(e) => handleItemChange(idx, 'quantity', e.target.value)}
                  className="input-base"
                  style={{ fontSize: '13px' }}
                />
                <input
                  type="number"
                  placeholder="Rate (₹)"
                  value={item.rate}
                  onChange={(e) => handleItemChange(idx, 'rate', e.target.value)}
                  className="input-base"
                  style={{ fontSize: '13px' }}
                />
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 600, color: 'var(--color-ink-700)', padding: '6px' }}>
                  ₹{(item.amount || 0).toLocaleString('en-IN')}
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveItem(idx)}
                  disabled={items.length === 1}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: items.length === 1 ? 'var(--color-border-default)' : 'var(--color-error-text)',
                    cursor: items.length === 1 ? 'not-allowed' : 'pointer',
                    padding: '4px'
                  }}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Expenses & Taxes & Calculations */}
        <div
          style={{
            backgroundColor: 'var(--color-bg-surface-sunken)',
            padding: 'var(--space-md)',
            borderRadius: 'var(--radius-md)',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 'var(--space-lg)',
            fontSize: '13px'
          }}
        >
          <div>
            <div style={{ marginBottom: '8px' }}>
              <label style={{ display: 'block', fontSize: '11px', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>
                Disbursements / Case Expenses (₹)
              </label>
              <input
                type="number"
                value={formData.expensesSubtotal}
                onChange={(e) => setFormData(p => ({ ...p, expensesSubtotal: e.target.value }))}
                className="input-base"
                style={{ height: '32px' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '11px', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>
                Configurable Tax Rate (%) [Optional]
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.taxPercentage}
                onChange={(e) => setFormData(p => ({ ...p, taxPercentage: e.target.value }))}
                className="input-base"
                style={{ height: '32px' }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '4px', textAlign: 'right' }}>
            <div>
              <span style={{ color: 'var(--color-text-secondary)' }}>Fees Subtotal: </span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>₹{subtotal.toLocaleString('en-IN')}</strong>
            </div>
            {expenses > 0 && (
              <div>
                <span style={{ color: 'var(--color-text-secondary)' }}>Expenses: </span>
                <strong style={{ fontFamily: 'var(--font-mono)' }}>₹{expenses.toLocaleString('en-IN')}</strong>
              </div>
            )}
            {tax > 0 && (
              <div>
                <span style={{ color: 'var(--color-text-secondary)' }}>Tax ({formData.taxPercentage}%): </span>
                <strong style={{ fontFamily: 'var(--font-mono)' }}>₹{tax.toLocaleString('en-IN')}</strong>
              </div>
            )}
            <div style={{ borderTop: '1px solid var(--color-border-subtle)', paddingTop: '4px', fontSize: '15px' }}>
              <span>Total Bill: </span>
              <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-ink-700)' }}>
                ₹{total.toLocaleString('en-IN')}
              </strong>
            </div>
          </div>
        </div>

        {/* Modal Buttons */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-sm)' }}>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Issue Invoice
          </Button>
        </div>
      </form>
    </Modal>
  );
};
