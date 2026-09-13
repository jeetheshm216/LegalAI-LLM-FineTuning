import { 
  INITIAL_BILLING_SUMMARY, 
  INITIAL_CLIENT_FINANCIALS, 
  INITIAL_INVOICES, 
  INITIAL_PAYMENTS, 
  INITIAL_EXPENSES, 
  INITIAL_REMINDERS 
} from '../mock/mockBilling';

let billingSummary = { ...INITIAL_BILLING_SUMMARY };
let clientFinancials = [...INITIAL_CLIENT_FINANCIALS];
let invoices = [...INITIAL_INVOICES];
let payments = [...INITIAL_PAYMENTS];
let expenses = [...INITIAL_EXPENSES];
let reminders = [...INITIAL_REMINDERS];

export const billingService = {
  getSummary: async () => {
    return { ...billingSummary };
  },

  getClientFinancials: async () => {
    return [...clientFinancials];
  },

  getCaseFinancials: async (caseId) => {
    const caseInvoices = invoices.filter(inv => inv.caseId === caseId);
    const casePayments = payments.filter(pay => pay.caseId === caseId);
    const caseExpenses = expenses.filter(exp => exp.caseId === caseId);

    const totalBilled = caseInvoices.reduce((sum, i) => sum + (i.amount || 0), 0);
    const totalPaid = caseInvoices.reduce((sum, i) => sum + (i.paidAmount || 0), 0);
    const outstanding = Math.max(0, totalBilled - totalPaid);
    const totalExpenseAmount = caseExpenses.reduce((sum, e) => sum + (e.amount || 0), 0);

    return {
      totalBilled: totalBilled || 50000,
      paid: totalPaid || 35000,
      outstanding: outstanding || 15000,
      expensesTotal: totalExpenseAmount || 11000,
      invoices: caseInvoices,
      payments: casePayments,
      expenses: caseExpenses,
      progressPercentage: totalBilled > 0 ? Math.round((totalPaid / totalBilled) * 100) : 70
    };
  },

  getInvoices: async () => {
    return [...invoices];
  },

  createInvoice: async (invoiceData) => {
    const items = invoiceData.items || [];
    const subtotal = items.reduce((sum, item) => sum + (Number(item.amount) || 0), 0);
    const expensesSubtotal = Number(invoiceData.expensesSubtotal) || 0;
    const taxRate = Number(invoiceData.taxPercentage) || 0;
    const taxAmount = Math.round((subtotal + expensesSubtotal) * (taxRate / 100));
    const total = subtotal + expensesSubtotal + taxAmount;
    const paid = Number(invoiceData.paidAmount) || 0;
    const outstanding = Math.max(0, total - paid);

    const newInvoice = {
      id: `inv-${Date.now()}`,
      invoiceNumber: invoiceData.invoiceNumber || `INV-${Math.floor(1000 + Math.random() * 9000)}`,
      client: invoiceData.client,
      caseId: invoiceData.caseId || "case-01",
      caseNumber: invoiceData.caseNumber || "2024-CV-1187",
      caseTitle: invoiceData.caseTitle || "Legal Matter",
      invoiceDate: invoiceData.invoiceDate || new Date().toISOString().split('T')[0],
      dueDate: invoiceData.dueDate || new Date(Date.now() + 30*86400000).toISOString().split('T')[0],
      amount: total,
      paidAmount: paid,
      outstandingAmount: outstanding,
      status: paid >= total ? "Paid" : paid > 0 ? "Partially Paid" : "Sent",
      items,
      expensesSubtotal,
      taxPercentage: taxRate,
      taxAmount,
      notes: invoiceData.notes || ""
    };

    invoices = [newInvoice, ...invoices];
    billingSummary.totalBilled += total;
    billingSummary.totalReceived += paid;
    billingSummary.totalOutstanding += outstanding;

    return newInvoice;
  },

  getPayments: async () => {
    return [...payments];
  },

  recordPayment: async (paymentData) => {
    const newPayment = {
      id: `pay-${Date.now()}`,
      receiptNumber: `REC-${new Date().getFullYear()}-${Math.floor(100 + Math.random() * 900)}`,
      paymentDate: paymentData.paymentDate || new Date().toISOString().split('T')[0],
      client: paymentData.client,
      caseId: paymentData.caseId || "case-01",
      caseNumber: paymentData.caseNumber || "2024-CV-1187",
      invoiceNumber: paymentData.invoiceNumber || "INV-0012",
      amount: Number(paymentData.amount) || 0,
      paymentMethod: paymentData.paymentMethod || "Bank transfer",
      reference: paymentData.reference || `REF-${Math.floor(100000 + Math.random() * 900000)}`,
      status: "Confirmed",
      notes: paymentData.notes || ""
    };

    payments = [newPayment, ...payments];
    billingSummary.totalReceived += newPayment.amount;
    billingSummary.totalOutstanding = Math.max(0, billingSummary.totalOutstanding - newPayment.amount);

    // Update invoice if matched
    invoices = invoices.map(inv => {
      if (inv.invoiceNumber === newPayment.invoiceNumber) {
        const newPaid = inv.paidAmount + newPayment.amount;
        const newOutstanding = Math.max(0, inv.amount - newPaid);
        return {
          ...inv,
          paidAmount: newPaid,
          outstandingAmount: newOutstanding,
          status: newPaid >= inv.amount ? "Paid" : "Partially Paid"
        };
      }
      return inv;
    });

    return newPayment;
  },

  getExpenses: async () => {
    return [...expenses];
  },

  addExpense: async (expenseData) => {
    const newExpense = {
      id: `exp-${Date.now()}`,
      caseId: expenseData.caseId || "case-01",
      caseNumber: expenseData.caseNumber || "2024-CV-1187",
      caseTitle: expenseData.caseTitle || "Commercial Matter",
      date: expenseData.date || new Date().toISOString().split('T')[0],
      category: expenseData.category || "Court fees",
      description: expenseData.description,
      amount: Number(expenseData.amount) || 0,
      notes: expenseData.notes || "",
      receiptAttached: !!expenseData.receiptAttached
    };

    expenses = [newExpense, ...expenses];
    billingSummary.totalExpenses += newExpense.amount;
    return newExpense;
  },

  getReminders: async () => {
    return [...reminders];
  },

  sendReminderMock: async (reminderId) => {
    await new Promise(r => setTimeout(r, 400));
    return { success: true, message: "Payment reminder notification dispatched." };
  }
};
