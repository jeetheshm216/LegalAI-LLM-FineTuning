export const INITIAL_TIMELINE = [
  {
    id: "time-01",
    caseId: "case-01",
    timestamp: "2026-09-10 16:45",
    relativeTime: "3 days ago",
    eventType: "ai_analysis", // hearing, document, order, meeting, note, ai_analysis
    title: "AI Statutory & Precedent Risk Synthesis",
    author: "Legal AI Engine",
    isAI: true,
    summary: "Identified conflict between charterparty demurrage clause 19(b) and statutory port force majeure notification under Maritime Admiralty Code.",
    details: "Automated analysis cross-referenced the newly uploaded Port Authority Strike Notification against clause 19(b) of the Charterparty Agreement. The analysis indicates strong grounds under Section 9 to obtain protection against cargo auction by terminal operators.",
    relatedDocument: "Port_Authority_Strike_Notification.pdf"
  },
  {
    id: "time-02",
    caseId: "case-01",
    timestamp: "2026-09-08 14:00",
    relativeTime: "5 days ago",
    eventType: "meeting",
    title: "Client Conference with Julian Martinez",
    author: "Adv. Elena Vance",
    isAI: false,
    summary: "Strategy meeting regarding emergency injunction petition before Commercial Bench IV.",
    details: "Client confirmed all bunker supply bills are cleared. Instructed counsel to press for appointment of Court Receiver if opposing party refuses cargo discharge.",
    relatedDocument: null
  },
  {
    id: "time-03",
    caseId: "case-01",
    timestamp: "2026-09-02 11:30",
    relativeTime: "11 days ago",
    eventType: "order",
    title: "Interim Ad-Interim Injunction Order Passed",
    author: "Registrar, High Court Bench IV",
    isAI: false,
    summary: "Bench granted ad-interim status quo restraining sale or transfer of 14,000 MT catalytic cargo.",
    details: "Presiding Judge signed order. Notice issued to Coastal Holdings returnable on September 17, 2026 at 10:30 AM.",
    relatedDocument: "Interim_Injunction_Order_Bench_IV.pdf"
  },
  {
    id: "time-04",
    caseId: "case-01",
    timestamp: "2026-08-28 09:15",
    relativeTime: "16 days ago",
    eventType: "document",
    title: "Document Ingested: Master Charterparty Agreement",
    author: "Chambers Paralegal",
    isAI: false,
    summary: "64-page executed agreement successfully indexed for vector search.",
    details: "Full contractual provisions OCR-validated and parsed into section-wise embeddings.",
    relatedDocument: "Master_Charterparty_Agreement_Executed.pdf"
  },
  {
    id: "time-05",
    caseId: "case-01",
    timestamp: "2024-03-14 10:00",
    relativeTime: "6 months ago",
    eventType: "created",
    title: "Matter Instituted & File Opened",
    author: "Adv. Elena Vance",
    isAI: false,
    summary: "Case #2024-CV-1187 created in chambers registry.",
    details: "Retainer agreement signed with Julian Martinez. Assigned high-priority commercial track.",
    relatedDocument: null
  },
  {
    id: "time-06",
    caseId: "case-02",
    timestamp: "2026-09-11 10:30",
    relativeTime: "2 days ago",
    eventType: "hearing",
    title: "Bail Scrutiny Hearing Conducted",
    author: "Sessions Court Division I",
    isAI: false,
    summary: "Arguments concluded on electronic seizure admissibility under BSA Section 63.",
    details: "Court reserved orders on interim bail application pending filing of hash verification certificate by investigating officer.",
    relatedDocument: "Digital_Forensic_Chain_Of_Custody.pdf"
  }
];
