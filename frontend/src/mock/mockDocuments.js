export const INITIAL_DOCUMENTS = [
  {
    id: "doc-101",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    filename: "Interim_Injunction_Order_Bench_IV.pdf",
    category: "Court Order",
    fileType: "pdf",
    fileSize: "2.4 MB",
    uploadedDate: "2026-09-02",
    status: "ready", // ready, processing, uploading, failed
    statusLabel: "Ready for AI search",
    pages: 18,
    excerpt: "IN THE HIGH COURT OF JUDICATURE AT BOMBAY, COMMERCIAL DIVISION. Notice of Motion No. 441 of 2024. The Defendants are hereby restrained from creating third-party liens or transferring the cargo currently situated at Berth 9 pending final disposal of the dispute under Section 9 of the Arbitration Act...",
    citablePassages: [
      { page: 4, section: "Para 12", text: "The balance of convenience lies decidedly in favor of the plaintiff, considering the perishable value of the industrial catalysts." }
    ]
  },
  {
    id: "doc-102",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    filename: "Master_Charterparty_Agreement_Executed.pdf",
    category: "Contract",
    fileType: "pdf",
    fileSize: "6.8 MB",
    uploadedDate: "2026-08-28",
    status: "ready",
    statusLabel: "Ready for AI search",
    pages: 64,
    excerpt: "CHARTERPARTY AGREEMENT DATED 14TH DECEMBER 2023 BETWEEN COASTAL HOLDINGS (OWNERS) AND MARITIME CONGLOMERATE (CHARTERERS). Clause 19(b): Demurrage at the loading port shall be computed at $18,500 per running day and pro rata for any part thereof...",
    citablePassages: [
      { page: 22, section: "Clause 19(b)", text: "Demurrage computation shall pause during port authority strike declarations or force majeure delays." }
    ]
  },
  {
    id: "doc-103",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    filename: "Port_Authority_Strike_Notification.pdf",
    category: "Evidence",
    fileType: "pdf",
    fileSize: "840 KB",
    uploadedDate: "2026-09-10",
    status: "processing",
    statusLabel: "Processing",
    progress: 88,
    pages: 3,
    excerpt: "Official communique from Maritime Port Terminal Authority declaring general stevedore strike between August 14 and August 22, 2026."
  },
  {
    id: "doc-104",
    caseId: "case-02",
    caseNumber: "2024-CR-0442",
    filename: "Police_ChargeSheet_No_88_2024.pdf",
    category: "Pleadings",
    fileType: "pdf",
    fileSize: "14.2 MB",
    uploadedDate: "2026-08-15",
    status: "ready",
    statusLabel: "Ready for AI search",
    pages: 112,
    excerpt: "FINAL REPORT UNDER SECTION 193 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (BNSS). In Crime No. 104/2024 against Accused Arthur Whitfield. Summary of allegations concerning alleged misappropriation of company computing servers...",
    citablePassages: [
      { page: 12, section: "Para 18", text: "The seized digital drive was forwarded to Central Forensic Science Laboratory on 24-04-2024 with hash digest SHA256: e8b9f..." },
      { page: 34, section: "Para 41", text: "Witness statements recorded under BNSS Section 180 do not indicate physical presence at premises on the alleged date of removal." }
    ]
  },
  {
    id: "doc-105",
    caseId: "case-02",
    caseNumber: "2024-CR-0442",
    filename: "Digital_Forensic_Chain_Of_Custody.pdf",
    category: "Evidence",
    fileType: "pdf",
    fileSize: "3.1 MB",
    uploadedDate: "2026-09-08",
    status: "ready",
    statusLabel: "Ready for AI search",
    pages: 14,
    excerpt: "CHAIN OF CUSTODY REPORT AND CERTIFICATE UNDER BHARATIYA SAKSHYA ADHINIYAM (BSA) SECTION 63. Electronic record integrity verification and hash comparisons."
  },
  {
    id: "doc-106",
    caseId: "case-02",
    caseNumber: "2024-CR-0442",
    filename: "Supplementary_Deposition_Transcript.docx",
    category: "Deposition",
    fileType: "docx",
    fileSize: "1.2 MB",
    uploadedDate: "2026-09-12",
    status: "uploading",
    statusLabel: "Uploading… 64%",
    progress: 64,
    pages: 8,
    excerpt: "Deposition examination-in-chief of Lead Systems Administrator conducted before Magistrate."
  },
  {
    id: "doc-107",
    caseId: "case-03",
    caseNumber: "2024-CV-0998",
    filename: "Last_Will_and_Testament_Nguyen.pdf",
    category: "Court Order",
    fileType: "pdf",
    fileSize: "4.5 MB",
    uploadedDate: "2026-05-12",
    status: "ready",
    statusLabel: "Ready for AI search",
    pages: 22,
    excerpt: "IN THE MATTER OF THE ESTATE OF LATE HENRY NGUYEN. Testamentary document executed on October 4, 2021, witnessed by Dr. Samuel Ross and Notary Public..."
  },
  {
    id: "doc-108",
    caseId: "case-04",
    caseNumber: "2024-CC-0120",
    filename: "Arbitration_Notice_and_Statement_of_Claim.pdf",
    category: "Pleadings",
    fileType: "pdf",
    fileSize: "5.1 MB",
    uploadedDate: "2026-07-01",
    status: "failed",
    statusLabel: "Processing failed",
    pages: 42,
    excerpt: "Notice invoking international commercial arbitration pursuant to Rule 24 of Singapore International Arbitration Centre (SIAC)."
  }
];
