import React, { useState, useEffect } from 'react';
import { Header } from './components/common/Header';
import { LoginScreen } from './components/auth/LoginModal';
import { DashboardView } from './components/dashboard/DashboardView';
import { CaseListView } from './components/cases/CaseListView';
import { CaseDetailView } from './components/case-detail/CaseDetailView';
import { CalendarView } from './components/calendar/CalendarView';
import { AIAssistantView } from './components/ai/AIAssistantView';
import { SettingsView } from './components/settings/SettingsView';
import { AddCaseModal } from './components/cases/AddCaseModal';

// Billing & Finance Components
import { BillingView } from './components/billing/BillingView';
import { CreateInvoiceModal } from './components/billing/CreateInvoiceModal';
import { RecordPaymentModal } from './components/billing/RecordPaymentModal';
import { AddExpenseModal } from './components/billing/AddExpenseModal';

// Legal Drafting Studio Components
import { DraftingDashboard } from './components/drafting/DraftingDashboard';
import { LegalDocumentEditor } from './components/drafting/LegalDocumentEditor';
import { NewDraftModal } from './components/drafting/NewDraftModal';

// Initial Mock Data
import { INITIAL_CASES } from './mock/mockCases';
import { INITIAL_DOCUMENTS } from './mock/mockDocuments';
import { INITIAL_TIMELINE } from './mock/mockTimeline';
import { INITIAL_EVENTS } from './mock/mockCalendar';
import { INITIAL_USER } from './mock/mockUser';
import { 
  INITIAL_BILLING_SUMMARY, 
  INITIAL_CLIENT_FINANCIALS, 
  INITIAL_INVOICES, 
  INITIAL_PAYMENTS, 
  INITIAL_EXPENSES, 
  INITIAL_REMINDERS 
} from './mock/mockBilling';
import { INITIAL_DRAFTS } from './mock/mockDrafting';

// Services
import { caseService } from './services/caseService';
import { documentService } from './services/documentService';
import { timelineService } from './services/timelineService';
import { calendarService } from './services/calendarService';
import { billingService } from './services/billingService';
import { draftingService } from './services/draftingService';

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [activeView, setActiveView] = useState('dashboard'); // 'dashboard' | 'cases' | 'case-detail' | 'calendar' | 'ai' | 'drafting' | 'editor' | 'billing' | 'settings'
  const [themeMode, setThemeMode] = useState('light'); // 'light' | 'dark' | 'system'
  
  // App-level data state
  const [cases, setCases] = useState(INITIAL_CASES);
  const [documents, setDocuments] = useState(INITIAL_DOCUMENTS);
  const [timelineEvents, setTimelineEvents] = useState(INITIAL_TIMELINE);
  const [calendarEvents, setCalendarEvents] = useState(INITIAL_EVENTS);
  const [currentUser, setCurrentUser] = useState(INITIAL_USER);

  // Billing state
  const [billingSummary, setBillingSummary] = useState(INITIAL_BILLING_SUMMARY);
  const [clientFinancials, setClientFinancials] = useState(INITIAL_CLIENT_FINANCIALS);
  const [invoices, setInvoices] = useState(INITIAL_INVOICES);
  const [payments, setPayments] = useState(INITIAL_PAYMENTS);
  const [expenses, setExpenses] = useState(INITIAL_EXPENSES);
  const [reminders, setReminders] = useState(INITIAL_REMINDERS);

  // Drafting state
  const [drafts, setDrafts] = useState(INITIAL_DRAFTS);
  const [currentEditingDraft, setCurrentEditingDraft] = useState(INITIAL_DRAFTS[0]);

  // Modal states
  const [selectedCase, setSelectedCase] = useState(INITIAL_CASES[0]);
  const [isAddCaseOpen, setIsAddCaseOpen] = useState(false);
  
  // Case-level modal anchors
  const [isNewDraftOpen, setIsNewDraftOpen] = useState(false);
  const [draftTargetCase, setDraftTargetCase] = useState(null);
  const [isCreateInvoiceOpen, setIsCreateInvoiceOpen] = useState(false);
  const [isRecordPaymentOpen, setIsRecordPaymentOpen] = useState(false);
  const [isAddExpenseOpen, setIsAddExpenseOpen] = useState(false);
  const [billingTargetCase, setBillingTargetCase] = useState(null);

  // Apply theme to root document per §17
  useEffect(() => {
    let effectiveTheme = themeMode;
    if (themeMode === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      effectiveTheme = prefersDark ? 'dark' : 'light';
    }
    document.documentElement.setAttribute('data-theme', effectiveTheme);
  }, [themeMode]);

  const handleSelectCase = (caseItem) => {
    setSelectedCase(caseItem);
    setActiveView('case-detail');
  };

  const handleCaseAdded = async (newCaseData) => {
    const created = await caseService.addCase(newCaseData);
    setCases(prev => [created, ...prev]);
    setSelectedCase(created);
    setActiveView('case-detail');
  };

  const handleUploadDocument = async ({ caseId, caseNumber, file, category }) => {
    const uploaded = await documentService.uploadDocument({ caseId, caseNumber, file, category });
    setDocuments(prev => [uploaded, ...prev]);

    // Simulate completion after 3 seconds
    setTimeout(() => {
      setDocuments(prev => prev.map(d => {
        if (d.id === uploaded.id) {
          return {
            ...d,
            status: 'ready',
            statusLabel: 'Ready for AI search'
          };
        }
        return d;
      }));
    }, 3000);
  };

  const handleAddTimelineEvent = async (eventData) => {
    const newEvent = await timelineService.addTimelineEvent(eventData);
    setTimelineEvents(prev => [newEvent, ...prev]);
  };

  const handleAddCalendarEvent = async (eventData) => {
    const newEvt = await calendarService.addEvent(eventData);
    setCalendarEvents(prev => [...prev, newEvt]);
  };

  const handleStartAIChat = (promptText) => {
    setActiveView('ai');
  };

  // --- Drafting Handlers ---
  const handleOpenDraft = (draft) => {
    setCurrentEditingDraft(draft);
    setActiveView('editor');
  };

  const handleDraftCreated = async (draftData) => {
    const created = await draftingService.createDraft(draftData);
    setDrafts(prev => [created, ...prev]);
    setIsNewDraftOpen(false);
    setCurrentEditingDraft(created);
    setActiveView('editor');
  };

  const handleSaveDraft = async ({ id, title, content, versions }) => {
    const saved = await draftingService.saveDraft(id, { title, content, versions });
    setDrafts(prev => prev.map(d => d.id === id ? saved : d));
    setCurrentEditingDraft(saved);
  };

  const handleCaseNewDraft = (caseItem) => {
    setDraftTargetCase(caseItem);
    setIsNewDraftOpen(true);
  };

  // --- Billing Handlers ---
  const handleInvoiceCreated = async (invoiceData) => {
    const created = await billingService.createInvoice(invoiceData);
    setInvoices(prev => [created, ...prev]);
    setIsCreateInvoiceOpen(false);
    
    // Update summary
    setBillingSummary(prev => ({
      ...prev,
      totalBilled: prev.totalBilled + (created.amount || 0),
      totalOutstanding: prev.totalOutstanding + (created.outstandingAmount || created.amount || 0)
    }));
  };

  const handlePaymentRecorded = async (paymentData) => {
    const recorded = await billingService.recordPayment(paymentData);
    setPayments(prev => [recorded, ...prev]);
    setIsRecordPaymentOpen(false);

    // Update invoices
    setInvoices(prev => prev.map(inv => {
      if (inv.invoiceNumber === paymentData.invoiceNumber) {
        const remaining = Math.max(0, inv.outstandingAmount - paymentData.amount);
        return {
          ...inv,
          paidAmount: (inv.paidAmount || 0) + paymentData.amount,
          outstandingAmount: remaining,
          status: remaining === 0 ? 'PAID' : 'PARTIAL'
        };
      }
      return inv;
    }));

    // Update summary
    setBillingSummary(prev => ({
      ...prev,
      totalReceived: prev.totalReceived + (paymentData.amount || 0),
      totalOutstanding: Math.max(0, prev.totalOutstanding - (paymentData.amount || 0))
    }));
  };

  const handleExpenseAdded = async (expenseData) => {
    const created = await billingService.addExpense(expenseData);
    setExpenses(prev => [created, ...prev]);
    setIsAddExpenseOpen(false);

    // Update summary
    setBillingSummary(prev => ({
      ...prev,
      totalExpenses: prev.totalExpenses + (created.amount || 0)
    }));
  };

  const handleCaseCreateInvoice = (caseItem) => {
    setBillingTargetCase(caseItem);
    setIsCreateInvoiceOpen(true);
  };

  const handleCaseRecordPayment = (caseItem) => {
    setBillingTargetCase(caseItem);
    setIsRecordPaymentOpen(true);
  };

  const handleCaseAddExpense = (caseItem) => {
    setBillingTargetCase(caseItem);
    setIsAddExpenseOpen(true);
  };

  if (!isAuthenticated) {
    return <LoginScreen onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  // Selected case finances for CaseDetailView
  const selectedCaseFinances = {
    invoices: invoices.filter(i => i.caseId === selectedCase?.id || i.caseNumber === selectedCase?.caseNumber),
    expenses: expenses.filter(e => e.caseId === selectedCase?.id || e.caseNumber === selectedCase?.caseNumber)
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-bg-canvas)', display: 'flex', flexDirection: 'column' }}>
      {/* 1. Global Header (§8: 60px fixed header, consistent across all views) */}
      <Header
        activeView={activeView}
        onNavigate={(view) => setActiveView(view)}
        themeMode={themeMode}
        onThemeChange={(m) => setThemeMode(m)}
        currentUser={currentUser}
        onLogout={() => setIsAuthenticated(false)}
      />

      {/* 2. Main Page View Content */}
      <main style={{ flex: 1 }}>
        {activeView === 'dashboard' && (
          <DashboardView
            cases={cases}
            documents={documents}
            events={calendarEvents}
            onNavigate={(v) => setActiveView(v)}
            onSelectCase={handleSelectCase}
            onOpenAddCase={() => setIsAddCaseOpen(true)}
            onStartAIChat={handleStartAIChat}
          />
        )}

        {activeView === 'cases' && (
          <CaseListView
            cases={cases}
            onSelectCase={handleSelectCase}
            onOpenAddCase={() => setIsAddCaseOpen(true)}
          />
        )}

        {activeView === 'case-detail' && selectedCase && (
          <CaseDetailView
            currentCase={selectedCase}
            documents={documents}
            timelineEvents={timelineEvents}
            drafts={drafts}
            caseFinances={selectedCaseFinances}
            onBack={() => setActiveView('cases')}
            onUploadDocument={handleUploadDocument}
            onAddTimelineEvent={handleAddTimelineEvent}
            onLaunchCaseAI={() => setActiveView('ai')}
            onOpenNewDraft={handleCaseNewDraft}
            onSelectDraft={handleOpenDraft}
            onOpenCreateInvoice={handleCaseCreateInvoice}
            onOpenRecordPayment={handleCaseRecordPayment}
            onOpenAddExpense={handleCaseAddExpense}
          />
        )}

        {activeView === 'calendar' && (
          <CalendarView
            events={calendarEvents}
            onAddEvent={handleAddCalendarEvent}
          />
        )}

        {activeView === 'ai' && (
          <div
            className="container"
            style={{
              padding: 'var(--space-md)',
              height: 'calc(100vh - var(--header-height))',
              display: 'flex',
              flexDirection: 'column',
              boxSizing: 'border-box'
            }}
          >
            <AIAssistantView
              initialMode="GENERAL"
              allCases={cases}
            />
          </div>
        )}

        {/* 3. Legal Drafting Studio */}
        {activeView === 'drafting' && (
          <DraftingDashboard
            drafts={drafts}
            onOpenNewDraft={() => {
              setDraftTargetCase(null);
              setIsNewDraftOpen(true);
            }}
            onSelectDraft={handleOpenDraft}
          />
        )}

        {activeView === 'editor' && currentEditingDraft && (
          <LegalDocumentEditor
            draft={currentEditingDraft}
            onBack={() => setActiveView('drafting')}
            onSave={handleSaveDraft}
          />
        )}

        {/* 4. Billing & Finance */}
        {activeView === 'billing' && (
          <BillingView
            summary={billingSummary}
            clientFinancials={clientFinancials}
            invoices={invoices}
            payments={payments}
            expenses={expenses}
            reminders={reminders}
            cases={cases}
            onCreateInvoice={handleInvoiceCreated}
            onRecordPayment={handlePaymentRecorded}
            onAddExpense={handleExpenseAdded}
          />
        )}

        {activeView === 'settings' && (
          <SettingsView
            currentUser={currentUser}
            themeMode={themeMode}
            onThemeChange={(m) => setThemeMode(m)}
            onLogout={() => setIsAuthenticated(false)}
            onUpdateUserSettings={(newSet) => setCurrentUser(prev => ({ ...prev, ...newSet }))}
          />
        )}
      </main>

      {/* Global & Case Modal: Add Case Intake */}
      <AddCaseModal
        isOpen={isAddCaseOpen}
        onClose={() => setIsAddCaseOpen(false)}
        onCaseAdded={handleCaseAdded}
      />

      {/* Case-anchored or Global: New Draft Wizard */}
      <NewDraftModal
        isOpen={isNewDraftOpen}
        onClose={() => setIsNewDraftOpen(false)}
        onDraftCreated={handleDraftCreated}
        cases={cases}
      />

      {/* Case-anchored: Create Invoice */}
      <CreateInvoiceModal
        isOpen={isCreateInvoiceOpen}
        onClose={() => setIsCreateInvoiceOpen(false)}
        onInvoiceCreated={handleInvoiceCreated}
        cases={cases}
      />

      {/* Case-anchored: Record Payment */}
      <RecordPaymentModal
        isOpen={isRecordPaymentOpen}
        onClose={() => setIsRecordPaymentOpen(false)}
        onPaymentRecorded={handlePaymentRecorded}
        invoices={invoices}
      />

      {/* Case-anchored: Add Expense */}
      <AddExpenseModal
        isOpen={isAddExpenseOpen}
        onClose={() => setIsAddExpenseOpen(false)}
        onExpenseAdded={handleExpenseAdded}
        cases={cases}
      />
    </div>
  );
}
