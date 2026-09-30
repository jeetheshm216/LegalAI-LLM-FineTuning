import React, { useState, useEffect } from 'react';
import { Header } from './components/common/Header';
import { LoginScreen } from './components/auth/LoginModal';
import { DashboardView } from './components/dashboard/DashboardView';
import { CaseListView } from './components/cases/CaseListView';
import { CaseDetailView } from './components/case-detail/CaseDetailView';
import { CalendarView } from './components/calendar/CalendarView';
import { AIAssistantView } from './components/ai/AIAssistantView';
import { CourtroomSimulationView } from './components/courtroom/CourtroomSimulationView';
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
import { authService } from './services/authService';
import { AuthState } from './types/authTypes';
import { AlertCircle } from 'lucide-react';
import { CompleteAdvocateVerificationModal } from './components/auth/CompleteAdvocateVerificationModal';

export function App() {
  const [authSnapshot, setAuthSnapshot] = useState(authService.getSnapshot());
  const [activeView, setActiveView] = useState('dashboard'); // 'dashboard' | 'cases' | 'case-detail' | 'calendar' | 'ai' | 'drafting' | 'editor' | 'billing' | 'settings'
  const [themeMode, setThemeMode] = useState('light'); // 'light' | 'dark' | 'system'
  const [isCompleteVerificationOpen, setIsCompleteVerificationOpen] = useState(false);

  useEffect(() => {
    const unsubscribe = authService.subscribe((snapshot) => {
      setAuthSnapshot(snapshot);
      if (snapshot.profile) {
        setCurrentUser(snapshot.profile);
      }
    });
    return () => unsubscribe();
  }, []);
  
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
    if (promptText && typeof promptText === 'string') {
      sessionStorage.setItem('courtroom_ai_prompt', promptText);
    }
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

  if (authSnapshot.authState === AuthState.INITIALIZING) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--color-bg-canvas)' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px' }}>
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 3H15L20 8V21H4V3Z" stroke="var(--color-ink-700)" strokeWidth="2" strokeLinejoin="round" />
            <path d="M15 3V8H20" stroke="var(--color-accent-500)" strokeWidth="2" strokeLinejoin="round" />
          </svg>
          <span style={{ fontFamily: 'var(--font-serif)', fontSize: '22px', fontWeight: 600, color: 'var(--color-ink-700)' }}>
            Legal AI
          </span>
        </div>
        <p style={{ marginTop: '12px', fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)' }}>
          Establishing secure chambers session...
        </p>
      </div>
    );
  }

  if (authSnapshot.authState === AuthState.UNAUTHENTICATED || authSnapshot.authState === AuthState.TWO_FACTOR_REQUIRED) {
    return <LoginScreen onLoginSuccess={() => {}} />;
  }

  if (
    authSnapshot.authState === AuthState.PROFESSIONAL_VERIFICATION_PENDING ||
    authSnapshot.authState === AuthState.PROFESSIONAL_VERIFICATION_REVIEW ||
    authSnapshot.authState === AuthState.PROFESSIONAL_VERIFICATION_FAILED
  ) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--color-bg-canvas)', padding: 'var(--space-md)' }}>
        <div style={{ width: '100%', maxWidth: '480px', backgroundColor: 'var(--color-bg-surface)', border: '1px solid var(--color-border-subtle)', borderRadius: 'var(--radius-xl)', padding: 'var(--space-xl)', boxShadow: 'var(--elevation-2)', textAlign: 'center' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: '50%', backgroundColor: 'var(--color-warning-wash)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--space-md)' }}>
            <AlertCircle size={28} color="var(--color-warning-text)" />
          </div>
          <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-h2)', color: 'var(--color-ink-700)', marginBottom: 'var(--space-xs)' }}>
            Professional Verification Required
          </h2>
          <p style={{ fontSize: 'var(--text-caption)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-lg)' }}>
            LegalAI is restricted to verified legal practitioners. Your identity has been authenticated, but your advocate credentials are currently{' '}
            <strong>{authSnapshot.profile?.verification_status || 'PENDING'}</strong>.
          </p>

          <div style={{ backgroundColor: 'var(--color-bg-surface-sunken)', borderRadius: 'var(--radius-md)', padding: 'var(--space-sm) var(--space-md)', textAlign: 'left', marginBottom: 'var(--space-lg)', fontSize: 'var(--text-caption)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>Account Email:</span>
              <span style={{ fontWeight: 500 }}>{authSnapshot.currentUser?.email || authSnapshot.profile?.email}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>State Bar Roll:</span>
              <span style={{ fontWeight: 500 }}>{authSnapshot.profile?.state_bar_council || 'Pending submission'}</span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 'var(--space-sm)', justifyContent: 'center' }}>
            <button
              onClick={() => setIsCompleteVerificationOpen(true)}
              style={{
                padding: '10px 18px',
                borderRadius: 'var(--radius-md)',
                border: 'none',
                backgroundColor: 'var(--color-accent-500)',
                color: '#FFFFFF',
                cursor: 'pointer',
                fontSize: 'var(--text-caption)',
                fontWeight: 600
              }}
            >
              Verify Advocate Credentials →
            </button>
            <button
              onClick={() => authService.logout()}
              style={{
                padding: '10px 16px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border-default)',
                backgroundColor: 'transparent',
                color: 'var(--color-text-secondary)',
                cursor: 'pointer',
                fontSize: 'var(--text-caption)',
                fontWeight: 500
              }}
            >
              Sign Out
            </button>
          </div>
        </div>

        {isCompleteVerificationOpen && (
          <CompleteAdvocateVerificationModal
            currentUser={authSnapshot.currentUser}
            profile={authSnapshot.profile}
            onClose={() => setIsCompleteVerificationOpen(false)}
            onComplete={() => setIsCompleteVerificationOpen(false)}
          />
        )}
      </div>
    );
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
        onLogout={() => authService.logout()}
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
            allCases={cases}
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
            style={{
              width: '100%',
              height: 'calc(100vh - var(--header-height, 60px))',
              display: 'flex',
              flexDirection: 'column',
              boxSizing: 'border-box',
              padding: 0,
              margin: 0,
              overflow: 'hidden'
            }}
          >
            <AIAssistantView
              initialMode="GENERAL"
              lockedCase={null}
              allCases={cases}
            />
          </div>
        )}

        {activeView === 'courtroom' && (
          <CourtroomSimulationView 
            globalTheme={themeMode}
            onNavigate={(v) => setActiveView(v)}
            onStartAIChat={handleStartAIChat}
          />
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
            onLogout={() => authService.logout()}
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
        targetCase={draftTargetCase}
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
