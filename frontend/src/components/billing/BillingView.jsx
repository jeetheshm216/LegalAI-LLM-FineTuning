import React, { useState } from 'react';
import { 
  FileText, 
  CreditCard, 
  Receipt, 
  BarChart3, 
  LayoutDashboard,
  Plus
} from 'lucide-react';
import { Button } from '../common/Button';
import { BillingOverview } from './BillingOverview';
import { InvoicesView } from './InvoicesView';
import { PaymentsView } from './PaymentsView';
import { ExpensesView } from './ExpensesView';
import { FinancialReports } from './FinancialReports';
import { CreateInvoiceModal } from './CreateInvoiceModal';
import { RecordPaymentModal } from './RecordPaymentModal';
import { AddExpenseModal } from './AddExpenseModal';

export const BillingView = ({ 
  summary, 
  clientFinancials, 
  invoices, 
  payments, 
  expenses, 
  reminders,
  cases,
  onCreateInvoice,
  onRecordPayment,
  onAddExpense
}) => {
  const [activeTab, setActiveTab] = useState('overview'); // overview, invoices, payments, expenses, reports
  const [isCreateInvoiceOpen, setIsCreateInvoiceOpen] = useState(false);
  const [isRecordPaymentOpen, setIsRecordPaymentOpen] = useState(false);
  const [isAddExpenseOpen, setIsAddExpenseOpen] = useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'invoices', label: `Invoices (${invoices.length})`, icon: FileText },
    { id: 'payments', label: `Payments (${payments.length})`, icon: CreditCard },
    { id: 'expenses', label: `Expenses (${expenses.length})`, icon: Receipt },
    { id: 'reports', label: 'Financial Reports', icon: BarChart3 }
  ];

  return (
    <div className="container" style={{ padding: 'var(--space-xl) var(--space-md)' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h1)', color: 'var(--color-text-primary)' }}>
            Chambers Billing & Finance
          </h1>
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            Professional fee invoicing, client account balances, matter disbursements, and revenue reports
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIsRecordPaymentOpen(true)}
          >
            Record Payment
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() => setIsCreateInvoiceOpen(true)}
          >
            New Invoice
          </Button>
        </div>
      </div>

      {/* Horizontal Underline Tabs (§8/§11 style) */}
      <div
        style={{
          display: 'flex',
          gap: 'var(--space-lg)',
          borderBottom: '1px solid var(--color-border-subtle)',
          marginBottom: 'var(--space-xl)',
          overflowX: 'auto'
        }}
      >
        {tabs.map(tab => {
          const isActive = activeTab === tab.id;
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: 'none',
                border: 'none',
                padding: 'var(--space-sm) 0',
                cursor: 'pointer',
                fontFamily: 'var(--font-sans)',
                fontSize: 'var(--text-h3)',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? 'var(--color-ink-700)' : 'var(--color-text-secondary)',
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                whiteSpace: 'nowrap'
              }}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
              {isActive && (
                <span
                  style={{
                    position: 'absolute',
                    bottom: '-1px',
                    left: 0,
                    right: 0,
                    height: '2px',
                    backgroundColor: 'var(--color-ink-700)'
                  }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      {activeTab === 'overview' && (
        <BillingOverview
          summary={summary}
          clientFinancials={clientFinancials}
          reminders={reminders}
          invoices={invoices}
          payments={payments}
          onOpenCreateInvoice={() => setIsCreateInvoiceOpen(true)}
          onOpenRecordPayment={() => setIsRecordPaymentOpen(true)}
          onOpenAddExpense={() => setIsAddExpenseOpen(true)}
          onNavigateTab={(tab) => setActiveTab(tab)}
        />
      )}

      {activeTab === 'invoices' && (
        <InvoicesView
          invoices={invoices}
          onOpenCreateInvoice={() => setIsCreateInvoiceOpen(true)}
        />
      )}

      {activeTab === 'payments' && (
        <PaymentsView
          payments={payments}
          onOpenRecordPayment={() => setIsRecordPaymentOpen(true)}
        />
      )}

      {activeTab === 'expenses' && (
        <ExpensesView
          expenses={expenses}
          onOpenAddExpense={() => setIsAddExpenseOpen(true)}
        />
      )}

      {activeTab === 'reports' && (
        <FinancialReports
          summary={summary}
          invoices={invoices}
          expenses={expenses}
          clientFinancials={clientFinancials}
        />
      )}

      {/* Modals */}
      <CreateInvoiceModal
        isOpen={isCreateInvoiceOpen}
        onClose={() => setIsCreateInvoiceOpen(false)}
        onInvoiceCreated={onCreateInvoice}
        cases={cases}
      />

      <RecordPaymentModal
        isOpen={isRecordPaymentOpen}
        onClose={() => setIsRecordPaymentOpen(false)}
        onPaymentRecorded={onRecordPayment}
        invoices={invoices}
      />

      <AddExpenseModal
        isOpen={isAddExpenseOpen}
        onClose={() => setIsAddExpenseOpen(false)}
        onExpenseAdded={onAddExpense}
        cases={cases}
      />
    </div>
  );
};
