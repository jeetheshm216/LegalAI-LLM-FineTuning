export const INITIAL_BILLING_SUMMARY = {
  totalBilled: 185000,
  totalReceived: 135000,
  totalOutstanding: 50000,
  totalExpenses: 24800,
  currencySymbol: "₹"
};

export const INITIAL_CLIENT_FINANCIALS = [
  {
    clientId: "cli-01",
    clientName: "Arun Kumar",
    matter: "Case 01 — Property Dispute & Title Rectification",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    totalBilled: 55000,
    paid: 40000,
    outstanding: 15000,
    progressPercentage: 73,
    lastInvoiceDate: "2026-08-20",
    lastPaymentDate: "2026-09-02",
    status: "Partially Paid"
  },
  {
    clientId: "cli-02",
    clientName: "Julian Martinez",
    matter: "Martinez v. Coastal Holdings Ltd. (Maritime Cargo)",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    totalBilled: 70000,
    paid: 55000,
    outstanding: 15000,
    progressPercentage: 78,
    lastInvoiceDate: "2026-08-28",
    lastPaymentDate: "2026-09-05",
    status: "Partially Paid"
  },
  {
    clientId: "cli-03",
    clientName: "Arthur Whitfield",
    matter: "State v. Whitfield (BNSS Bail Defense)",
    caseId: "case-02",
    caseNumber: "2024-CR-0442",
    totalBilled: 35000,
    paid: 25000,
    outstanding: 10000,
    progressPercentage: 71,
    lastInvoiceDate: "2026-08-15",
    lastPaymentDate: "2026-08-30",
    status: "Partially Paid"
  },
  {
    clientId: "cli-04",
    clientName: "Thao Nguyen (Executor)",
    matter: "Nguyen Estate Testamentary Probate",
    caseId: "case-03",
    caseNumber: "2024-CV-0998",
    totalBilled: 25000,
    paid: 15000,
    outstanding: 10000,
    progressPercentage: 60,
    lastInvoiceDate: "2026-07-22",
    lastPaymentDate: "2026-08-10",
    status: "Partially Paid"
  }
];

export const INITIAL_INVOICES = [
  {
    id: "inv-0012",
    invoiceNumber: "INV-0012",
    client: "Arun Kumar",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    caseTitle: "Property Title & Maritime Cargo Lien",
    invoiceDate: "2026-08-20",
    dueDate: "2026-09-12",
    amount: 55000,
    paidAmount: 40000,
    outstandingAmount: 15000,
    status: "Overdue", // Draft, Sent, Partially Paid, Paid, Overdue, Cancelled
    items: [
      { description: "Legal consultation & statutory strategy", quantity: 1, rate: 10000, amount: 10000 },
      { description: "Drafting Interim Injunction Notice of Motion", quantity: 1, rate: 20000, amount: 20000 },
      { description: "Senior Advocate Court appearance (Bench IV)", quantity: 2, rate: 12500, amount: 25000 }
    ],
    expensesSubtotal: 5000,
    taxPercentage: 0,
    taxAmount: 0,
    notes: "Professional fee bill for interlocutory stage proceedings."
  },
  {
    id: "inv-0013",
    invoiceNumber: "INV-0013",
    client: "Julian Martinez",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    caseTitle: "Martinez v. Coastal Holdings Ltd.",
    invoiceDate: "2026-08-28",
    dueDate: "2026-09-25",
    amount: 70000,
    paidAmount: 55000,
    outstandingAmount: 15000,
    status: "Partially Paid",
    items: [
      { description: "Maritime demurrage clause audit & review", quantity: 1, rate: 15000, amount: 15000 },
      { description: "Pleading preparation and rejoinder filing", quantity: 1, rate: 25000, amount: 25000 },
      { description: "Court appearance before Commercial Division", quantity: 2, rate: 15000, amount: 30000 }
    ],
    expensesSubtotal: 4800,
    taxPercentage: 0,
    taxAmount: 0,
    notes: "Ad-interim injunction granted. Balance due prior to final hearing."
  },
  {
    id: "inv-0014",
    invoiceNumber: "INV-0014",
    client: "Arthur Whitfield",
    caseId: "case-02",
    caseNumber: "2024-CR-0442",
    caseTitle: "State v. Whitfield (Bail Review)",
    invoiceDate: "2026-08-15",
    dueDate: "2026-09-15",
    amount: 35000,
    paidAmount: 25000,
    outstandingAmount: 10000,
    status: "Partially Paid",
    items: [
      { description: "CFSL Hash Analysis & Section 63 BSA objection draft", quantity: 1, rate: 15000, amount: 15000 },
      { description: "Sessions Court Bail argument hearing", quantity: 1, rate: 20000, amount: 20000 }
    ],
    expensesSubtotal: 3500,
    taxPercentage: 0,
    taxAmount: 0,
    notes: "Fee for forensic scrutiny and bail petition."
  },
  {
    id: "inv-0015",
    invoiceNumber: "INV-0015",
    client: "Thao Nguyen (Executor)",
    caseId: "case-03",
    caseNumber: "2024-CV-0998",
    caseTitle: "Nguyen Estate Testamentary Probate",
    invoiceDate: "2026-07-22",
    dueDate: "2026-08-22",
    amount: 25000,
    paidAmount: 15000,
    outstandingAmount: 10000,
    status: "Overdue",
    items: [
      { description: "Testamentary caveat reply & attesting witness deposition prep", quantity: 1, rate: 25000, amount: 25000 }
    ],
    expensesSubtotal: 2500,
    taxPercentage: 0,
    taxAmount: 0,
    notes: "Probate caveat stage fees."
  }
];

export const INITIAL_PAYMENTS = [
  {
    id: "pay-101",
    receiptNumber: "REC-2026-081",
    paymentDate: "2026-09-05",
    client: "Julian Martinez",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    invoiceNumber: "INV-0013",
    amount: 55000,
    paymentMethod: "Bank transfer", // Bank transfer, UPI, Cheque, Cash
    reference: "NEFT-UTR-99182301",
    status: "Confirmed",
    notes: "Interim appearance advance received."
  },
  {
    id: "pay-102",
    receiptNumber: "REC-2026-080",
    paymentDate: "2026-09-02",
    client: "Arun Kumar",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    invoiceNumber: "INV-0012",
    amount: 40000,
    paymentMethod: "UPI",
    reference: "UPI/3819283719@okaxis",
    status: "Confirmed",
    notes: "Initial retainer tranche payment."
  },
  {
    id: "pay-103",
    receiptNumber: "REC-2026-079",
    paymentDate: "2026-08-30",
    client: "Arthur Whitfield",
    caseId: "case-02",
    caseNumber: "2024-CR-0442",
    invoiceNumber: "INV-0014",
    amount: 25000,
    paymentMethod: "Bank transfer",
    reference: "RTGS-SBI-8192031",
    status: "Confirmed",
    notes: "Bail drafting advance."
  },
  {
    id: "pay-104",
    receiptNumber: "REC-2026-078",
    paymentDate: "2026-08-10",
    client: "Thao Nguyen",
    caseId: "case-03",
    caseNumber: "2024-CV-0998",
    invoiceNumber: "INV-0015",
    amount: 15000,
    paymentMethod: "Cheque",
    reference: "CHQ #441920 (HDFC Bank)",
    status: "Confirmed",
    notes: "Probate registry filing tranche."
  }
];

export const INITIAL_EXPENSES = [
  {
    id: "exp-01",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    caseTitle: "Martinez v. Coastal Holdings",
    date: "2026-09-01",
    category: "Court fees", // Court fees, Filing fees, Travel, Documentation, Printing, Professional services, Other
    description: "High Court Commercial Division motion court fee stamp",
    amount: 5000,
    notes: "Challan No. HC-COM-2026-881 attached",
    receiptAttached: true
  },
  {
    id: "exp-02",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    caseTitle: "Martinez v. Coastal Holdings",
    date: "2026-09-03",
    category: "Travel",
    description: "Chambers team travel to Port Authority maritime terminal inspection",
    amount: 3200,
    notes: "Vehicle hire & fuel bill Berth 9 inspection",
    receiptAttached: true
  },
  {
    id: "exp-03",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    caseTitle: "Martinez v. Coastal Holdings",
    date: "2026-09-04",
    category: "Printing",
    description: "High volume brief paper book printing and binding (6 copies)",
    amount: 2800,
    notes: "Commercial Court registrar set requirements",
    receiptAttached: false
  },
  {
    id: "exp-04",
    caseId: "case-02",
    caseNumber: "2024-CR-0442",
    caseTitle: "State v. Whitfield",
    date: "2026-08-25",
    category: "Filing fees",
    description: "Sessions Court urgent bail application registry stamp",
    amount: 2500,
    notes: "Official court treasury receipt #8812",
    receiptAttached: true
  },
  {
    id: "exp-05",
    caseId: "case-02",
    caseNumber: "2024-CR-0442",
    caseTitle: "State v. Whitfield",
    date: "2026-08-29",
    category: "Professional services",
    description: "Independent Digital Forensic Expert consultation on SHA256 integrity",
    amount: 7500,
    notes: "Preliminary expert opinion report on seizure protocol",
    receiptAttached: true
  },
  {
    id: "exp-06",
    caseId: "case-03",
    caseNumber: "2024-CV-0998",
    caseTitle: "Nguyen Estate Probate",
    date: "2026-07-28",
    category: "Documentation",
    description: "Certified true copies of testamentary record & codicil registration",
    amount: 3800,
    notes: "Sub-Registrar certified copy fees",
    receiptAttached: true
  }
];

export const INITIAL_REMINDERS = [
  {
    id: "rem-01",
    client: "Arun Kumar",
    invoiceNumber: "INV-0012",
    caseNumber: "2024-CV-1187",
    outstanding: 15000,
    dueDate: "2026-09-12",
    status: "Overdue by 1 day",
    isUrgent: true
  },
  {
    id: "rem-02",
    client: "Thao Nguyen",
    invoiceNumber: "INV-0015",
    caseNumber: "2024-CV-0998",
    outstanding: 10000,
    dueDate: "2026-08-22",
    status: "Overdue by 22 days",
    isUrgent: true
  },
  {
    id: "rem-03",
    client: "Julian Martinez",
    invoiceNumber: "INV-0013",
    caseNumber: "2024-CV-1187",
    outstanding: 15000,
    dueDate: "2026-09-25",
    status: "Due in 12 days",
    isUrgent: false
  }
];
