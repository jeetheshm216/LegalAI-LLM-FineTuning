import os
import sys
import fitz
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def generate_martinez_documents():
    docs_dir = REPO_ROOT / "data" / "demo_case"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # 1. Interim_Injunction_Order_Bench_IV.pdf
    doc1_path = docs_dir / "Interim_Injunction_Order_Bench_IV.pdf"
    doc1 = fitz.open()
    
    # Page 1
    p1 = doc1.new_page(width=595, height=842)
    text1_p1 = """
IN THE HIGH COURT OF JUDICATURE AT BOMBAY
COMMERCIAL DIVISION · BENCH IV
Commercial Suit No. 1187 of 2024 · Notice of Motion No. 441 of 2024

Julian Martinez                                                ... Plaintiff / Charterer
    v.
Coastal Holdings Ltd.                                          ... Defendant / Vessel Owner

CORAM: THE HON'BLE MR. JUSTICE K. R. MERCHANT
DATE: 02-SEPTEMBER-2026

INTERIM AD-INTERIM INJUNCTION ORDER (Under Section 9, Arbitration & Conciliation Act, 1996)

1. Heard learned Counsel Adv. Elena Vance for the Plaintiff and learned Counsel for the Defendant.
2. The present application seeks urgent interlocutory protection regarding 14,000 MT of industrial 
   catalysts cargo currently situated aboard the vessel 'MV Coastal Trader' docked at Berth 9, 
   Commercial Port Terminal.
3. The Defendant has issued an ultimatum threatening to exercise a maritime possessory lien and 
   auction the cargo to satisfy an alleged demurrage claim of USD 184,000.
4. The Plaintiff establishes prima facie that the charterparty agreement contains an arbitration 
   clause and that invocation of maritime lien is governed by Clause 24 and demurrage accrual 
   is governed by Clause 19(b).
5. The balance of convenience lies decidedly in favor of the plaintiff, considering the perishable 
   nature and volatile chemical shelf-life of the industrial catalysts. Irreparable injury would 
   be caused to the Plaintiff if the cargo is detained or alienated.
"""
    p1.insert_text((50, 60), text1_p1.strip(), fontsize=10, fontname="helv")

    # Page 2
    p2 = doc1.new_page(width=595, height=842)
    text1_p2 = """
Commercial Suit No. 1187 of 2024 · Order dated 02-September-2026 (Page 2)

OPERATIVE DIRECTIONS & SCHEDULING:
6. There shall be an ad-interim status quo order restraining the Defendant Coastal Holdings Ltd., 
   its agents, servants, and representatives from asserting a maritime cargo lien, detaining, selling, 
   transferring, or creating third-party rights in respect of the 14,000 MT of industrial catalysts 
   at Berth 9, pending final hearing of this motion.
7. The Plaintiff Julian Martinez is directed to maintain the security deposit of Rs. 25,00,000 previously 
   deposited with the Court Prothonotary & Senior Master until further orders.
8. Defendant shall file its reply affidavit within 7 days. Rejoinder, if any, within 4 days thereafter.
9. Verified notification from the Maritime Port Terminal Authority regarding stevedore labor disruption 
   must be submitted to the Bench registry prior to next listing.
10. Notice returnable and matter listed for final hearing before Commercial Bench IV on:
    DATE & TIME: 17-SEPTEMBER-2026 AT 10:30 AM.

By Order of the Court,
[Sd/- Registrar, High Court Commercial Division]
"""
    p2.insert_text((50, 60), text1_p2.strip(), fontsize=10, fontname="helv")
    doc1.save(str(doc1_path))
    doc1.close()
    print(f"Generated {doc1_path} (2 pages)")

    # 2. Master_Charterparty_Agreement_Executed.pdf
    doc2_path = docs_dir / "Master_Charterparty_Agreement_Executed.pdf"
    doc2 = fitz.open()

    # Page 1
    p2_1 = doc2.new_page(width=595, height=842)
    text2_p1 = """
MASTER TIME CHARTERPARTY AGREEMENT
================================================================================
VESSEL: MV Coastal Trader (IMO 9481204, Port of Registry: Monrovia)
DATE OF AGREEMENT: 14th December 2023
OWNERS: Coastal Holdings Ltd. (Registered in Port Terminal Commercial Zone)
CHARTERERS: Maritime Conglomerate / Julian Martinez (Sole Proprietor & Cargo Owner)
CARGO: 14,000 MT Industrial Catalysts (Special Handling, Hazard Class 4.2)
DISCHARGE / LOADING LOCATION: Berth 9, Commercial Port Terminal

RECITALS & GENERAL OBLIGATIONS:
The Owners agree to let and the Charterers agree to hire the vessel for transportation and 
berthing of industrial cargo subject to covenants, exceptions, and terms herein stated.

CLAUSE 14: BUNKER SUPPLIES & RUNNING CHARGES
The Charterer shall be responsible for fuel and bunker provision. The parties acknowledge that 
all bunker supply statements and fuel replenishment bills through August 2026 have been fully 
reconciled and cleared in advance by Charterer Julian Martinez without outstanding arrears.
"""
    p2_1.insert_text((50, 60), text2_p1.strip(), fontsize=10, fontname="helv")

    # Page 2
    p2_2 = doc2.new_page(width=595, height=842)
    text2_p2 = """
MASTER TIME CHARTERPARTY AGREEMENT (CONTINUED) · PAGE 2

CLAUSE 19: DEMURRAGE & FORCE MAJEURE SUSPENSION
(a) Demurrage Rate: Demurrage at loading or discharge port shall be computed at the fixed rate 
    of USD 18,500 per running day and pro rata for any part of a day.
(b) Suspension of Demurrage (Force Majeure & Port Strikes): 
    Notwithstanding sub-clause (a), demurrage computation shall pause and be suspended during 
    any period in which vessel operations, cargo clearance, or gate access are interrupted by 
    reason of official port authority strike declarations, labor union stoppages, lockouts, civil 
    commotion, or force majeure delays beyond the reasonable control of the Charterers. 
    No demurrage charges shall accrue against Charterers for the duration of such stoppage.

CLAUSE 24: MARITIME LIEN ON CARGO
The Owners shall have a possessory lien on the cargo only for verified unpaid freight and undisputed 
demurrage. Such lien shall arise only after thirty (30) days formal written notice specifying the 
exact default. No lien may be enforced where a bona fide dispute exists concerning strike suspension 
under Clause 19(b), or where security has been tendered.

EXECUTED BY AUTHORIZED SIGNATORIES:
For Owners: Coastal Holdings Ltd. [Signed: Marcus Vance, Managing Director]
For Charterers: Julian Martinez [Signed: Julian Martinez, Charterer]
"""
    p2_2.insert_text((50, 60), text2_p2.strip(), fontsize=10, fontname="helv")
    doc2.save(str(doc2_path))
    doc2.close()
    print(f"Generated {doc2_path} (2 pages)")

    # 3. Port_Authority_Strike_Notification.pdf
    doc3_path = docs_dir / "Port_Authority_Strike_Notification.pdf"
    doc3 = fitz.open()

    p3_1 = doc3.new_page(width=595, height=842)
    text3_p1 = """
MARITIME PORT TERMINAL AUTHORITY
TRAFFIC & OPERATIONS HEADQUARTERS · HARBOR SECTOR 4
================================================================================
Ref: MPTA/OPS/2026/08-14                                  Date: 14-August-2026

OFFICIAL NOTIFICATION: GENERAL STEVEDORE STRIKE & FORCE MAJEURE CLOSURE

TO ALL PORT USERS, VESSEL MASTERS, TERMINAL OPERATORS, AND CHARTERERS:

1. Notice is hereby formally issued that the Stevedores & Crane Operators Joint Union has declared 
   an immediate general strike commencing on 14-August-2026 at 06:00 hrs.
2. In consequence thereof, all commercial loading, unloading, dock crane hoisting, and terminal gate 
   transit across Docks 1 through 12 (including Berth 9) are completely suspended.
3. The Terminal Authority has officially declared this labor disruption a statutory Force Majeure 
   event under Regulation 41 of the Major Port Authorities (Operations) Regulations.
4. Strike Duration: The continuous stoppage remained active from 14-August-2026 until 22-August-2026 
   at 20:00 hrs, during which no private cargo clearance or stevedoring was permitted.
5. Limited gated access for emergency inspections resumed on 23-August-2026 under restricted shifts.
6. All vessel masters and charterers are notified that port detention during this interval constitutes 
   official authority-mandated stoppage.

Issued under authority of:
Capt. Arvind Swaminathan, Chief Operations Officer
Maritime Port Terminal Authority
"""
    p3_1.insert_text((50, 60), text3_p1.strip(), fontsize=10, fontname="helv")
    doc3.save(str(doc3_path))
    doc3.close()
    print(f"Generated {doc3_path} (1 page)")

    return [
        (doc1_path, "Interim_Injunction_Order_Bench_IV.pdf", "Court Order", "doc-martinez-01"),
        (doc2_path, "Master_Charterparty_Agreement_Executed.pdf", "Contract", "doc-martinez-02"),
        (doc3_path, "Port_Authority_Strike_Notification.pdf", "Evidence", "doc-martinez-03")
    ]

def index_into_rag(files):
    from src.case_rag import CaseRAGPipeline, CaseEmbedder
    
    rag_db = str(REPO_ROOT / "data" / "legalai_case_rag.db")
    print(f"Connecting to Case RAG DB: {rag_db}")
    embedder = CaseEmbedder()
    pipeline = CaseRAGPipeline(index_db_path=rag_db, embedder=embedder)

    case_ids = ["2024-CV-1187", "case-01"]
    for cid in case_ids:
        print(f"\n--- Ingesting documents for case_id='{cid}' ---")
        for fpath, fname, cat, did in files:
            doc = pipeline.ingest_document(
                file_path=str(fpath),
                case_id=cid,
                document_id=f"{did}-{cid}",
                filename=fname,
                category=cat
            )
            print(f"  Ingested {fname} under case_id='{cid}': pages={doc.pages}, status={doc.status}")

    # Verify counts
    cnt_1187 = pipeline.index.count_chunks_for_case("2024-CV-1187")
    cnt_case01 = pipeline.index.count_chunks_for_case("case-01")
    print(f"\nIndexed chunks in legalai_case_rag.db: 2024-CV-1187={cnt_1187}, case-01={cnt_case01}")

    # Register in legalai_app.db
    app_db = str(REPO_ROOT / "data" / "legalai_app.db")
    conn = sqlite3.connect(app_db)
    cur = conn.cursor()
    for fpath, fname, cat, did in files:
        fsize = f"{(fpath.stat().st_size / (1024 * 1024)):.2f} MB" if fpath.stat().st_size > 1024*1024 else f"{(fpath.stat().st_size / 1024):.1f} KB"
        # Register under case-01
        cur.execute("""
            INSERT OR REPLACE INTO documents (
                id, caseId, caseNumber, filename, category, fileType,
                fileSize, uploadedDate, status, statusLabel, pages, excerpt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"{did}-app-01", "case-01", "2024-CV-1187", fname, cat, "pdf",
            fsize, "2026-09-10", "indexed", "Indexed", 2, "Grounded case file document for Martinez v. Coastal Holdings Ltd."
        ))
        # Also register under 2024-CV-1187
        cur.execute("""
            INSERT OR REPLACE INTO documents (
                id, caseId, caseNumber, filename, category, fileType,
                fileSize, uploadedDate, status, statusLabel, pages, excerpt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"{did}-app-1187", "2024-CV-1187", "2024-CV-1187", fname, cat, "pdf",
            fsize, "2026-09-10", "indexed", "Indexed", 2, "Grounded case file document for Martinez v. Coastal Holdings Ltd."
        ))
    conn.commit()
    conn.close()
    print("Registered documents in legalai_app.db")

if __name__ == "__main__":
    generated_files = generate_martinez_documents()
    index_into_rag(generated_files)
