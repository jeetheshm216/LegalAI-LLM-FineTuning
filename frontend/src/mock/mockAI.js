export const INITIAL_CONVERSATIONS = [
  {
    id: "conv-01",
    title: "Injunction & Demurrage Analysis — Martinez v. Coastal",
    mode: "SINGLE_CASE", // GENERAL, MULTI_CASE, SINGLE_CASE
    caseId: "case-01",
    caseNumber: "2024-CV-1187",
    selectedCases: ["case-01"],
    contextSettings: {
      includeDocuments: true,
      includeNotes: true,
      includeTimeline: true,
      includeHistory: true,
      supportingCases: []
    },
    updatedAt: "Today, 11:20 AM",
    messages: [
      {
        id: "msg-101",
        role: "user",
        timestamp: "11:18 AM",
        content: "Under our charterparty agreement and the recent Port Authority Strike notification, what are our strongest arguments to restrain Coastal Holdings from asserting a maritime cargo lien?"
      },
      {
        id: "msg-102",
        role: "assistant",
        timestamp: "11:19 AM",
        reliability: "supported", // supported, limited, verify
        reliabilityLabel: "Supported by sources",
        content: `Based on an examination of the **Master Charterparty Agreement** and the **Port Authority Strike Notification**, there are two primary grounds to oppose Coastal Holdings' lien enforcement:

### 1. Force Majeure & Demurrage Suspension
Clause 19(b) explicitly provides that demurrage computations are suspended during official port authority strikes. Because the strike commenced on August 14 under an official terminal directive, Coastal Holdings cannot lawfully accrue demurrage charges during this interval. Consequently, their claim of outstanding demurrage totaling $184,000 lacks contractual basis.

### 2. Lack of Possessory Ground for Maritime Lien
Under maritime admiralty standards, a shipowner's lien requires rightful and continuous detention of the cargo based on enforceable debt. Because the cargo consists of perishable industrial catalysts whose market value diminishes with detention, the balance of convenience heavily favors preserving the status quo under Section 9 of the Arbitration Act.

> "The balance of convenience lies decidedly in favor of the plaintiff, considering the perishable value of the industrial catalysts."
> — High Court Commercial Bench IV (Notice of Motion 441/2024)

### Recommended Course of Action
1. Move the Commercial Bench to convert the ad-interim order into a permanent injunction pending arbitration.
2. Offer security for disputed bunker charges into court registry to eliminate any equitable lien claim.`,
        sources: [
          {
            id: "src-1",
            type: "document", // document, statute, judgment
            title: "Master_Charterparty_Agreement_Executed.pdf",
            reference: "Page 22, Clause 19(b)",
            excerpt: "Demurrage computation shall pause during port authority strike declarations or force majeure delays."
          },
          {
            id: "src-2",
            type: "document",
            title: "Interim_Injunction_Order_Bench_IV.pdf",
            reference: "Page 4, Para 12",
            excerpt: "The balance of convenience lies decidedly in favor of the plaintiff, considering the perishable value of the industrial catalysts."
          },
          {
            id: "src-3",
            type: "statute",
            title: "Arbitration & Conciliation Act",
            reference: "Section 9(1)(ii)(a)",
            excerpt: "Interim measures for the preservation, interim custody or sale of any goods which are the subject-matter of the arbitration agreement."
          }
        ]
      }
    ]
  },
  {
    id: "conv-02",
    title: "Electronic Evidence Admissibility (BSA s.63 vs BNSS)",
    mode: "MULTI_CASE",
    caseId: null,
    caseNumber: null,
    selectedCases: ["case-01", "case-02"],
    contextSettings: {
      includeDocuments: true,
      includeNotes: false,
      includeTimeline: true,
      includeHistory: true,
      supportingCases: ["case-01", "case-02"]
    },
    updatedAt: "Yesterday",
    messages: [
      {
        id: "msg-201",
        role: "user",
        timestamp: "Yesterday, 03:40 PM",
        content: "Compare the electronic evidence chain-of-custody requirements under Bharatiya Sakshya Adhiniyam (BSA) Section 63 with previous Indian Evidence Act Section 65B requirements."
      },
      {
        id: "msg-202",
        role: "assistant",
        timestamp: "Yesterday, 03:42 PM",
        reliability: "supported",
        reliabilityLabel: "Supported by sources",
        content: `Under the **Bharatiya Sakshya Adhiniyam, 2023 (BSA)**, Section 63 governs the admissibility of electronic records, succeeding Section 65B of the Indian Evidence Act, 1872. Key procedural transitions include:

### 1. Mandatory Certificate Format & Expert Endorsement
BSA Section 63(4) now specifies that the certificate must be signed by a person in charge of the computer device or management of relevant activities, and optionally validated by an examiner of electronic evidence under Section 79A.

### 2. Hash Digest Validation
Unlike older jurisprudence where oral testimony could sometimes cure defective certificates, judicial practice under BSA mandates cryptographic hash verification (e.g. SHA-256) at the time of electronic seizure.

### Impact on State v. Whitfield (#2024-CR-0442)
The Police ChargeSheet cites CFSL verification, but the hash value on record was generated 18 days post-seizure without contemporaneous sealing under BNSS Section 105. This constitutes a substantial procedural defense.`,
        sources: [
          {
            id: "src-4",
            type: "statute",
            title: "The Bharatiya Sakshya Adhiniyam, 2023 (Act 47 of 2023)",
            reference: "Section 63(4), Schedule Part A",
            excerpt: "Admissibility of electronic records and requirements for contemporaneous certification."
          },
          {
            id: "src-5",
            type: "document",
            title: "Digital_Forensic_Chain_Of_Custody.pdf",
            reference: "Page 2, Item 4",
            excerpt: "Hash digest recorded on 24-04-2024; seizure conducted on 06-04-2024."
          }
        ]
      }
    ]
  },
  {
    id: "conv-03",
    title: "General Research: Limitation Periods for Testamentary Caveats",
    mode: "GENERAL",
    caseId: null,
    caseNumber: null,
    selectedCases: [],
    contextSettings: {
      includeDocuments: false,
      includeNotes: false,
      includeTimeline: false,
      includeHistory: false,
      supportingCases: []
    },
    updatedAt: "Sep 9, 2026",
    messages: [
      {
        id: "msg-301",
        role: "user",
        timestamp: "Sep 9, 05:10 PM",
        content: "What is the statutory limitation period to lodge a caveat against a probate petition in High Court testamentary proceedings?"
      },
      {
        id: "msg-302",
        role: "assistant",
        timestamp: "Sep 9, 05:11 PM",
        reliability: "limited",
        reliabilityLabel: "Limited supporting evidence",
        content: `Under High Court Original Side Rules governing Testamentary and Intestate Jurisdiction:

1. **Caveat Lodgment Window**: Any person intending to oppose the grant of probate or letters of administration must file a caveat within **14 days** from the service of citation upon them, or within 14 days of publication of notice.
2. **Affidavit in Support**: An affidavit in support of the caveat setting out the grounds of objection must be filed within **8 days** from the date of lodging the caveat.
3. **Conversion to Suit**: Upon lodging a supported caveat, the petition is numbered and registered as a contentious testamentary suit.

*Note: Specific High Court rules vary slightly between jurisdictions (e.g. Bombay High Court Rules Chapter XXVI vs Calcutta High Court Chapter XXXV).*`,
        sources: [
          {
            id: "src-6",
            type: "statute",
            title: "Indian Succession Act, 1925",
            reference: "Section 284 & Section 285",
            excerpt: "Caveats against grant of probate or administration."
          }
        ]
      }
    ]
  }
];

export const MOCK_LEGAL_RESPONSES = [
  {
    trigger: "bail",
    content: `Regarding bail review under BNSS Section 479 & 480:

### 1. First-time Offender Statutory Entitlement
Under Section 479 of the Bharatiya Nagarik Suraksha Sanhita, an undertrial prisoner who is a first-time offender is entitled to release on bond if they have undergone detention extending up to one-third of the maximum period of imprisonment.

### 2. Absence of Flight Risk
In Arthur Whitfield's matter, the accused has surrendered all international travel documents and possesses established commercial roots within the jurisdiction.

### Recommended Next Step:
Draft a supplementary memorandum highlighting compliance with the CFSL deposition requirements.`,
    sources: [
      {
        id: "s-10",
        type: "statute",
        title: "The Bharatiya Nagarik Suraksha Sanhita, 2023",
        reference: "Section 479(1) Proviso",
        excerpt: "Maximum period for which undertrial prisoner can be detained."
      }
    ],
    reliability: "supported",
    reliabilityLabel: "Supported by sources"
  },
  {
    trigger: "default",
    content: `I have analyzed the matter across the active legal context.

### Findings:
1. The contractual covenants provide explicit procedural remedies prior to invoking forfeiture or lien provisions.
2. Evidentiary records require contemporaneous certification under statutory disclosure rules.
3. The opposing party bears the burden of establishing prima facie non-compliance with the interim directions.

### Strategic Recommendations:
- Submit the rejoinder affidavit within the 7-day window.
- Preserve all electronic mail headers to establish chain-of-custody in court.`,
    sources: [
      {
        id: "s-99",
        type: "document",
        title: "Matter_Record_Dossier.pdf",
        reference: "Section 4, Page 12",
        excerpt: "Procedural stipulations governing interlocutory relief."
      }
    ],
    reliability: "supported",
    reliabilityLabel: "Supported by sources"
  }
];
