import React, { useState } from 'react';
import { Search, Plus, Paperclip, CheckCircle } from 'lucide-react';
import { Button } from '../common/Button';

export const ExpensesView = ({ expenses, onOpenAddExpense }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  const categories = ['ALL', 'Court fees', 'Filing fees', 'Travel', 'Documentation', 'Printing', 'Professional services'];

  const filteredExpenses = expenses.filter(exp => {
    const matchesSearch = 
      exp.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      exp.caseNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      exp.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = selectedCategory === 'ALL' || exp.category.toLowerCase() === selectedCategory.toLowerCase();
    return matchesSearch && matchesCat;
  });

  const totalExpenseSum = filteredExpenses.reduce((sum, e) => sum + (e.amount || 0), 0);

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
        <div style={{ position: 'relative', width: '280px', maxWidth: '100%' }}>
          <Search size={15} color="var(--color-text-muted)" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search expenses, challans, matter…"
            className="input-base"
            style={{ paddingLeft: '32px', paddingTop: '4px', paddingBottom: '4px', fontSize: 'var(--text-caption)' }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2xs)', overflowX: 'auto' }}>
          {categories.map(cat => {
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
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
                {cat}
              </button>
            );
          })}
        </div>

        <Button
          variant="primary"
          size="sm"
          icon={Plus}
          onClick={onOpenAddExpense}
        >
          Record Expense
        </Button>
      </div>

      {/* Expenses Table */}
      <div className="card-base" style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface-sunken)' }}>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Date</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Category</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Matter Docket</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Description & Notes</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', textAlign: 'center' }}>Voucher</th>
              <th style={{ padding: '12px 16px', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', textAlign: 'right' }}>Amount</th>
            </tr>
          </thead>
          <tbody>
            {filteredExpenses.map(exp => (
              <tr key={exp.id} style={{ height: '56px', borderBottom: '1px solid var(--color-border-subtle)' }}>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                  {exp.date}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ padding: '2px 8px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--color-bg-surface-sunken)', fontSize: 'var(--text-caption)', color: 'var(--color-text-primary)' }}>
                    {exp.category}
                  </span>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-mono)', fontWeight: 600, color: 'var(--color-ink-700)' }}>
                    {exp.caseNumber}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                    {exp.caseTitle}
                  </div>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <div style={{ fontSize: 'var(--text-body)', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                    {exp.description}
                  </div>
                  {exp.notes && (
                    <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                      {exp.notes}
                    </div>
                  )}
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                  {exp.receiptAttached ? (
                    <Paperclip size={15} color="var(--color-accent-700)" title="Receipt attached" />
                  ) : (
                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>None</span>
                  )}
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-body)', fontWeight: 600, color: 'var(--color-ink-700)' }}>
                  ₹{exp.amount.toLocaleString('en-IN')}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr style={{ backgroundColor: 'var(--color-bg-surface-sunken)', fontWeight: 600 }}>
              <td colSpan={5} style={{ padding: '12px 16px', fontSize: 'var(--text-caption)' }}>
                Total Recorded Expenses ({filteredExpenses.length} items)
              </td>
              <td style={{ padding: '12px 16px', textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '15px', color: 'var(--color-ink-700)' }}>
                ₹{totalExpenseSum.toLocaleString('en-IN')}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};
