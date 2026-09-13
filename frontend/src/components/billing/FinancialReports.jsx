import React from 'react';
import { Download, Printer } from 'lucide-react';
import { Button } from '../common/Button';

export const FinancialReports = ({ summary, invoices, expenses, clientFinancials }) => {
  const monthlyData = [
    { month: 'Jun 2026', billed: 40000, received: 35000, expenses: 8000 },
    { month: 'Jul 2026', billed: 65000, received: 45000, expenses: 9500 },
    { month: 'Aug 2026', billed: 80000, received: 55000, expenses: 7300 },
    { month: 'Sep 2026', billed: 55000, received: 40000, expenses: 5800 }
  ];

  const maxAmount = 90000;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
      {/* Top Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-text-primary)' }}>
            Chambers Financial Audit & Practice Reports
          </h2>
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            Quarterly revenue collection, case disbursements, and outstanding fee recovery
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
          <Button variant="secondary" size="sm" icon={Printer} onClick={() => alert("Printing report...")}>
            Print Report
          </Button>
          <Button variant="secondary" size="sm" icon={Download} onClick={() => alert("Exporting report CSV/PDF...")}>
            Export Audit
          </Button>
        </div>
      </div>

      {/* 1. Monthly Revenue & Collections Chart (Restrained Monochrome Bars per §24) */}
      <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
        <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', marginBottom: 'var(--space-xs)' }}>
          Monthly Collections vs Billed Fees
        </h3>
        <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-lg)' }}>
          Comparison of professional fees billed (<span style={{ color: 'var(--color-ink-500)', fontWeight: 600 }}>Ink bar</span>) and actual receipts realized (<span style={{ color: 'var(--color-accent-500)', fontWeight: 600 }}>Verdigris bar</span>).
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          {monthlyData.map((item) => (
            <div key={item.month} style={{ display: 'grid', gridTemplateColumns: '90px 1fr 140px', alignItems: 'center', gap: 'var(--space-md)' }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
                {item.month}
              </div>

              {/* Stacked Proportional Bars */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {/* Billed */}
                <div style={{ display: 'flex', alignItems: 'center', height: '12px', backgroundColor: 'var(--color-bg-surface-sunken)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${(item.billed / maxAmount) * 100}%`,
                      height: '100%',
                      backgroundColor: 'var(--color-ink-500)'
                    }}
                    title={`Billed: ₹${item.billed.toLocaleString('en-IN')}`}
                  />
                </div>
                {/* Received */}
                <div style={{ display: 'flex', alignItems: 'center', height: '12px', backgroundColor: 'var(--color-bg-surface-sunken)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${(item.received / maxAmount) * 100}%`,
                      height: '100%',
                      backgroundColor: 'var(--color-accent-500)'
                    }}
                    title={`Received: ₹${item.received.toLocaleString('en-IN')}`}
                  />
                </div>
              </div>

              {/* Data numbers */}
              <div style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
                <div>Billed: ₹{item.billed.toLocaleString('en-IN')}</div>
                <div style={{ color: 'var(--color-accent-700)', fontWeight: 600 }}>Rec: ₹{item.received.toLocaleString('en-IN')}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Client Payment Recovery Table */}
      <div className="card-base" style={{ padding: 'var(--space-lg)' }}>
        <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h3)', marginBottom: 'var(--space-md)' }}>
          Matter Recovery Summary & Outstanding Receivables
        </h3>

        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 'var(--text-caption)' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--color-border-subtle)', backgroundColor: 'var(--color-bg-surface-sunken)' }}>
              <th style={{ padding: '10px 12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Client</th>
              <th style={{ padding: '10px 12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Matter Reference</th>
              <th style={{ padding: '10px 12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Total Billed</th>
              <th style={{ padding: '10px 12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Total Paid</th>
              <th style={{ padding: '10px 12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Outstanding Balance</th>
              <th style={{ padding: '10px 12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Realization %</th>
            </tr>
          </thead>
          <tbody>
            {clientFinancials.map(cf => (
              <tr key={cf.clientId} style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
                <td style={{ padding: '10px 12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>{cf.clientName}</td>
                <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)' }}>{cf.caseNumber}</td>
                <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)' }}>₹{cf.totalBilled.toLocaleString('en-IN')}</td>
                <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', color: 'var(--color-success-text)' }}>₹{cf.paid.toLocaleString('en-IN')}</td>
                <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', color: 'var(--color-case-urgent-text)', fontWeight: 600 }}>₹{cf.outstanding.toLocaleString('en-IN')}</td>
                <td style={{ padding: '10px 12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <div style={{ width: '60px', height: '6px', backgroundColor: 'var(--color-bg-surface-sunken)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${cf.progressPercentage}%`, height: '100%', backgroundColor: 'var(--color-accent-500)' }} />
                    </div>
                    <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}>{cf.progressPercentage}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
