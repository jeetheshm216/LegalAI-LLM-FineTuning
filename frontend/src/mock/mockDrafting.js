export const DRAFT_CATEGORIES = [
  "Legal Notice",
  "Petition",
  "Application",
  "Affidavit",
  "Reply",
  "Written Statement",
  "Arguments",
  "Contract",
  "Client Letter",
  "Email",
  "Case Summary",
  "Hearing Notes"
];

export const INITIAL_DRAFTS = [
  {
    id: "draft-01",
    title: "Legal Notice for Freight Demurrage Breach — Martinez v. Coastal",
    documentType: "Legal Notice",
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    caseTitle: "Martinez v. Coastal Holdings Ltd.",
    status: "In Review", // Draft, In Review, Final, Archived
    version: "Version 3",
    wordCount: 542,
    createdAt: "2026-09-08 14:20",
    lastModified: "Today, 03:45 PM",
    author: "Adv. Elena Vance",
    content: `LEGAL NOTICE UNDER SECTION 11 OF THE MARITIME ARBITRATION RULES

To,
Coastal Holdings Limited,
Through its Managing Director & Port Agents,
Marine Terminal Plaza, Berth 9,
Mumbai - 400001.

SUBJECT: DEMAND FOR IMMEDIATE RELEASE OF 14,000 MT CATALYTIC CARGO AND CEASE-AND-DESIST AGAINST UNLAWFUL FREIGHT LIEN

Dear Sirs,

Under instructions from and on behalf of our client, Mr. Julian Martinez, Charterer under the Master Charterparty Agreement dated 14th December 2023, we hereby serve upon you this formal Legal Notice:

1. That pursuant to Clause 19(b) of the Charterparty Agreement, demurrage accrual is expressly suspended during declared port authority stevedore strikes or force majeure contingencies.

2. That the Maritime Port Terminal Authority issued an official directive on August 14, 2026 declaring a general stevedore cessation. Consequently, your demand for $184,000 in accumulated demurrage is wholly devoid of contractual justification.

3. That your refusal to permit cargo discharge and your threat to auction the industrial catalysts violates the Ad-Interim Injunction granted by Commercial Bench IV on September 2, 2026.

WE THEREFORE CALL UPON YOU to immediately cease and desist from asserting any maritime possessory lien on the cargo and to grant unconditional gate passes within forty-eight (48) hours of receipt of this notice, failing which our client shall institute contempt proceedings and initiate international arbitration at your sole risk, cost, and consequence.

Yours faithfully,

Elena Vance
Advocate for the Charterer
Chambers of Vance & Associates`,
    versions: [
      {
        id: "v-3",
        versionNumber: "Version 3",
        timestamp: "Today, 03:45 PM",
        author: "Adv. Elena Vance",
        summary: "Integrated ad-interim injunction order reference from Bench IV into paragraph 3."
      },
      {
        id: "v-2",
        versionNumber: "Version 2",
        timestamp: "Yesterday, 05:12 PM",
        author: "Adv. Elena Vance",
        summary: "Refined force majeure clause 19(b) statutory wording and tightened 48-hour deadline."
      },
      {
        id: "v-1",
        versionNumber: "Version 1",
        timestamp: "2026-09-08 14:20",
        author: "Chambers Paralegal",
        summary: "Initial draft framework generated from case documents."
      }
    ]
  },
  {
    id: "draft-02",
    title: "Interim Bail Application under BNSS Section 479 — State v. Whitfield",
    documentType: "Application",
    caseId: "case-02",
    caseNumber: "2024-CR-0442",
    caseTitle: "State v. Whitfield",
    status: "Draft",
    version: "Version 2",
    wordCount: 688,
    createdAt: "2026-09-11 11:30",
    lastModified: "Today, 11:15 AM",
    author: "Adv. Elena Vance",
    content: `IN THE COURT OF SESSIONS JUDGE, FIRST DIVISION

CRIMINAL MISCELLANEOUS APPLICATION NO. _____ OF 2026
IN CRIME NO. 104 OF 2024 (PS ECONOMIC OFFENCES)

IN THE MATTER OF:
Arthur Whitfield ... Applicant / Accused

VERSUS
The State of Public Prosecution ... Respondent

APPLICATION FOR REGULAR BAIL UNDER SECTION 479 READ WITH SECTION 480 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (BNSS)

MOST RESPECTFULLY SHOWETH:

1. That the Applicant has been falsely implicated in the aforementioned Crime No. 104/2024 registered under Section 316 of the Bharatiya Nyaya Sanhita, 2023.

2. That the Applicant is a first-time offender with no prior criminal antecedents, and has deep commercial and familial roots within this jurisdiction, thereby dispelling any legitimate apprehension of flight risk.

3. That the seizure of electronic servers relied upon in the ChargeSheet was conducted in flagrant violation of the mandatory certificate and hash-integrity requirements codified under Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 (BSA). Specifically, no contemporaneous hash value was sealed at the locus in quo.

4. That the Applicant has been in judicial custody since 45 days, and the investigation qua the Applicant is substantially complete.

PRAYER:
Wherefore, in the light of the facts and circumstances stated above, it is most respectfully prayed that this Hon'ble Court may be pleased to release the Applicant on regular bail upon such terms as this Court may deem fit.

Filed by:
Elena Vance, Advocate
Counsel for the Applicant`,
    versions: [
      {
        id: "v-2",
        versionNumber: "Version 2",
        timestamp: "Today, 11:15 AM",
        author: "Adv. Elena Vance",
        summary: "Added ground regarding lack of contemporaneous SHA-256 hash sealing under BSA Section 63."
      },
      {
        id: "v-1",
        versionNumber: "Version 1",
        timestamp: "2026-09-11 11:30",
        author: "Adv. Elena Vance",
        summary: "Initial bail petition structure."
      }
    ]
  },
  {
    id: "draft-03",
    title: "Client Opinion Letter regarding Testamentary Caveat — Nguyen Estate",
    documentType: "Client Letter",
    caseId: "case-03",
    caseNumber: "2024-CV-0998",
    caseTitle: "Nguyen Estate Testamentary Probate",
    status: "Final",
    version: "Version 1",
    wordCount: 420,
    createdAt: "2026-08-25 16:00",
    lastModified: "2026-08-25 16:30",
    author: "Adv. Elena Vance",
    content: `CONFIDENTIAL ATTORNEY-CLIENT PRIVILEGED COMMUNICATION

To:
Ms. Thao Nguyen,
Executor of the Estate of Late Henry Nguyen.

SUBJECT: LEGAL OPINION ON CAVEAT LODGED BY CONTESTING BENEFICIARIES

Dear Ms. Nguyen,

Following our scrutiny of the caveat filed before the High Court Testamentary Division, we provide below our legal opinion on procedural defense:

1. Statutory 8-Day Rule: Under the Testamentary Rules, an opposing party lodging a caveat must file their substantive affidavit of objections within eight (8) days. Failure to lodge such affidavit will entitle us to move the Court for summary discharge of the caveat.

2. Testamentary Capacity Evidence: The attesting physician, Dr. Samuel Ross, was present at the execution of the codicil. His contemporaneous medical fitness certificate creates a strong statutory presumption in favor of the probate.

Next Steps: We are preparing the rejoinder affidavit and will file for an expedited hearing on the caveats next month.

Yours sincerely,
Elena Vance, Advocate`,
    versions: [
      {
        id: "v-1",
        versionNumber: "Version 1",
        timestamp: "2026-08-25 16:00",
        author: "Adv. Elena Vance",
        summary: "Final issued client legal advice letter."
      }
    ]
  }
];

export const MOCK_AI_DRAFTING_TEMPLATES = {
  "Legal Notice": `LEGAL NOTICE UNDER STATUTORY PROVISIONS

To: [Opposing Party / Company Name]
Address: [Full Postal Address]

SUBJECT: LEGAL NOTICE CALLING UPON IMMEDIATE REMEDY OF BREACH

Under instructions from and on behalf of our client [Client Name], we hereby state as under:

1. That our client entered into a valid agreement dated [Date] with your organization concerning [Matter Description].
2. That you have committed material breach of contractual covenants by [Specify Breach Particulars].
3. That despite repeated communications, the outstanding dues amounting to [Amount] remain unpaid.

WE THEREFORE CALL UPON YOU to remedy the breach within fifteen (15) days of receipt of this notice, failing which legal proceedings shall be instituted at your sole risk and expense.

Yours faithfully,
[Advocate Name]`,

  "Bail Application": `IN THE SESSIONS COURT / HIGH COURT OF JUDICATURE

CRIMINAL MISC. APPLICATION NO. ___ OF 2026

IN THE MATTER OF:
[Applicant Name] ... Applicant

VERSUS
State Prosecution ... Respondent

APPLICATION FOR REGULAR BAIL UNDER SECTION 479 BNSS, 2023

1. That the Applicant has been falsely implicated in Crime No. [Number] registered at Police Station [Station].
2. That the Applicant has clean antecedents and is ready to furnish solvent surety.
3. That the digital and documentary evidence is already in safe police custody and cannot be tampered with.

PRAYER:
May it please this Hon'ble Court to enlarge the Applicant on regular bail.`,

  "Affidavit": `IN THE HIGH COURT OF JUDICATURE

AFFIDAVIT OF COMPLIANCE & VERIFICATION

I, [Deponent Name], aged [Age] years, residing at [Address], do hereby solemnly affirm and state on oath as under:

1. I am the [Petitioner / Authorized Signatory] in the above-titled proceedings and well conversant with the facts of the case.
2. The statements made in paragraphs 1 to [Number] of the accompanying petition are true to my personal knowledge.
3. No material facts have been concealed or misrepresented.

DEPONENT

VERIFICATION:
Verified at [Location] on this [Date] that the contents of the above affidavit are true and correct.`
};
