"""
src/api/server.py

FastAPI backend server for LegalAI.
Provides a thin HTTP and SSE layer directly connected to the existing
production LegalAIRAGPipeline (Qwen2.5-14B-Instruct + outputs/qwen14b-legalai-v2).
Operates strictly on Physical GPU 2 (CUDA_VISIBLE_DEVICES=2).
"""

import os
import sys
import time
import json
import sqlite3
import shutil
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Enforce Physical GPU 2 before torch/cuda initialization
os.environ["CUDA_VISIBLE_DEVICES"] = "2"

import torch
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

# Existing LegalAI RAG Pipeline & Query Router
from src.rag.integration.rag_legalai import LegalAIRAGPipeline
from src.api.query_router import QueryRouter, QueryIntent, get_query_router
from src.case_rag import CaseRAGPipeline, CaseEmbedder

# Global singleton RAG pipeline & Case RAG pipeline
pipeline: Optional[LegalAIRAGPipeline] = None
case_rag_pipeline: Optional[CaseRAGPipeline] = None

# SQLite database for Cases and Documents metadata
APP_DB_PATH = REPO_ROOT / "data" / "legalai_app.db"
DOCS_STORAGE_DIR = REPO_ROOT / "data" / "case_documents"


def init_app_database():
    """Initializes local SQLite schema for cases and documents."""
    os.makedirs(APP_DB_PATH.parent, exist_ok=True)
    os.makedirs(DOCS_STORAGE_DIR, exist_ok=True)

    conn = sqlite3.connect(APP_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        caseNumber TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        client TEXT NOT NULL,
        opposingParty TEXT,
        court TEXT NOT NULL,
        caseType TEXT NOT NULL,
        status TEXT NOT NULL,
        priority TEXT NOT NULL,
        filedDate TEXT NOT NULL,
        nextHearing TEXT,
        hearingCountdownDays INTEGER,
        assignedLawyer TEXT,
        description TEXT,
        matterSummary TEXT,
        tags TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        caseId TEXT NOT NULL,
        caseNumber TEXT NOT NULL,
        filename TEXT NOT NULL,
        category TEXT NOT NULL,
        fileType TEXT NOT NULL,
        fileSize TEXT NOT NULL,
        uploadedDate TEXT NOT NULL,
        status TEXT NOT NULL,
        statusLabel TEXT NOT NULL,
        pages INTEGER DEFAULT 1,
        excerpt TEXT,
        storagePath TEXT,
        FOREIGN KEY(caseId) REFERENCES cases(id)
    )
    """)

    # Seed default cases if empty
    cursor.execute("SELECT COUNT(*) FROM cases")
    count = cursor.fetchone()[0]
    if count == 0:
        default_cases = [
            (
                "case-01", "2024-CV-1187", "Martinez v. Coastal Holdings Ltd.",
                "Julian Martinez", "Coastal Holdings Ltd.",
                "High Court of Commercial Jurisdiction, Bench IV",
                "Commercial Contracts & Maritime Liens", "Urgent", "urgent",
                "2024-03-14", "2026-09-17 10:30 AM", 4, "Adv. Elena Vance",
                "Injunction application regarding contested charterparty freight dispute and cargo lien under Maritime Commercial Regulations.",
                "Breach of contract claim alleging premature lien enforcement on 14,000 MT industrial cargo docked at Berth 9. Preliminary injunction hearing scheduled this week.",
                json.dumps(["Injunction", "Maritime", "Priority Review"])
            ),
            (
                "case-02", "2024-CR-0442", "State v. Whitfield",
                "Arthur Whitfield", "State Department of Public Prosecutions",
                "District Sessions Court, First Division",
                "Substantive Criminal Law & Procedure", "Active", "normal",
                "2024-01-22", "2026-09-24 11:00 AM", 11, "Adv. Elena Vance",
                "Statutory defense and bail review under Section 111 & 316 of the criminal code. ChargeSheet scrutiny and digital forensic validation.",
                "Reviewing chargesheet documentation, search seizure chain-of-custody, and application for regular bail before the Sessions Judge.",
                json.dumps(["Criminal Defense", "Bail Application", "Digital Evidence"])
            ),
            (
                "case-03", "2024-CV-0998", "In re Nguyen Estate Testamentary Probate",
                "Thao Nguyen (Executor)", "Contesting Beneficiaries (represented by Sterling & Cole LLP)",
                "High Court Probate & Testamentary Division",
                "Succession & Trust Law", "Pending", "normal",
                "2024-05-09", "2026-10-08 02:00 PM", 25, "Adv. Elena Vance",
                "Petition for Grant of Probate under valid codicil; preliminary objections filed alleging undue influence and lack of testamentary capacity.",
                "Awaiting filing of cross-affidavits of attesting witnesses and deposition schedule for testamentary capacity assessment.",
                json.dumps(["Probate", "Testamentary", "Estate Trust"])
            ),
            (
                "case-04", "2024-CC-0120", "Apex Logistics Corp. v. Horizon Freight Services",
                "Apex Logistics Corp.", "Horizon Freight Services",
                "Commercial Appellate Tribunal",
                "Arbitration & Commercial Enforcement", "Upcoming", "normal",
                "2024-06-18", "2026-09-30 09:30 AM", 17, "Adv. Marcus Sterling",
                "Section 9 interim measures petition pending constitution of the arbitral tribunal concerning supply chain exclusivity covenants.",
                "Hearing scheduled for ad-interim relief restraining enforcement of liquidated damages under Section 9 of the Arbitration Act.",
                json.dumps(["Commercial", "Arbitration", "Ad-Interim Relief"])
            )
        ]

        cursor.executemany("""
        INSERT INTO cases (
            id, caseNumber, title, client, opposingParty, court, caseType,
            status, priority, filedDate, nextHearing, hearingCountdownDays,
            assignedLawyer, description, matterSummary, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, default_cases)

    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes DB and loads singleton RAG pipeline once."""
    global pipeline, case_rag_pipeline
    print("\n" + "=" * 65)
    print("STARTING LEGALAI FASTAPI SERVICE")
    print(f"Target Host / Device: Physical GPU 2 (CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')})")
    print(f"Database Path:       {REPO_ROOT / 'data' / 'legalai_rag_mvp.db'}")
    print("=" * 65)

    init_app_database()

    print("Initializing production LegalAIRAGPipeline...")
    pipeline = LegalAIRAGPipeline(
        db_path=str(REPO_ROOT / "data" / "legalai_rag_mvp.db"),
        base_model_name="Qwen/Qwen2.5-14B-Instruct",
        adapter_dir=str(REPO_ROOT / "outputs" / "qwen14b-legalai-v2"),
        device="cuda:0"
    )

    print("Pre-loading Qwen model and LegalAI V2 LoRA adapter into GPU memory...")
    pipeline.load_model()
    print("LegalAIRAGPipeline ready for incoming requests.\n")

    # Load Case Analysis V1 LoRA adapter onto existing model singleton
    case_v1_path = str(REPO_ROOT / "outputs" / "qwen14b-case-analysis-v1")
    if os.path.exists(case_v1_path) and hasattr(pipeline.model, "load_adapter"):
        print(f"Registering Case Analysis V1 adapter from {case_v1_path}...")
        try:
            pipeline.model.load_adapter(case_v1_path, adapter_name="case_analysis_v1")
            pipeline.model.set_adapter("default")
            print("Successfully registered 'case_analysis_v1' adapter on model singleton.")
        except Exception as e:
            print(f"Warning loading case_analysis_v1 adapter: {e}")

    # Initialize Case Document RAG Subsystem
    print("Initializing Case Document RAG subsystem...")
    case_rag_db = str(REPO_ROOT / "data" / "legalai_case_rag.db")
    case_embedder = CaseEmbedder(existing_model=pipeline.embedder.model)
    case_rag_pipeline = CaseRAGPipeline(
        index_db_path=case_rag_db,
        base_pipeline=pipeline,
        embedder=case_embedder
    )
    print("CaseRAGPipeline ready for document ingestion and case analysis.\n")

    yield

    print("Shutting down LegalAI API service...")


app = FastAPI(
    title="LegalAI — Production RAG API",
    version="2.0.0",
    description="Thin API layer over Qwen2.5-14B + V2 LoRA + Indian Statutory RAG",
    lifespan=lifespan
)

# CORS: Allow local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------
class AIChatRequest(BaseModel):
    content: str = Field(..., description="Legal question query")
    conversationId: Optional[str] = "conv-default"
    mode: Optional[str] = "GENERAL"
    caseId: Optional[str] = None
    caseNumber: Optional[str] = None
    selectedCases: Optional[List[str]] = []
    contextSettings: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, Any]]] = []
    effective_date: Optional[str] = None
    act_filter: Optional[str] = None
    section_filter: Optional[str] = None


class AIContextualRequest(BaseModel):
    selectedText: str = Field(..., description="Selected legal excerpt")
    question: Optional[str] = Field("", description="Follow-up question")
    conversationContext: Optional[Dict[str, Any]] = {}


class CaseCreateRequest(BaseModel):
    title: str
    client: str
    opposingParty: Optional[str] = "Undisclosed"
    court: str
    caseType: str
    status: Optional[str] = "Active"
    priority: Optional[str] = "normal"
    filedDate: Optional[str] = None
    nextHearing: Optional[str] = "None scheduled"
    hearingCountdownDays: Optional[int] = None
    assignedLawyer: Optional[str] = "Adv. Elena Vance"
    description: Optional[str] = ""
    matterSummary: Optional[str] = ""
    tags: Optional[List[str]] = ["New Matter"]


class CaseStatusUpdateRequest(BaseModel):
    status: str


# -------------------------------------------------------------
# Reliability & Citation Helpers
# -------------------------------------------------------------
def map_reliability(rag_result: dict) -> tuple[str, str]:
    """Maps RAG confidence & citation verification to frontend reliability contract."""
    conf = rag_result.get("confidence_status", "")
    evid = rag_result.get("evidence_status", "")
    verif = rag_result.get("citation_verification", {})
    is_valid = verif.get("is_valid", True) if verif else True

    if conf == "GROUNDED_STATUTORY" and is_valid:
        return "supported", "Supported by sources"
    elif conf == "TEMPORAL_TRANSITION_APPLIED" or evid == "TEMPORALLY_UNCERTAIN":
        return "limited", "Temporal transition applied"
    else:
        return "verify", "Requires verification"


def format_sources(retrieved_sources: list) -> list:
    """Formats retrieved section metadata into frontend sources contract."""
    sources = []
    for idx, s in enumerate(retrieved_sources):
        act_name = s.get("act_name") or s.get("act_prefix") or "Statute"
        sec = s.get("section_number") or ""
        title = s.get("section_title") or f"{act_name} Section {sec}".strip()
        sources.append({
            "id": s.get("chunk_id") or f"src-{idx+1}",
            "type": "statute",
            "title": act_name,
            "reference": f"Section {sec}" if sec else title,
            "excerpt": s.get("section_title") or f"{act_name} Section {sec}".strip()
        })
    return sources


# -------------------------------------------------------------
# Conversational Prompt & Single-Model Generation Helper
# -------------------------------------------------------------
CONVERSATIONAL_SYSTEM_PROMPT = """You are LegalAI, an advanced AI assistant designed specifically for advocates and legal professionals.

You converse naturally, professionally, and courteously. You can introduce yourself, explain your capabilities, and assist with general inquiries.

IMPORTANT OPERATIONAL PRINCIPLES:
1. IDENTITY & CAPABILITIES:
   You are LegalAI, created to assist legal professionals with statutory research, criminal procedure, evidence evaluation, and case matter intelligence under Indian law.
2. STATUTORY GROUNDING BOUNDARY:
   When the user asks for legal facts, statutes, sections, current law, or authoritative legal verification, the application routes the request through the authoritative legal retrieval pipeline (Legal RAG).
   Do not claim that you verified a legal proposition unless authoritative sources were actually provided by the application.
3. CONVERSATIONAL DEMEANOR:
   Keep conversational greetings, assistance offers, and identity answers concise, warm, articulate, and ready to assist with legal research or case analysis."""


def generate_conversational_response(
    pipeline: LegalAIRAGPipeline,
    message: str,
    max_new_tokens: int = 256
) -> str:
    """Generates a natural conversational response reusing the existing Qwen2.5-14B + LoRA singleton."""
    messages = [
        {"role": "system", "content": CONVERSATIONAL_SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ]
    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = pipeline.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(pipeline.device) for k, v in inputs.items()}
    input_length = inputs["input_ids"].shape[1]

    with torch.inference_mode():
        output_ids = pipeline.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=pipeline.tokenizer.pad_token_id,
            eos_token_id=pipeline.tokenizer.eos_token_id,
        )

    new_tokens = output_ids[0, input_length:]
    return pipeline.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def generate_case_guidance(case_id: Optional[str] = None) -> str:
    """Generates factual case guidance based on registered case matter without fabricating case facts."""
    if case_id:
        conn = sqlite3.connect(APP_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT caseNumber, title, court, status, nextHearing, matterSummary FROM cases WHERE id = ?",
            (case_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return (
                f"**Case Matter:** {row[1]} ({row[0]})\n"
                f"**Court:** {row[2]} | **Status:** {row[3]}\n"
                f"**Next Hearing:** {row[4]}\n\n"
                f"**Summary of Matter:**\n{row[5]}\n\n"
                f"*Case Document Intelligence (Case RAG) is currently connected to this matter. "
                f"To analyze specific pleadings, FIRs, or orders, please ensure relevant documents are uploaded in the Case Documents tab. "
                f"For statutory law or legal research questions, feel free to ask directly.*"
            )
    return (
        "You are inquiring about specific case matter or evidentiary documents. "
        "To analyze a case, please select an active matter from the Case Files view or upload relevant case documents in the Documents manager. "
        "For statutory questions or general legal research (such as under BNS, BNSS, or BSA), you can ask directly anytime."
    )


# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------
@app.get("/api/v1/health")
async def health_check():
    """Health endpoint exposing model and GPU status."""
    import torch
    global pipeline, case_rag_pipeline
    return {
        "status": "healthy",
        "service": "LegalAI RAG API",
        "version": "2.0.0",
        "gpu": {
            "device": "Physical GPU 2",
            "cuda_available": torch.cuda.is_available(),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", "2")
        },
        "model": {
            "base_model": "Qwen/Qwen2.5-14B-Instruct",
            "adapter": "outputs/qwen14b-legalai-v2",
            "is_loaded": pipeline is not None and pipeline.model is not None
        },
        "rag": {
            "database": "data/legalai_rag_mvp.db",
            "statutes": ["BNS", "BNSS", "BSA"]
        },
        "case_rag": {
            "database": "data/legalai_case_rag.db",
            "is_loaded": case_rag_pipeline is not None,
            "adapter": "outputs/qwen14b-case-analysis-v1"
        },
        "auth": {
            "status": "pending_backend_auth",
            "description": "Backend authentication pending; using frontend demo session"
        }
    }


# --- Case Management ---
@app.get("/api/v1/cases")
async def get_cases():
    """Returns all scoped cases."""
    conn = sqlite3.connect(APP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, caseNumber, title, client, opposingParty, court, caseType,
               status, priority, filedDate, nextHearing, hearingCountdownDays,
               assignedLawyer, description, matterSummary, tags
        FROM cases ORDER BY filedDate DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    cases = []
    for r in rows:
        cases.append({
            "id": r[0],
            "caseNumber": r[1],
            "title": r[2],
            "client": r[3],
            "opposingParty": r[4],
            "court": r[5],
            "caseType": r[6],
            "status": r[7],
            "priority": r[8],
            "filedDate": r[9],
            "nextHearing": r[10],
            "hearingCountdownDays": r[11],
            "assignedLawyer": r[12],
            "description": r[13],
            "matterSummary": r[14],
            "tags": json.loads(r[15]) if r[15] else []
        })
    return cases


@app.get("/api/v1/cases/{case_id}")
async def get_case_by_id(case_id: str):
    """Returns a single case by ID or caseNumber."""
    conn = sqlite3.connect(APP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, caseNumber, title, client, opposingParty, court, caseType,
               status, priority, filedDate, nextHearing, hearingCountdownDays,
               assignedLawyer, description, matterSummary, tags
        FROM cases WHERE id = ? OR caseNumber = ?
    """, (case_id, case_id))
    r = cursor.fetchone()
    conn.close()

    if not r:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    return {
        "id": r[0],
        "caseNumber": r[1],
        "title": r[2],
        "client": r[3],
        "opposingParty": r[4],
        "court": r[5],
        "caseType": r[6],
        "status": r[7],
        "priority": r[8],
        "filedDate": r[9],
        "nextHearing": r[10],
        "hearingCountdownDays": r[11],
        "assignedLawyer": r[12],
        "description": r[13],
        "matterSummary": r[14],
        "tags": json.loads(r[15]) if r[15] else []
    }


@app.post("/api/v1/cases", status_code=status.HTTP_201_CREATED)
async def create_case(case_data: CaseCreateRequest):
    """Creates a new legal matter."""
    case_id = f"case-{int(time.time() * 1000)}"
    case_number = f"2026-CV-{int(time.time()) % 10000}"
    filed_date = case_data.filedDate or time.strftime("%Y-%m-%d")

    conn = sqlite3.connect(APP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cases (
            id, caseNumber, title, client, opposingParty, court, caseType,
            status, priority, filedDate, nextHearing, hearingCountdownDays,
            assignedLawyer, description, matterSummary, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id, case_number, case_data.title, case_data.client,
        case_data.opposingParty, case_data.court, case_data.caseType,
        case_data.status, case_data.priority, filed_date,
        case_data.nextHearing, case_data.hearingCountdownDays,
        case_data.assignedLawyer, case_data.description,
        case_data.matterSummary or case_data.description,
        json.dumps(case_data.tags or ["New Matter"])
    ))
    conn.commit()
    conn.close()

    return await get_case_by_id(case_id)


@app.patch("/api/v1/cases/{case_id}/status")
async def update_case_status(case_id: str, body: CaseStatusUpdateRequest):
    """Updates case status."""
    conn = sqlite3.connect(APP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE cases SET status = ? WHERE id = ? OR caseNumber = ?", (body.status, case_id, case_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    conn.commit()
    conn.close()
    return await get_case_by_id(case_id)


# --- Document Management ---
@app.get("/api/v1/cases/{case_id}/documents")
async def get_case_documents(case_id: str):
    """Returns documents associated with a case."""
    conn = sqlite3.connect(APP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, caseId, caseNumber, filename, category, fileType,
               fileSize, uploadedDate, status, statusLabel, pages, excerpt
        FROM documents WHERE caseId = ?
    """, (case_id,))
    rows = cursor.fetchall()
    conn.close()

    docs = []
    for r in rows:
        docs.append({
            "id": r[0],
            "caseId": r[1],
            "caseNumber": r[2],
            "filename": r[3],
            "category": r[4],
            "fileType": r[5],
            "fileSize": r[6],
            "uploadedDate": r[7],
            "status": r[8],
            "statusLabel": r[9],
            "pages": r[10],
            "excerpt": r[11]
        })
    return docs


@app.post("/api/v1/cases/{case_id}/documents")
async def upload_case_document(
    case_id: str,
    file: UploadFile = File(...),
    caseNumber: Optional[str] = Form(None),
    category: Optional[str] = Form("Evidence")
):
    """Uploads, stores, and indexes a case document into the Case RAG layer."""
    global case_rag_pipeline
    doc_id = f"doc-{int(time.time() * 1000)}"
    case_dir = DOCS_STORAGE_DIR / case_id
    os.makedirs(case_dir, exist_ok=True)
    target_path = case_dir / file.filename

    # Save file contents
    content = await file.read()
    with open(target_path, "wb") as f:
        f.write(content)

    file_size_mb = f"{(len(content) / (1024 * 1024)):.2f} MB"
    ext = file.filename.lower().split(".")[-1] if "." in file.filename else "pdf"
    file_type = ext
    uploaded_date = time.strftime("%Y-%m-%d")

    # Ingest document into Case RAG subsystem
    pages = 1
    doc_status = "indexed"
    doc_status_label = "Indexed"
    excerpt = "Document uploaded and indexed into case file repository."

    if case_rag_pipeline:
        try:
            ingested_doc = await asyncio.to_thread(
                case_rag_pipeline.ingest_document,
                case_id=case_id,
                file_path=str(target_path),
                filename=file.filename,
                category=category or "Evidence"
            )
            pages = ingested_doc.pages or 1
            doc_id = ingested_doc.id
            excerpt = f"{file.filename} ({pages} pages) indexed into Case Document RAG."
        except Exception as e:
            print(f"Error ingesting document into Case RAG: {e}")
            doc_status = "failed"
            doc_status_label = "Failed"
            excerpt = f"Processing error: {str(e)}"

    conn = sqlite3.connect(APP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (
            id, caseId, caseNumber, filename, category, fileType,
            fileSize, uploadedDate, status, statusLabel, pages, excerpt, storagePath
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doc_id, case_id, caseNumber or "Case Matter", file.filename,
        category, file_type, file_size_mb, uploaded_date,
        doc_status, doc_status_label, pages, excerpt,
        str(target_path)
    ))
    conn.commit()
    conn.close()

    return {
        "id": doc_id,
        "caseId": case_id,
        "caseNumber": caseNumber or "Case Matter",
        "filename": file.filename,
        "category": category,
        "fileType": file_type,
        "fileSize": file_size_mb,
        "uploadedDate": uploaded_date,
        "status": doc_status,
        "statusLabel": doc_status_label,
        "pages": pages,
        "excerpt": excerpt
    }


@app.get("/api/v1/documents/{doc_id}/status")
async def get_document_status(doc_id: str):
    """Returns indexing status of a document."""
    conn = sqlite3.connect(APP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status, statusLabel FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"id": doc_id, "status": "indexed", "statusLabel": "Indexed"}

    return {"id": doc_id, "status": row[0], "statusLabel": row[1]}


# --- Legal AI Assistant ---
@app.post("/api/v1/ai/chat")
async def ai_chat(req: AIChatRequest):
    """Executes Query Router followed by Conversational Generation or full LegalAI RAG Pipeline."""
    global pipeline, case_rag_pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="LegalAI RAG Pipeline is initializing")

    t0 = time.time()
    router = get_query_router()
    route_result = router.classify(req.content, conversation_history=req.history)

    # Route 1: CONVERSATIONAL
    if route_result.intent == QueryIntent.CONVERSATIONAL:
        answer_text = await asyncio.to_thread(
            generate_conversational_response,
            pipeline=pipeline,
            message=req.content,
            max_new_tokens=256
        )
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "CONVERSATIONAL",
            "type": "conversational",
            "reliability": "supported",
            "reliabilityLabel": "General Assistance",
            "sources": [],
            "citations": [],
            "requires_verification": False,
            "confidence_status": "CONVERSATIONAL",
            "evidence_status": "CONVERSATIONAL",
            "generation_time_sec": round(time.time() - t0, 3)
        }

    # Route 2: CASE_QUERY or (Case Mode and not an explicit statutory query)
    effective_case_id = req.caseId or (req.selectedCases[0] if (req.selectedCases and len(req.selectedCases) > 0) else None)
    is_case_mode = (req.mode == "SINGLE_CASE" and effective_case_id) or (req.selectedCases and len(req.selectedCases) > 0)

    if route_result.intent == QueryIntent.CASE_QUERY or (is_case_mode and route_result.intent != QueryIntent.LEGAL_QUERY):
        if not effective_case_id:
            answer_text = generate_case_guidance(None)
            sources = []
            rel = "supported"
            rel_label = "Case Guidance"
            conf_status = "CASE_GUIDANCE"
        elif case_rag_pipeline:
            case_analysis = await asyncio.to_thread(
                case_rag_pipeline.answer_case_question,
                question=req.content,
                case_id=effective_case_id,
                top_k=6,
                max_new_tokens=768
            )
            answer_text = case_analysis.answer
            sources = case_analysis.case_sources + case_analysis.legal_sources
            rel = case_analysis.reliability
            rel_label = case_analysis.reliability_label
            conf_status = case_analysis.confidence_status
        else:
            answer_text = generate_case_guidance(effective_case_id)
            sources = []
            rel = "supported"
            rel_label = "Case Guidance"
            conf_status = "CASE_GUIDANCE"

        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "CASE_QUERY",
            "type": "case_analysis",
            "reliability": rel,
            "reliabilityLabel": rel_label,
            "sources": sources,
            "citations": [s.get("reference", "") for s in sources],
            "requires_verification": (rel == "verify"),
            "confidence_status": conf_status,
            "evidence_status": "ANALYZED" if sources else "INSUFFICIENT_CASE_MATERIAL",
            "generation_time_sec": round(time.time() - t0, 3)
        }

    # Route 3: LEGAL_QUERY (Existing unweakened LegalAIRAGPipeline)
    rag_result = await asyncio.to_thread(
        pipeline.answer_question,
        question=req.content,
        act_filter=req.act_filter,
        section_filter=req.section_filter,
        effective_date=req.effective_date,
        top_k=5,
        max_new_tokens=512
    )

    rel, rel_label = map_reliability(rag_result)
    sources = format_sources(rag_result.get("retrieved_sources", []))

    return {
        "id": f"msg-{int(time.time() * 1000)}",
        "role": "assistant",
        "timestamp": time.strftime("%I:%M %p"),
        "content": rag_result.get("answer", ""),
        "query_type": "LEGAL_QUERY",
        "type": "legal",
        "reliability": rel,
        "reliabilityLabel": rel_label,
        "sources": sources,
        "citations": rag_result.get("citations", []),
        "requires_verification": (rel == "verify"),
        "confidence_status": rag_result.get("confidence_status", ""),
        "evidence_status": rag_result.get("evidence_status", ""),
        "generation_time_sec": rag_result.get("generation_time_sec", 0.0)
    }


@app.post("/api/v1/ai/chat/stream")
async def ai_chat_stream(req: AIChatRequest):
    """Server-Sent Events (SSE) streaming endpoint for LegalAI Assistant."""
    global pipeline, case_rag_pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="LegalAI RAG Pipeline is initializing")

    router = get_query_router()
    route_result = router.classify(req.content, conversation_history=req.history)

    async def event_generator():
        t0 = time.time()

        # Stream Route 1: CONVERSATIONAL
        if route_result.intent == QueryIntent.CONVERSATIONAL:
            answer_text = await asyncio.to_thread(
                generate_conversational_response,
                pipeline=pipeline,
                message=req.content,
                max_new_tokens=256
            )
            words = answer_text.split(" ")
            current_text = ""
            for i, word in enumerate(words):
                current_text += (word if i == 0 else " " + word)
                token_payload = {"token": current_text}
                yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
                await asyncio.sleep(0.015)

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": answer_text,
                "query_type": "CONVERSATIONAL",
                "type": "conversational",
                "reliability": "supported",
                "reliabilityLabel": "General Assistance",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "CONVERSATIONAL",
                "evidence_status": "CONVERSATIONAL",
                "generation_time_sec": round(time.time() - t0, 3)
            }
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2: CASE_QUERY or (Case Mode and not an explicit statutory query)
        effective_case_id = req.caseId or (req.selectedCases[0] if (req.selectedCases and len(req.selectedCases) > 0) else None)
        is_case_mode = (req.mode == "SINGLE_CASE" and effective_case_id) or (req.selectedCases and len(req.selectedCases) > 0)

        if route_result.intent == QueryIntent.CASE_QUERY or (is_case_mode and route_result.intent != QueryIntent.LEGAL_QUERY):
            if not effective_case_id:
                answer_text = generate_case_guidance(None)
                sources = []
                rel = "supported"
                rel_label = "Case Guidance"
                conf_status = "CASE_GUIDANCE"
            elif case_rag_pipeline:
                case_analysis = await asyncio.to_thread(
                    case_rag_pipeline.answer_case_question,
                    question=req.content,
                    case_id=effective_case_id,
                    top_k=6,
                    max_new_tokens=768
                )
                answer_text = case_analysis.answer
                sources = case_analysis.case_sources + case_analysis.legal_sources
                rel = case_analysis.reliability
                rel_label = case_analysis.reliability_label
                conf_status = case_analysis.confidence_status
            else:
                answer_text = generate_case_guidance(effective_case_id)
                sources = []
                rel = "supported"
                rel_label = "Case Guidance"
                conf_status = "CASE_GUIDANCE"

            words = answer_text.split(" ")
            current_text = ""
            for i, word in enumerate(words):
                current_text += (word if i == 0 else " " + word)
                token_payload = {"token": current_text}
                yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
                await asyncio.sleep(0.015)

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": answer_text,
                "query_type": "CASE_QUERY",
                "type": "case_analysis",
                "reliability": rel,
                "reliabilityLabel": rel_label,
                "sources": sources,
                "citations": [s.get("reference", "") for s in sources],
                "requires_verification": (rel == "verify"),
                "confidence_status": conf_status,
                "evidence_status": "ANALYZED" if sources else "INSUFFICIENT_CASE_MATERIAL",
                "generation_time_sec": round(time.time() - t0, 3)
            }
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 3: LEGAL_QUERY (Existing RAG pipeline)
        rag_result = await asyncio.to_thread(
            pipeline.answer_question,
            question=req.content,
            act_filter=req.act_filter,
            section_filter=req.section_filter,
            effective_date=req.effective_date,
            top_k=5,
            max_new_tokens=512
        )

        full_answer = rag_result.get("answer", "")
        words = full_answer.split(" ")

        # Stream accumulated tokens to frontend
        current_text = ""
        for i, word in enumerate(words):
            current_text += (word if i == 0 else " " + word)
            token_payload = {"token": current_text}
            yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
            await asyncio.sleep(0.015)

        # Send completion event with full verified metadata
        rel, rel_label = map_reliability(rag_result)
        sources = format_sources(rag_result.get("retrieved_sources", []))

        complete_payload = {
            "id": f"msg-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": full_answer,
            "query_type": "LEGAL_QUERY",
            "type": "legal",
            "reliability": rel,
            "reliabilityLabel": rel_label,
            "sources": sources,
            "citations": rag_result.get("citations", []),
            "requires_verification": (rel == "verify"),
            "confidence_status": rag_result.get("confidence_status", ""),
            "evidence_status": rag_result.get("evidence_status", ""),
            "generation_time_sec": rag_result.get("generation_time_sec", 0.0)
        }
        yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/v1/ai/contextual")
async def ai_contextual(req: AIContextualRequest):
    """Contextual AI evaluation on selected text excerpt."""
    global pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="LegalAI RAG Pipeline is initializing")

    query = (
        f"{req.question}\n\nSelected Clause/Excerpt:\n\"{req.selectedText}\""
        if req.question and req.question.strip()
        else f"Provide legal analysis of the following statutory excerpt:\n\"{req.selectedText}\""
    )

    rag_result = await asyncio.to_thread(
        pipeline.answer_question,
        question=query,
        top_k=3,
        max_new_tokens=384
    )

    sources = format_sources(rag_result.get("retrieved_sources", []))

    return {
        "id": f"ctx-{int(time.time() * 1000)}",
        "role": "assistant",
        "timestamp": time.strftime("%I:%M %p"),
        "content": rag_result.get("answer", ""),
        "sources": sources
    }
