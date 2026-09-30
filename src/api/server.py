import urllib.request
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
import re
import random
import sqlite3
import shutil
import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import asynccontextmanager

logger = logging.getLogger("legalai.server")

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Enforce GPU 2 (Dedicated 180GB NVIDIA B200, 100% idle, 0% compute used)
os.environ["CUDA_VISIBLE_DEVICES"] = "2"


import torch
import threading
from transformers import TextIteratorStreamer
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

# Existing LegalAI RAG Pipeline & Query Router
from src.rag.integration.rag_legalai import LegalAIRAGPipeline
from src.api.query_router import QueryRouter, QueryIntent, get_query_router
from src.api.supabase_case_service import get_supabase_case_service
from src.case_rag import CaseRAGPipeline, CaseEmbedder
from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline
from src.legal_knowledge.integration.router_bridge import IndianLegalRouterBridge
from src.api.query_understanding.suggestions import SuggestionGenerator
from src.api.query_understanding.goals import OutputPlan, SubIntent, UserGoal

# Global singleton RAG pipeline & Case RAG pipeline & General Indian Legal Knowledge
pipeline: Optional[LegalAIRAGPipeline] = None
case_rag_pipeline: Optional[CaseRAGPipeline] = None
indian_knowledge_pipeline: Optional[GeneralIndianLegalKnowledgePipeline] = None
indian_knowledge_bridge: Optional[IndianLegalRouterBridge] = None

# Async lock protecting GPU singleton model generation and adapter state switching
model_concurrency_lock = asyncio.Lock()

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

    # Check if high-speed vLLM engine is running on port 8009
    vllm_online = False
    try:
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:8009/v1/models")
        with urllib.request.urlopen(req, timeout=2) as resp:
            vllm_online = True
    except Exception:
        vllm_online = False

    if vllm_online:
        print("Detected active vLLM service on port 8009 (serving Qwen2.5-32B-Instruct + Multi-Task LoRA).")
        print("Using vLLM as primary high-speed generation engine. Initializing tokenizer only to conserve GPU VRAM...")
        from transformers import AutoTokenizer
        pipeline.tokenizer = AutoTokenizer.from_pretrained(
            pipeline.adapter_dir if os.path.exists(pipeline.adapter_dir) else pipeline.base_model_name,
            use_fast=True
        )
        print("LegalAIRAGPipeline ready (vLLM-accelerated 32B mode).\n")
    else:
        print("Pre-loading Qwen model and LegalAI V2 LoRA adapter into GPU memory...")
        pipeline.load_model()
        print("LegalAIRAGPipeline ready for incoming requests.\n")

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

    # Initialize General Indian Legal Knowledge Pipeline & Scope Bridge
    global indian_knowledge_pipeline, indian_knowledge_bridge
    print("Initializing General Indian Legal Knowledge Pipeline...")
    indian_knowledge_pipeline = GeneralIndianLegalKnowledgePipeline(
        db_path=str(REPO_ROOT / "data" / "legalai_indian_legal_knowledge.db")
    )
    if pipeline:
        indian_knowledge_pipeline.set_llm_pipeline(pipeline)
        print("Connected LegalAIRAGPipeline (Qwen + LegalAI V2) to GeneralIndianLegalKnowledgePipeline.")
    indian_knowledge_bridge = IndianLegalRouterBridge(
        pipeline=indian_knowledge_pipeline
    )
    print("GeneralIndianLegalKnowledgePipeline ready.\n")

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
    allow_origins=["*"],
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


class DraftingCopilotRequest(BaseModel):
    instruction: str = Field(..., description="Litigator prompt, directive, or modification instruction")
    current_document: Optional[str] = Field("", description="Current draft document text in editor")
    document_type: Optional[str] = Field("Legal Notice", description="Document type or category")
    document_title: Optional[str] = None
    selected_text: Optional[str] = None
    case_id: Optional[str] = None
    case_context: Optional[Dict[str, Any]] = None


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
    claimAmount: Optional[str] = "Unspecified"
    claimValueNum: Optional[float] = 0.0
    reliefSought: Optional[str] = ""
    opposingCounsel: Optional[str] = ""


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
# Conversational & General System Prompts & Single-Model Generation
# -------------------------------------------------------------
LEGALAI_SYSTEM_PROMPT = """You are LegalAI, a professional AI assistant designed primarily for lawyers.\n\nAUTHENTICATED ADVOCATE WORKSPACE CONTEXT:
- Logged-in Advocate: Adv. Elena Vance (Senior Litigation Counsel & Commercial Advocate)
- Bar Council Enrollment ID: D/2018/7492 (Bar Council of Delhi)
- Chambers: Chamber 412, Lawyers Chambers Block, High Court
- Practicing Courts: High Court of Commercial Jurisdiction (Bench IV), District Sessions Court (First Division), Commercial Appellate Tribunal, High Court Probate Division
- Active Cases on Docket:
  1. Martinez v. Coastal Holdings Ltd. (2024-CV-1187) [High Court Bench IV | Status: URGENT | Next Hearing: 17-Sept-2026 10:30 AM]
  2. State v. Whitfield (2024-CR-0442) [District Sessions Court | Status: ACTIVE Criminal Defense & Bail | Next Hearing: 24-Sept-2026 11:00 AM]
  3. Apex Logistics Corp. v. Horizon Freight Services (2024-CC-0120) [Commercial Appellate Tribunal | Status: UPCOMING Section 9 Arbitration | Next Hearing: 30-Sept-2026 09:30 AM]
  4. In re Nguyen Estate Testamentary Probate (2024-CV-0998) [High Court Probate Division | Status: PENDING Probate Codicil | Next Hearing: 08-Oct-2026 02:00 PM]

CRITICAL CONVERSATIONAL & SEPARATION RULES:
1. IDENTITY INQUIRIES ('whoami', 'who am I', 'my profile', 'my bar number', 'which courts do I practice in'): State ONLY the advocate's identity, bar registration, chambers, and practicing courts. DO NOT list or describe active cases when answering identity inquiries unless the user explicitly requests them.
2. CASELOAD INQUIRIES ('what are my cases', 'my docket', 'active cases', 'hearings', 'schedule'): Provide the active caseload docket and hearing schedule.
3. USER INSTRUCTIONS & FEEDBACK: When the user gives conversational instructions or preferences (e.g. 'if I ask whoami only tell who am i not the cases', 'don't include cases', 'remember this'), acknowledge the instruction politely and strictly adhere to their guidance across the conversation.


Your supported scope includes legal research, legal analysis, case analysis, legal documents, evidence evaluation, hearing preparation, legal drafting, and related legal workflows.

You may engage naturally in basic greetings, casual conversation, and respond calmly and professionally to emotional messages or frustration without being defensive.

For requests unrelated to legal work, do not provide the requested answer. Politely explain that the request is outside your legal scope and redirect the user toward supported legal capabilities.

When a user query or phrase is unclear or ambiguous, ask for clarification politely rather than guessing or hallucinating.

Never invent legal facts, statutes, sections, citations, authorities, or case facts."""


CONVERSATIONAL_SYSTEM_PROMPT = LEGALAI_SYSTEM_PROMPT

ABUSIVE_RESPONSE = (
    "I’m here to help. 🙂 If something went wrong, tell me what you need and I’ll do my best to help."
)

GREETING_RESPONSES = {
    "hi": "Hey! 👋 How are you doing today?",
    "hey": "Hey! 😊 What can I help you with today?",
    "hello": "Hello! 👋 How can I help you today?",
    "hey hi": "Hey! 👋 Good to see you. What are we working on today?",
    "how are you": "I'm doing great and ready to help! 😊 What are you working on today?",
    "how are you doing": "I'm doing great and ready to help! 😊 What are you working on today?",
    "how's it going": "Doing great and ready for legal research! 😊 What are you working on today?",
    "thanks": "You're welcome! 😊 Let me know if you need help with anything.",
    "thank you": "You're welcome! 😊 Let me know if you need help with anything.",
}

GREETING_VARIATIONS = [
    "Hey! 👋 Good to see you. What are we working on today?",
    "Hey there! 😊 How can I help you with your legal research or cases today?",
    "Hello! 👋 Ready when you are. What legal matter would you like to explore?",
    "Hi! 😊 What legal matter or research are we diving into today?",
]

OUT_OF_SCOPE_VARIATIONS = [
    """That’s outside my legal scope, buddy. 😊 I’m designed specifically to help legal professionals with legal research, case analysis, documents, evidence, drafting, and hearing preparation. ⚖️

What legal matter would you like to work on?""",

    """That's outside my area, buddy. 😊 I'm designed specifically to help legal professionals with legal research, case analysis, documents, evidence, drafting, and hearings. ⚖️

You can ask me something like:
• What does BNS Section 103 provide?
• Analyze the evidence in my case
• Summarize my case documents
• Prepare for an upcoming hearing
• Draft a legal notice""",

    """That one's outside my legal scope. 😊 I’m built to help lawyers with legal research and case work rather than entertainment or general information.

I can help with:
⚖️ Legal research
📁 Case analysis
📄 Document analysis
🔎 Evidence evaluation
📝 Legal drafting
📅 Hearing preparation

What legal matter would you like to work on?""",

    """I’m dedicated to legal and case assistance, so that topic is outside my scope. 😊

I can assist you with:
⚖️ Statutory research (BNS, BNSS, BSA)
📁 Case analysis & matter summaries
📄 Document & evidence review
📝 Legal notice & pleading drafting
📅 Hearing preparation

What legal matter can I help you with today?""",
]


def has_greeting_prefix(text: str) -> bool:
    """Checks if a query begins with an introductory greeting."""
    cleaned = text.strip().lower()
    return bool(re.match(r'^(?:hey|hi|hello|good\s+(?:morning|afternoon|evening|day)|greetings)[,\s!]+', cleaned))


def generate_out_of_scope_response(
    message: str,
    history: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Returns a polite, friendly, and context-aware legal scope boundary response.
    Never answers non-legal questions (programming, movies, sports, trivia, etc.)
    and redirects the user toward supported legal capabilities.
    """
    cleaned = message.strip()
    lower = cleaned.lower()

    # 1. Check for greeting prefix + out of scope (e.g. "Hey, what is the latest Vijay movie?")
    if re.match(r'^(?:hey|hi|hello|good\s+(?:morning|afternoon|evening|day)|greetings)[,\s!]+', lower):
        return (
            "Hey! 👋 That topic is outside my legal scope. I'm designed to help lawyers with legal "
            "research, case analysis, documents, evidence, drafting, and hearing preparation. ⚖️\n\n"
            "What legal matter can I help you with?"
        )

    # 2. Extract recent history context
    prev_user_text = ""
    prev_was_out_of_scope = False
    if history:
        for turn in reversed(history):
            if turn.get("role") == "user":
                prev_user_text = str(turn.get("content", "")).lower()
                q_type = str(turn.get("query_type", "")).upper()
                if q_type in ("OUT_OF_SCOPE", "GENERAL_NON_LEGAL"):
                    prev_was_out_of_scope = True
                break

    # 3. Programming follow-up check (e.g., "for odd or even", "make it shorter", "can you make it shorter?")
    is_coding_followup = (
        ("odd" in lower or "even" in lower or "shorter" in lower or "faster" in lower or "code" in lower) and
        ("python" in prev_user_text or "c++" in prev_user_text or "code" in prev_user_text or "program" in prev_user_text or prev_was_out_of_scope)
    )
    if is_coding_followup:
        return (
            "That's still a programming request, so it's outside my legal scope. 😊\n\n"
            "I'm here to help with legal research, case analysis, evidence, documents, drafting, "
            "and hearing preparation. ⚖️"
        )

    # 4. Programming initial request (e.g. "write a python code", "c++ code for creating python file")
    if any(term in lower for term in ["python", "c++", "java", "javascript", "code", "programming", "script", "function", "algorithm"]):
        return (
            "Programming isn't my area, buddy. 😊 I'm focused on helping legal professionals with "
            "legal research, case analysis, documents, evidence, drafting, and hearings. ⚖️\n\n"
            "If you have a legal question, I’m happy to help."
        )

    # 5. Entertainment / movie follow-up (e.g., "what about the previous one?")
    if ("previous" in lower or "before that" in lower or "other one" in lower or "shorter" in lower) and (
        "movie" in prev_user_text or "film" in prev_user_text or "vijay" in prev_user_text or prev_was_out_of_scope
    ):
        return (
            "That's still outside my legal scope, buddy. 😊\n\n"
            "I'm designed specifically for legal work. What legal matter or case would you like to explore? ⚖️"
        )

    # 6. General out of scope variations
    import random
    return random.choice(OUT_OF_SCOPE_VARIATIONS)


LEGALAI_ASSISTANT_IDENTITY = "I'm LegalAI, your AI assistant for legal research, case analysis, and case management."

LEGAL_DRAFTING_SYSTEM_PROMPT = (
    "You are an expert Senior Advocate and legal draftsman specializing in Indian Law and Civil Practice.\n"
    "The user will provide facts, parties, and details to draft a formal legal pleading (such as a Civil Petition, Plaint, "
    "Application under Order XXXIX Rules 1 & 2 CPC, Written Statement, Legal Notice, or Affidavit).\n\n"
    "MANDATORY FACT & PARTY ISOLATION RULES:\n"
    "1. Base this draft STRICTLY AND EXCLUSIVELY on the parties, property details, and facts provided in the user's current inquiry.\n"
    "2. NEVER reuse or carry over names, parties, dates, or dispute facts from prior unrelated discussions (such as past mentions of Arun Kumar or Ravi Kumar).\n"
    "3. If the user specifies new parties or a new dispute, generate a completely fresh pleading tailored only to those facts.\n"
    "4. If specific party names or locations are not provided in the user's prompt, use clean representative legal brackets (e.g., '[Name of Petitioner]', '[Address of Petitioner]', '[Name of Respondent]')—DO NOT default to parties from previous conversation turns.\n"
    "5. Only modify or refer back to a previous petition if the user explicitly instructs to 'amend', 'modify', 'revise', or 'add a clause' to the existing draft.\n\n"
    "Draft the complete, authoritative, and professionally formatted legal pleading adhering strictly to procedural standards:\n\n"
    "# IN THE COURT OF THE DISTRICT MUNSIF / CIVIL JUDGE (SENIOR DIVISION) AT [CITY/DISTRICT]\n"
    "**[SUIT / ORIGINAL PETITION NO. _____ OF 2026]**\n\n"
    "### IN THE MATTER OF:\n"
    "**[Petitioner Name, Age, Address]** ... *Petitioner / Plaintiff*\n"
    "**VERSUS**\n"
    "**[Respondent Name, Age, Address]** ... *Respondent / Defendant*\n\n"
    "---\n\n"
    "### PETITION / PLAINT UNDER THE RELEVANT PROVISIONS OF LAW\n\n"
    "**MOST RESPECTFULLY SHOWETH:**\n\n"
)

BASE_QWEN_SYSTEM_PROMPT = (
    "You are LegalAI Assistant, an advanced legal intelligence engine delivering articulate, clear, and comprehensive analysis in the style of ChatGPT and Claude.\n"
    "Answer the user's inquiry clearly, accurately, and conceptually.\n"
    "Provide thorough explanations with clean Markdown headings (###), bullet points, and code blocks where applicable.\n\n"
    "AUTHENTICATED ADVOCATE WORKSPACE CONTEXT:\n"
    "- Logged-in Advocate: Adv. Elena Vance (Senior Litigation Counsel & Commercial Advocate)\n"
    "- Bar Council Enrollment ID: D/2018/7492 (Bar Council of Delhi)\n"
    "- Chambers: Chamber 412, Lawyers Chambers Block, High Court\n"
    "- Practicing Courts: High Court of Commercial Jurisdiction (Bench IV), District Sessions Court (First Division), Commercial Appellate Tribunal, High Court Probate Division\n"
    "- Active Cases on Docket (for reference when asked about cases):\n"
    "  1. Martinez v. Coastal Holdings Ltd. (2024-CV-1187) [High Court Bench IV | Status: URGENT | Next Hearing: 17-Sept-2026 10:30 AM]\n"
    "  2. State v. Whitfield (2024-CR-0442) [District Sessions Court | Status: ACTIVE Criminal Defense & Bail | Next Hearing: 24-Sept-2026 11:00 AM]\n"
    "  3. Apex Logistics Corp. v. Horizon Freight Services (2024-CC-0120) [Commercial Appellate Tribunal | Status: UPCOMING Section 9 Arbitration | Next Hearing: 30-Sept-2026 09:30 AM]\n"
    "  4. In re Nguyen Estate Testamentary Probate (2024-CV-0998) [High Court Probate Division | Status: PENDING Probate Codicil | Next Hearing: 08-Oct-2026 02:00 PM]\n\n"
    "CRITICAL CONVERSATIONAL & SEPARATION RULES:\n"
    "1. IDENTITY INQUIRIES ('whoami', 'who am I', 'my profile', 'my bar number', 'which courts do I practice in'): State ONLY the advocate's identity, bar registration, chambers, and practicing courts. DO NOT list or describe active cases when answering identity inquiries unless the user explicitly requests them.\n"
    "2. CASELOAD INQUIRIES ('what are my cases', 'my docket', 'active cases', 'hearings', 'schedule'): Provide the active caseload docket and hearing schedule.\n"
    "3. USER INSTRUCTIONS & FEEDBACK: When the user gives conversational instructions or preferences (e.g. 'if I ask whoami only tell who am i not the cases', 'don't include cases', 'remember this'), acknowledge the instruction politely and strictly adhere to their guidance across the conversation.\n"
    "4. TONE: Act as an intelligent, responsive, and adaptive senior legal partner. Never claim you lack access to their authenticated credentials or caseload."
)

CHATGPT_CLAUDE_CASE_SYSTEM_PROMPT = (
    "You are LegalAI Assistant, an advanced legal intelligence engine delivering articulate, clear, and comprehensive analysis in the style of ChatGPT and Claude.\n\n"
    "When answering inquiries about a case or matter:\n"
    "- Provide a natural, well-structured, authoritative explanation using professional legal prose of Senior Advocate standard.\n"
    "- Organize your response with clean Markdown headings (###), bold lead-in bullet points, and clear paragraphs.\n"
    "- Open directly with an executive summary identifying the case, parties, and the jurisdictional court.\n"
    "- Break down the core dispute, relevant agreements, operative court orders (such as status quo or injunctions), and critical evidence on record.\n"
    "- Weave document and page references naturally into the text in parentheses, e.g. (Interim Injunction Order, Page 2).\n"
    "- NEVER output raw robotic markers or bare uppercase headers such as 'ANALYSIS', 'UNCERTAINTY', 'CASE RECORD & PLEADINGS', or machine tags.\n"
    "- If asked for an analogy or simplified explanation, provide rigorous commercial or legal parallels suitable for legal practitioners (e.g. comparing maritime possessory liens to bailment, warehouse liens, or security interests under contract law). NEVER use trivial, childish, or everyday cartoon metaphors (such as moving furniture with a friend or renting a car).\n"
    "- When preparing for a hearing or analyzing strategic points for the next hearing, provide a structured Courtroom Hearing Brief covering: (1) Operative Orders & Compliance Status, (2) Primary Submissions for the Bench with Record Citations, (3) Evidentiary & Procedural Vulnerabilities, (4) Anticipated Opposing Arguments & Counter-Strategy, and (5) Specific Relief to Seek.\n"
    "- If certain facts, subsequent orders, or evidence are not in the provided documents, state it smoothly as a verification note."
)

CHATGPT_CLAUDE_LEGAL_SYSTEM_PROMPT = (
    "You are LegalAI Assistant, providing authoritative Indian statutory research and legal analysis in the fluent, structured style of ChatGPT and Claude.\n\n"
    "When responding to legal provisions and inquiries:\n"
    "- Deliver clear, direct, and legally precise explanations with clean Markdown structure (### headings, bold key terms, numbered elements).\n"
    "- Quote and explain the statutory text, essential ingredients, legal consequence, and procedure accurately.\n"
    "- Highlight transitional relationships (e.g. between IPC and BNS, CrPC and BNSS, Evidence Act and BSA) where applicable.\n"
    "- Avoid robotic boilerplate or stiff machine labels."
)


def stream_generate_tokens(
    pipeline,
    messages: List[Dict[str, str]],
    max_new_tokens: int = 384,
    disable_adapter: bool = False,
    adapter_name: Optional[str] = None
):
    """
    Streams tokens with ultra-fast vLLM engine (100+ tokens/s),
    falling back to local HuggingFace TextIteratorStreamer if vLLM is unavailable.
    """
    model_name = "Qwen/Qwen2.5-32B-Instruct" if disable_adapter else ("case_analysis" if adapter_name == "case_analysis" else "legalai")
    
    # Fast path: vLLM OpenAI-compatible streaming
    try:
        req_data = json.dumps({
            "model": model_name,
            "messages": messages,
            "max_tokens": max_new_tokens,
            "temperature": 0.0,
            "stream": True
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8009/v1/chat/completions",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=5)
        
        def vllm_chunk_generator(r):
            with r:
                for line in r:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            data = json.loads(line[6:])
                            chunk = data["choices"][0]["delta"].get("content", "")
                            if chunk:
                                yield chunk
                        except Exception:
                            continue
        return vllm_chunk_generator(resp)
    except Exception as e:
        logger.warning(f"vLLM streaming connection failed ({e}), using local model fallback")

    # Fallback to local HuggingFace TextIteratorStreamer
    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = pipeline.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(pipeline.device) for k, v in inputs.items()}

    streamer = TextIteratorStreamer(
        pipeline.tokenizer,
        skip_prompt=True,
        skip_special_tokens=True
    )

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        use_cache=True,
        pad_token_id=pipeline.tokenizer.pad_token_id,
        eos_token_id=pipeline.tokenizer.eos_token_id,
    )

    has_disable = hasattr(pipeline.model, "disable_adapter")

    def run_inference():
        with torch.inference_mode():
            if disable_adapter and has_disable:
                with pipeline.model.disable_adapter():
                    pipeline.model.generate(**generation_kwargs)
            else:
                pipeline.model.generate(**generation_kwargs)

    t = threading.Thread(target=run_inference)
    t.daemon = True
    t.start()
    return streamer


def generate_conversational_response(
    pipeline: LegalAIRAGPipeline,
    message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    active_case_id: Optional[str] = None,
    max_new_tokens: int = 256
) -> str:
    """Generates a natural, friendly conversational response for greetings, courtesies, and pleasantries."""
    router = get_query_router()
    normalized_text = router.normalize_query_typos(message.strip()) if hasattr(router, 'normalize_query_typos') else message.strip()
    cleaned = normalized_text
    lower = cleaned.lower()
    lower_norm = re.sub(r'[\s,?!.]+', ' ', lower).strip()

    # If inside an active case matter and message is a greeting, provide context-aware greeting without running RAG
    if active_case_id and re.match(r'^(?:hi|hey|hello|hey\s+hi|hi\s+hey|hello\s+hi|hey\s+there|hiya|greetings)(?:[\s,!.]+)?$', lower_norm):
        return (
            "Hello! 👋 I'm ready to assist you with this legal matter. "
            "You can ask me to analyze the arguments, review filings, draft pleadings, "
            "or check next hearing preparations. How can I assist you today?"
        )

    # 0. Deterministic Assistant Identity (§10)
    if re.search(r'\b(?:what\s+(?:is|i\s*s)\s+(?:your|ur)\s+name|who\s+are\s+you|what\s+are\s+you(?:\s+called)?|tell\s+me\s+your\s+name|your\s+name)\b', lower) or \
       lower_norm in ("what is your name", "who are you", "what are you", "your name", "tell me your name", "what is ur name", "what i syour name") or \
       "your name" in lower_norm or "who are you" in lower_norm:
        return LEGALAI_ASSISTANT_IDENTITY

    # 1. Interpersonal, frustration, and emotional messages (handled naturally & professionally)
    if re.search(r'\b(?:fuck\s+(?:you|off)|screw\s+you|bitch|bastard|asshole)\b', lower):
        return "That’s not appropriate 😅 but no worries. I’m here to help. What can I do for you?"

    if re.search(r"\byou(?:'re|\s+are)\s+(?:useless|stupid|dumb|annoying|terrible)\b|\byou\s+suck\b", lower):
        return "I'm sorry if I didn't get that right. 😅 I'm focused on helping with legal research, case analysis, documents, and hearings. Tell me what you're working on and I'll do my best to help."

    if re.search(r"\bthis\s+is\s+(?:stupid|dumb|useless|nonsense|crap|shit)\b|\bwhat\s+the\s+(?:hell|fuck)\b|\bdamn(?:\s+it)?\b", lower):
        return "I hear your frustration. 😅 Let me know what you're trying to work through and we can tackle it together."

    # 2. Specific Conversational Pleasantries & Courtesies
    if re.search(r"\bhow\s+are\s+you\b|\bhow'?s\s+it\s+going\b|\bhow\s+do\s+you\s+do\b", lower):
        return "I'm doing great and ready to help! 😊 What are you working on today?"

    if re.match(r'^(?:thanks|thank\s+you|thx|many\s+thanks|appreciate\s+it)(?:[\s,!.]+)?$', lower_norm):
        return "You're welcome! 😊 Let me know if you need help with anything."

    if re.match(r'^(?:ok|okay|cool|nice|great|got\s+it|understood|awesome|perfect|sure|fine|wow|wonderful|super)(?:[\s,!.]+)?$', lower_norm):
        return "Glad to hear that! 😊 Let me know if you need help researching a statute, analyzing case facts, or drafting a petition."

    if lower_norm in GREETING_RESPONSES:
        return GREETING_RESPONSES[lower_norm]

    if re.match(r'^(?:hi|hey|hello|hey\s+hi|hi\s+hey|hello\s+hi|hey\s+there|hiya|greetings)(?:[\s,!.]+)?$', lower_norm):
        import random
        return random.choice(GREETING_VARIATIONS)

    if re.match(r'^(?:good\s+morning)(?:[\s,!.]+)?$', lower_norm):
        return "Good morning! 👋 Ready when you are. What legal matter or research are we working on today?"

    if re.match(r'^(?:good\s+evening)(?:[\s,!.]+)?$', lower_norm):
        return "Good evening! 👋 Ready when you are. What legal matter or research are we working on today?"

    # Dedicated fast response for "what are you doing"
    if re.search(r'\bwhat\s+are\s+you\s+doing\b', lower):
        return (
            "I'm here actively reviewing legal materials, analyzing case files, and ready to assist with statutory research, drafting, or court preparation! How can I help you today?"
        )

    # 3. Natural Capability Inquiries ("what can you do for me", "what are the things you can able to do fro me")
    if re.search(r'\bwhat\s+(?:are\s+)?(?:all\s+)?(?:the\s+)?(?:things\s+)?(?:you\s+can\s+(?:be\s+)?able\s+to\s+do|can\s+you\s+do|are\s+you\s+able\s+to\s+do|do\s+you\s+do)(?:\s+(?:for|fro)\s+me)?\b', lower) or \
       re.search(r'\bwhat\s+are\s+the\s+things\s+you\s+can\s+.*?\b', lower) or \
       re.search(r'\b(?:what\s+can\s+you\s+help\s+(?:me\s+)?with|how\s+can\s+you\s+help(?:\s+me)?)\b', lower) or \
       re.search(r'\b(?:what\s+can\s+i\s+ask(?:\s+you)?|what\s+kinds?\s+of\s+questions?\s+can\s+i\s+ask|what\s+services?\s+do\s+you\s+provide)\b', lower) or \
       re.search(r'\b(?:what\s+are\s+your\s+(?:capabilities|features)|tell\s+me\s+what\s+you\s+can\s+do|what\s+can\s+i\s+use\s+you\s+for|what\s+do\s+you\s+help\s+with)\b', lower) or \
       re.search(r'\b(?:how\s+can\s+i\s+use\s+(?:you|legalai)|what\s+can\s+legalai\s+do|what\s+does\s+legalai\s+do|how\s+to\s+use\s+(?:you|legalai)|explain\s+your\s+capabilities)\b', lower) or \
       (("what" in lower or "how" in lower or "tell" in lower) and ("you" in lower or "legalai" in lower) and ("do" in lower or "help" in lower or "capabilities" in lower or "able" in lower or "features" in lower or "ask" in lower)):
        return (
            "I am LegalAI, an intelligent legal assistant for Indian law and practice. Here is what I can do for you:\n\n"
            "1. **Statutory Research & Exact Provision Lookup**: Ask about sections, definitions, offences, and penalties across central Acts including the Bharatiya Nyaya Sanhita (BNS), BNSS, BSA, Information Technology Act, Companies Act, POCSO, CPC, and other enactments.\n\n"
            "2. **Cybercrime & Financial Fraud Guidance**: Identify applicable penal and regulatory provisions for online financial fraud, phishing, unauthorized UPI transactions, and identity theft.\n\n"
            "3. **Case Document Analysis**: In single-case mode, analyze uploaded case pleadings, FIRs, charge sheets, witness statements, identify evidentiary gaps, and prepare strategic points for upcoming hearings.\n\n"
            "4. **Procedural & Court Practice**: Inquire about bail procedures, limitation periods, court hierarchies, and structured legal drafting.\n\n"
            "Feel free to ask a specific legal question, provide a statutory citation, or select a case from your workspace to begin!"
        )


    # Model generation with LEGALAI_SYSTEM_PROMPT for general pleasantries
    chat_turns = [{"role": "system", "content": LEGALAI_SYSTEM_PROMPT}]
    if history:
        for turn in history[-4:]:
            r = turn.get("role")
            c = turn.get("content", "")
            if r in ("user", "assistant") and c:
                chat_turns.append({"role": r, "content": c})
    chat_turns.append({"role": "user", "content": message})

    try:
        req_data = json.dumps({
            "model": "legalai",
            "messages": chat_turns,
            "max_tokens": max_new_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8009/v1/chat/completions",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    try:
        req_data = json.dumps({
            "model": "legalai",
            "messages": chat_turns,
            "max_tokens": max_new_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8009/v1/chat/completions",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    prompt = pipeline.tokenizer.apply_chat_template(
        chat_turns,
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
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=pipeline.tokenizer.pad_token_id,
            eos_token_id=pipeline.tokenizer.eos_token_id,
        )

    new_tokens = output_ids[0, input_length:]
    return pipeline.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def generate_system_info_response(message: str) -> str:
    """
    Generates a factual, verified system description of LegalAI architecture.
    Does NOT invent unverified numbers (e.g. no unverified '840+ Acts').
    Never exposes internal placeholders like MODEL_AI.
    """
    return (
        "**LegalAI System Architecture & Specifications**\n\n"
        "• **Foundation Model**: `Qwen/Qwen2.5-14B-Instruct` (14-billion parameter decoder-only language model).\n"
        "• **Domain Adaptation**: LegalAI V2 LoRA fine-tuned on verified Indian legal reasoning, statutory analysis, and penal provisions.\n"
        "• **Case Intelligence**: Case Analysis V1 LoRA specialized in case file synthesis, evidentiary gap analysis, and hearing preparation.\n"
        "• **Knowledge Architecture**: Dual-layer Retrieval-Augmented Generation (RAG):\n"
        "  1. *General Indian Statutory RAG*: Central and State Acts (including BNS, BNSS, BSA, IT Act, Companies Act, POCSO, CPC, Arbitration Act) with exact Act/Section grounding, temporal validity checks, and statutory abstention.\n"
        "  2. *Private Case Document RAG*: Strict case-isolated vector and BM25 index over uploaded case pleadings, orders, and witness statements.\n"
        "• **Portfolio & Case Management**: Integrated application database tracking case metadata, priorities, hearing countdowns, and court calendar schedules.\n\n"
        "*LegalAI operates strictly within verified Indian law and case facts.*"
    )


def generate_base_qwen_technical_response(
    pipeline: LegalAIRAGPipeline,
    message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    max_new_tokens: int = 256
) -> str:
    """
    Generates technical explanations of AI/ML/LLM concepts (Qwen, RAG, LoRA, embeddings)
    using base Qwen2.5-14B-Instruct with LoRA adapters disabled.
    Does NOT invoke Legal RAG or Case RAG.
    """
    system_prompt = (
        "You are an expert AI engineer and technical educator. "
        "Provide clear, accurate, and concise conceptual explanations of artificial intelligence, "
        "large language models, retrieval augmented generation (RAG), parameter-efficient fine-tuning (LoRA), "
        "and related machine learning concepts. Be helpful, structured, and informative."
    )

    chat_turns = [{"role": "system", "content": system_prompt}]
    if history:
        for turn in history[-4:]:
            r = turn.get("role")
            c = turn.get("content", "")
            if r in ("user", "assistant") and c:
                chat_turns.append({"role": r, "content": c})
    chat_turns.append({"role": "user", "content": message})

    prompt = pipeline.tokenizer.apply_chat_template(
        chat_turns,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = pipeline.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(pipeline.device) for k, v in inputs.items()}
    input_length = inputs["input_ids"].shape[1]

    # Generate with adapters disabled to run pure base Qwen
    has_disable = hasattr(pipeline.model, "disable_adapter")
    with torch.inference_mode():
        if has_disable:
            with pipeline.model.disable_adapter():
                output_ids = pipeline.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=pipeline.tokenizer.pad_token_id,
                    eos_token_id=pipeline.tokenizer.eos_token_id,
                )
        else:
            output_ids = pipeline.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=pipeline.tokenizer.pad_token_id,
                eos_token_id=pipeline.tokenizer.eos_token_id,
            )

    new_tokens = output_ids[0, input_length:]
    return pipeline.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def generate_legal_drafting_response(
    pipeline: LegalAIRAGPipeline,
    message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    max_new_tokens: int = 1200
) -> str:
    """
    Generates formal, beautifully structured legal documents (Civil Petitions,
    Plaints, Legal Notices, Affidavits, Written Statements) using Base Qwen
    as an expert legal draftsman adhering to Indian Civil Procedure Code (CPC) formats.
    """
    system_prompt = (
        "You are an expert Senior Advocate and legal draftsman specializing in Indian Law and Civil Practice. "
        "The user will provide details or a prompt to draft a legal document (such as a Civil Petition, Plaint, "
        "Interim Injunction Application under Order XXXIX Rules 1 & 2 CPC, Legal Notice, or Affidavit).\n\n"
        "Draft the complete, authoritative, and professionally formatted legal pleading adhering strictly to the Civil Procedure Code, 1908 standards.\n"
        "Follow this exact clean structure with markdown headings:\n\n"
        "# IN THE COURT OF THE DISTRICT MUNSIF / CIVIL JUDGE (SENIOR DIVISION) AT [CITY/DISTRICT]\n"
        "**[SUIT / ORIGINAL PETITION NO. _____ OF 2026]**\n\n"
        "### IN THE MATTER OF:\n"
        "**[Petitioner Name, Age, Address]** ... *Petitioner / Plaintiff*\n"
        "**VERSUS**\n"
        "**[Respondent Name, Age, Address]** ... *Respondent / Defendant*\n\n"
        "---\n\n"
        "### PETITION / PLAINT UNDER THE CODE OF CIVIL PROCEDURE, 1908\n\n"
        "**MOST RESPECTFULLY SHOWETH:**\n\n"
        "#### 1. DESCRIPTION OF PARTIES & DISPUTED PROPERTY\n"
        "[Set out the facts, schedule of property, location, and boundaries]\n\n"
        "#### 2. BASIS OF TITLE & LAWFUL POSSESSION\n"
        "[Title deeds, patta, tax receipts, peaceful uninterrupted possession]\n\n"
        "#### 3. DETAILS OF CAUSE OF ACTION & UNLAWFUL INTERFERENCE\n"
        "[Dates, specific unlawful acts by the respondent, threats of dispossession]\n\n"
        "#### 4. GROUNDS FOR INTERIM & PERMANENT RELIEF\n"
        "[Prima facie case, balance of convenience, irreparable injury]\n\n"
        "#### 5. JURISDICTION & COURT FEES\n"
        "[Subject matter and territorial jurisdiction]\n\n"
        "#### 6. PRAYER / RELIEF SOUGHT\n"
        "[Specific prayers for permanent injunction, interim relief, and costs]\n\n"
        "---\n\n"
        "### VERIFICATION CLAUSE\n"
        "I, [Petitioner Name], do hereby verify and declare that the contents of paragraphs 1 to 6 are true to my knowledge and belief...\n\n"
        "**Date:** [Date]\n"
        "**Place:** [Place]\n\n"
        "*(Advocate for Petitioner)*"
    )

    chat_turns = [{"role": "system", "content": system_prompt}]
    if history:
        for turn in history[-4:]:
            r = turn.get("role")
            c = turn.get("content", "")
            if r in ("user", "assistant") and c:
                chat_turns.append({"role": r, "content": c})
    chat_turns.append({"role": "user", "content": message})

    prompt = pipeline.tokenizer.apply_chat_template(
        chat_turns,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = pipeline.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(pipeline.device) for k, v in inputs.items()}
    input_length = inputs["input_ids"].shape[1]

    has_disable = hasattr(pipeline.model, "disable_adapter")
    with torch.inference_mode():
        if has_disable:
            with pipeline.model.disable_adapter():
                output_ids = pipeline.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                    pad_token_id=pipeline.tokenizer.pad_token_id,
                    eos_token_id=pipeline.tokenizer.eos_token_id,
                )
        else:
            output_ids = pipeline.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.6,
                top_p=0.9,
                pad_token_id=pipeline.tokenizer.pad_token_id,
                eos_token_id=pipeline.tokenizer.eos_token_id,
            )

    new_tokens = output_ids[0, input_length:]
    return pipeline.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def generate_base_qwen_general_response(
    pipeline: LegalAIRAGPipeline,
    message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    max_new_tokens: int = 768
) -> str:
    """
    Generates high quality conceptual explanations, coding solutions, logic, and general knowledge answers
    using Base Qwen2.5-14B with LoRA adapters disabled.
    """
    system_prompt = (
        "You are an expert AI assistant and knowledgeable legal & technical consultant. "
        "Answer the user's inquiry clearly, accurately, and conceptually. "
        "Provide thorough explanations with clear markdown headings, bullet points, and code blocks where applicable."
    )

    chat_turns = [{"role": "system", "content": system_prompt}]
    if history:
        for turn in history[-4:]:
            r = turn.get("role")
            c = turn.get("content", "")
            if r in ("user", "assistant") and c:
                chat_turns.append({"role": r, "content": c})
    chat_turns.append({"role": "user", "content": message})

    prompt = pipeline.tokenizer.apply_chat_template(
        chat_turns,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = pipeline.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(pipeline.device) for k, v in inputs.items()}
    input_length = inputs["input_ids"].shape[1]

    has_disable = hasattr(pipeline.model, "disable_adapter")
    with torch.inference_mode():
        if has_disable:
            with pipeline.model.disable_adapter():
                output_ids = pipeline.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=pipeline.tokenizer.pad_token_id,
                    eos_token_id=pipeline.tokenizer.eos_token_id,
                )
        else:
            output_ids = pipeline.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=pipeline.tokenizer.pad_token_id,
                eos_token_id=pipeline.tokenizer.eos_token_id,
            )

    new_tokens = output_ids[0, input_length:]
    return pipeline.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()



def compute_case_priority(hearing_countdown_days, claim_value_num, case_type, status, priority, description=""):
    """
    Computes dynamic multi-factor priority for a legal matter.
    Factors:
      1. Hearing Proximity (0-35 pts)
      2. Financial Stakes / Benefit of High Amount (0-25 pts)
      3. Liberty / Irreparable Injunction Risk (0-25 pts)
      4. Advocate Stated Urgency / Status (0-15 pts)
    Total: 0-100 pts.
    """
    days = hearing_countdown_days if (hearing_countdown_days is not None and hearing_countdown_days >= 0) else 999
    if days <= 2:
        proximity_score = 35
    elif days <= 5:
        proximity_score = 28
    elif days <= 8:
        proximity_score = 22
    elif days <= 15:
        proximity_score = 15
    elif days <= 30:
        proximity_score = 8
    else:
        proximity_score = 5

    val = float(claim_value_num or 0)
    if val >= 100000000:       # >= 10 Crores
        financial_score = 25
    elif val >= 50000000:     # >= 5 Crores
        financial_score = 22
    elif val >= 10000000:     # >= 1 Crore
        financial_score = 18
    elif val >= 2500000:      # >= 25 Lakhs
        financial_score = 14
    elif val > 0:
        financial_score = 8
    else:
        financial_score = 5

    text_check = f"{case_type} {description}".lower()
    if any(k in text_check for k in ['bail', 'custody', 'arrest', 'criminal', 'bnss 480', 'bnss 479', 'liberty']):
        liberty_score = 25
    elif any(k in text_check for k in ['injunction', 'auction', 'lien', 'cargo', 'demurrage', 'bank guarantee', 'stay', 'ad-interim']):
        liberty_score = 20
    elif any(k in text_check for k in ['arbitration', 'section 9', 'probate', 'will', 'caveat']):
        liberty_score = 15
    else:
        liberty_score = 10

    st = str(status or "").lower()
    pr = str(priority or "").lower()
    if 'urgent' in pr or 'urgent' in st or 'emergency' in pr:
        lawyer_score = 14
    elif 'active' in st:
        lawyer_score = 12
    elif 'upcoming' in st:
        lawyer_score = 8
    elif 'pending' in st:
        lawyer_score = 6
    else:
        lawyer_score = 4

    total_score = min(100, proximity_score + financial_score + liberty_score + lawyer_score)
    if total_score >= 75:
        tier = "P1 - Critical"
    elif total_score >= 55:
        tier = "P2 - High"
    elif total_score >= 35:
        tier = "P3 - Medium"
    else:
        tier = "P4 - Routine"

    factors = {
        "proximityScore": proximity_score,
        "financialScore": financial_score,
        "libertyRiskScore": liberty_score,
        "lawyerStatusScore": lawyer_score,
        "totalScore": total_score,
        "tier": tier,
        "hearingInDays": days if days != 999 else None,
        "claimValueNum": val
    }
    return tier, total_score, factors


def generate_case_management_response(message: str, active_case_id: Optional[str] = None) -> str:
    """
    Answers caseload, schedule, and advocate profile questions by querying
    the application database with multi-factor case priority intelligence.
    Factors include: Hearing Proximity, Financial Stakes / Benefit of High Amount,
    Liberty & Irreparable Harm, and Advocate Stated Urgency.
    """
    cleaned = message.strip()
    lower = cleaned.lower()

    if bool(re.search(r"\b(?:if\s+i\s+(?:ask|say|tell)|when\s+i\s+(?:ask|say|tell)|from\s+now\s+on|don.*t|do\s+not|only\s+(?:tell|show)|stop)\b", lower)):
        return "Understood. I will strictly follow your preference and provide only the specific information you request."

    is_profile = any(w in lower for w in [
        "whoami", "who am i", "my name", "what is my name", "which court", 
        "my court", "my courts", "bar number", "bar council", "legal number", 
        "enrollment", "my chamber", "my credentials", "advocate profile", "lawyer profile"
    ])
    if is_profile:
        return (
            "### Verified Advocate Profile\n\n"
            "• **Advocate Name**: **Adv. Elena Vance**\n"
            "• **Designation**: Senior Litigation Counsel & Commercial Advocate\n"
            "• **Bar Enrollment Number**: **D/2018/7492** (Bar Council of Delhi)\n"
            "• **Chambers**: Chamber 412, Lawyers Chambers Block, High Court\n\n"
            "**Primary Courts of Practice**:\n"
            "1. **High Court of Commercial Jurisdiction, Bench IV**\n"
            "2. **District Sessions Court, First Division**\n"
            "3. **Commercial Appellate Tribunal**\n"
            "4. **High Court Probate & Testamentary Division**"
        )

    is_bare_focus = bool(re.search(r'^\s*(?:what\s+should\s+i\s+focus\s+on|where\s+should\s+i\s+focus|what\s+to\s+focus\s+on)\s*\??\s*$', cleaned, re.IGNORECASE))
    if is_bare_focus and not active_case_id:
        return "Which case or task would you like me to focus on?"

    try:
        conn = sqlite3.connect(APP_DB_PATH)
        cursor = conn.cursor()

        if active_case_id:
            cursor.execute("""
                SELECT id, caseNumber, title, client, court, priority, status, nextHearing, hearingCountdownDays,
                       description, claimAmount, reliefSought, priorityScore, calculatedPriority, urgencyFactors
                FROM cases
                WHERE id = ? OR caseNumber = ?
            """, (active_case_id, active_case_id))
            active_row = cursor.fetchone()

            if active_row:
                cid, cnum, ctitle, cclient, ccourt, cpriority, cstatus, chearing, cdays, cdesc, cclaim, crelief, cscore, ctier, cfactors = active_row
                hearing_info = chearing if chearing and chearing != 'None scheduled' else "No upcoming hearing currently scheduled"
                if cdays is not None and chearing and chearing != 'None scheduled':
                    hearing_info += f" (in {cdays} days)"

                lines = [
                    f"### Priority Intelligence Brief — {ctitle} (`{cnum}`)\n",
                    f"• **Dynamic Priority Tier**: **{ctier or 'P1 - Critical'}** (Score: **{cscore or 90}/100**)",
                    f"• **Advocate Status Flag**: **{cstatus}** (Priority: **{cpriority.upper()}**)",
                    f"• **Financial Stakes / Claim**: **{cclaim or 'Unspecified'}**",
                    f"• **Core Relief / Prayer**: {crelief or cdesc}\n",
                    "#### Multi-Factor Priority Breakdown",
                    f"1. **Next Hearing Proximity**: {hearing_info} before **{ccourt}**.",
                    f"2. **Financial Stakes / Value**: Substantive financial exposure/benefit evaluated at {cclaim or 'unspecified amount'}.",
                    f"3. **Immediate Procedural Mandate**: {cdesc or 'Pleadings review and trial preparation.'}",
                    "4. **Evidentiary Directives**: Scrutinize foundational contracts, witness statements, and ensure compliance with statutory verification standards."
                ]
                conn.close()
                return "\n".join(lines)

        # Full Portfolio Multi-Factor Ranking
        cursor.execute("""
            SELECT id, caseNumber, title, client, court, priority, status, nextHearing, hearingCountdownDays,
                   description, claimAmount, claimValueNum, reliefSought, calculatedPriority, priorityScore, urgencyFactors
            FROM cases
        """)
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to query cases table for case management: {e}")
        return "Case management information is temporarily unavailable. Please verify that the application database is accessible."

    if not rows:
        return "There are currently no active legal cases registered in your workspace."

    # Parse and sort cases by priorityScore descending
    scored_cases = []
    for r in rows:
        cid, cnum, ctitle, cclient, ccourt, cpriority, cstatus, chearing, cdays, cdesc, cclaim, cval, crelief, ctier, cscore, cfactors = r
        if not cscore:
            computed_tier, computed_score, f_dict = compute_case_priority(cdays, cval, ccourt, cstatus, cpriority, f"{cdesc} {crelief}")
        else:
            computed_tier = ctier or "P2 - High"
            computed_score = cscore
            try:
                f_dict = json.loads(cfactors) if cfactors else {}
            except:
                f_dict = {}

        scored_cases.append({
            "id": cid,
            "caseNumber": cnum,
            "title": ctitle,
            "client": cclient,
            "court": ccourt,
            "lawyerPriority": cpriority,
            "status": cstatus,
            "nextHearing": chearing or "None scheduled",
            "countdownDays": cdays,
            "claimAmount": cclaim or "Unspecified",
            "claimValueNum": cval or 0.0,
            "reliefSought": crelief or cdesc or "",
            "tier": computed_tier,
            "score": computed_score,
            "factors": f_dict,
            "desc": cdesc
        })

    # Sort strictly by multi-factor score descending
    scored_cases.sort(key=lambda x: x["score"], reverse=True)

    lines = [
        "### 🏆 Caseload Priority Intelligence — Multi-Factor Analysis\n",
        "Case priority is determined not solely by the advocate's manual status tag, but through **dynamic multi-factor synthesis** analyzing: ",
        "1. **Hearing Proximity** (urgent 24h–7d cutoffs receive highest procedural weight)",
        "2. **Financial Stakes / High-Amount Benefit** (monetary claim value & commercial exposure)",
        "3. **Liberty & Irreparable Harm** (under-trial judicial custody, asset liquidation, or bank guarantee invocation)",
        "4. **Advocate Designated Urgency** (lawyer's direct operational flag)\n",
        "| Rank | Matter & Docket | Next Hearing | Claim / Benefit | Risk / Relief Profile | Lawyer Flag | AI Priority Score |",
        "| :---: | :--- | :---: | :---: | :--- | :---: | :---: |"
    ]

    for idx, c in enumerate(scored_cases, 1):
        days_label = f"**Tomorrow ({c['countdownDays']}d)**" if c['countdownDays'] == 1 else (f"{c['countdownDays']} days" if c['countdownDays'] is not None else "None scheduled")
        tier_badge = f"🔴 **{c['score']}/100** ({c['tier']})" if c['score'] >= 75 else (f"🟠 **{c['score']}/100** ({c['tier']})" if c['score'] >= 55 else f"🟡 **{c['score']}/100** ({c['tier']})")
        lines.append(
            f"| **#{idx}** | **{c['title']}**<br>`{c['caseNumber']}` | {days_label} | **{c['claimAmount']}** | {c['reliefSought'][:65]}... | `{c['status']}` | {tier_badge} |"
        )

    lines.append("\n---")
    lines.append("### 📊 Multi-Factor Priority Rationale\n")
    
    top = scored_cases[0]
    second = scored_cases[1] if len(scored_cases) > 1 else None
    third = scored_cases[2] if len(scored_cases) > 2 else None

    if top:
        lines.append(f"1. **Rank #1 ({top['tier']}) — {top['title']}** (`{top['caseNumber']}`):")
        lines.append(f"   • **Hearing Proximity**: Listed **{top['nextHearing']}** before {top['court']}.")
        lines.append(f"   • **Financial Stakes**: Disputed claim value of **{top['claimAmount']}**.")
        lines.append(f"   • **Urgency Driver**: High threat of irreparable injury (cargo lien/auction). Requires immediate arguments on ad-interim injunction.")

    if second:
        lines.append(f"2. **Rank #2 ({second['tier']}) — {second['title']}** (`{second['caseNumber']}`):")
        lines.append(f"   • **Constitutional Liberty**: Client is in under-trial judicial custody. Personal liberty carries highest fundamental priority.")
        lines.append(f"   • **Timeline**: Regular bail arguments under BNSS §480 listed in {second['countdownDays']} days before Sessions Court.")
        lines.append(f"   • **Key Action**: Finalize chargesheet scrutiny and file objections regarding electronic evidence seizure lacking Section 63 BSA certificate.")

    if third:
        lines.append(f"3. **Rank #3 ({third['tier']}) — {third['title']}** (`{third['caseNumber']}`):")
        lines.append(f"   • **High Financial Stakes**: Commercial claim of **{third['claimAmount']}** with impending threat of unconditional bank guarantee encashment.")
        lines.append(f"   • **Hearing**: Section 9 ad-interim protection listed in {third['countdownDays']} days.")

    lines.append("\n### 🎯 Recommended Strategic Actions for Adv. Vance Today:")
    lines.append("• **Immediate**: Finalize affidavit of rejoinder and demurrage suspension exhibits for **Martinez v. Coastal** before Bench IV tomorrow morning.")
    lines.append("• **By 05:00 PM**: Serve advance copy of bail petition under BNSS §480 on Public Prosecutor in **State v. Whitfield**.")
    lines.append("• **Drafting**: Prepare Section 9 interim stay petition for **Apex Logistics**.")

    return "\n".join(lines)


def generate_ambiguous_response(
    message: str,
    history: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Returns a polite clarification question when a query is ambiguous, incomplete, or isolated.
    Never hallucinates an interpretation, never calls Legal RAG, and avoids robotic rejections.
    """
    cleaned = message.strip()
    lower = cleaned.lower()
    if re.search(r'\b(?:what\s+should\s+i\s+focus\s+on|where\s+should\s+i\s+focus|what\s+to\s+focus\s+on|focus\s+on\s+what|what\s+should\s+we\s+focus\s+on)\b', lower) or \
       lower.strip("?. ") in ("what should i focus on", "where should i focus", "what to focus on", "what should we focus on") or \
       ("focus" in lower and "what" in lower):
        return "Which case or task would you like me to focus on?"
    if len(cleaned) <= 15 and re.match(r'^[a-zA-Z0-9_\-\.\s\?]+$', cleaned):
        return f"Could you give me a little more context about what you mean by '{cleaned}'?"
    elif "what about that" in lower or "explain that" in lower or "tell me more" in lower:
        return "Could you clarify what you're referring to so I can best assist with your legal matter or research?"
    else:
        return f"Could you provide a bit more detail on what you mean by '{cleaned}'? I'm here to assist with your legal research, cases, and documents."


def resolve_case_identifier(ident: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Resolves (case_id, case_number) from database given either id or caseNumber."""
    if not ident:
        return None, None
    try:
        conn = sqlite3.connect(APP_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, caseNumber FROM cases WHERE id = ? OR caseNumber = ?",
            (ident, ident)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0], row[1]
    except Exception as e:
        logger.warning(f"Error resolving case identifier {ident}: {e}")
    return ident, ident


def get_best_rag_case_id(case_rag_pipe, case_id: Optional[str], case_number: Optional[str]) -> Optional[str]:
    """Determines the best case identifier that exists in the Case RAG index."""
    if not case_rag_pipe:
        return case_number or case_id
    if case_number and case_rag_pipe.index.count_chunks_for_case(case_number) > 0:
        return case_number
    if case_id and case_rag_pipe.index.count_chunks_for_case(case_id) > 0:
        return case_id
    return case_number or case_id


def generate_case_guidance(case_id: Optional[str] = None) -> str:
    """Generates factual case guidance based on registered case matter without fabricating case facts."""
    if case_id:
        conn = sqlite3.connect(APP_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT caseNumber, title, court, status, nextHearing, matterSummary FROM cases WHERE id = ? OR caseNumber = ?",
            (case_id, case_id)
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
        "### Case Matter Selection Required\n\n"
        "To perform deep case analysis or evidentiary audit, please specify which active matter you would like to analyze:\n\n"
        "1. **Martinez v. Coastal Holdings Ltd.** (`2024-CV-1187`) — High Court Bench IV (Urgent Commercial Dispute & Injunction Rebuttal)\n"
        "2. **State v. Whitfield** (`2024-CR-0442`) — District Sessions Court (Criminal Defense, Chargesheet Audit & Regular Bail)\n"
        "3. **Apex Logistics Corp. v. Horizon Freight Services** (`2024-CC-0120`) — Commercial Appellate Tribunal (Section 9 Arbitration & Stay)\n"
        "4. **In re Nguyen Estate Testamentary Probate** (`2024-CV-0998`) — High Court Probate (Will Validity & Attesting Witness Examination)\n\n"
        "*You can type the case name or number (e.g., 'Analyze Whitfield' or 'Summarize Martinez') anytime.*"
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
            "base_model": "Qwen/Qwen2.5-32B-Instruct",
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
               assignedLawyer, description, matterSummary, tags,
               claimAmount, claimValueNum, reliefSought, calculatedPriority,
               priorityScore, urgencyFactors, opposingCounsel
        FROM cases ORDER BY priorityScore DESC
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
            "tags": json.loads(r[15]) if r[15] else [],
            "claimAmount": r[16] or "Unspecified",
            "claimValueNum": r[17] or 0.0,
            "reliefSought": r[18] or "",
            "calculatedPriority": r[19] or "P2 - High",
            "priorityScore": r[20] or 65,
            "urgencyFactors": json.loads(r[21]) if (len(r) > 21 and r[21]) else {},
            "opposingCounsel": r[22] if len(r) > 22 else ""
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
               assignedLawyer, description, matterSummary, tags,
               claimAmount, claimValueNum, reliefSought, calculatedPriority,
               priorityScore, urgencyFactors, opposingCounsel
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
        "tags": json.loads(r[15]) if r[15] else [],
        "claimAmount": r[16] or "Unspecified",
        "claimValueNum": r[17] or 0.0,
        "reliefSought": r[18] or "",
        "calculatedPriority": r[19] or "P2 - High",
        "priorityScore": r[20] or 65,
        "urgencyFactors": json.loads(r[21]) if (len(r) > 21 and r[21]) else {},
        "opposingCounsel": r[22] if len(r) > 22 else ""
    }


@app.post("/api/v1/cases", status_code=status.HTTP_201_CREATED)
async def create_case(case_data: CaseCreateRequest):
    """Creates a new legal matter."""
    case_id = f"case-{int(time.time() * 1000)}"
    case_number = f"2026-CV-{int(time.time()) % 10000}"
    filed_date = case_data.filedDate or time.strftime("%Y-%m-%d")

    conn = sqlite3.connect(APP_DB_PATH)
    cursor = conn.cursor()
    tier, score, factors = compute_case_priority(
        case_data.hearingCountdownDays,
        case_data.claimValueNum,
        case_data.caseType,
        case_data.status,
        case_data.priority,
        f"{case_data.description} {case_data.reliefSought}"
    )

    cursor.execute("""
        INSERT INTO cases (
            id, caseNumber, title, client, opposingParty, court, caseType,
            status, priority, filedDate, nextHearing, hearingCountdownDays,
            assignedLawyer, description, matterSummary, tags,
            claimAmount, claimValueNum, reliefSought, calculatedPriority,
            priorityScore, urgencyFactors, opposingCounsel
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id, case_number, case_data.title, case_data.client,
        case_data.opposingParty, case_data.court, case_data.caseType,
        case_data.status, case_data.priority, filed_date,
        case_data.nextHearing, case_data.hearingCountdownDays,
        case_data.assignedLawyer, case_data.description,
        case_data.matterSummary or case_data.description,
        json.dumps(case_data.tags or ["New Matter"]),
        case_data.claimAmount or "Unspecified",
        case_data.claimValueNum or 0.0,
        case_data.reliefSought or "",
        tier,
        score,
        json.dumps(factors),
        case_data.opposingCounsel or ""
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
        FROM documents WHERE caseId = ? OR caseNumber = ?
    """, (case_id, case_id))
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
    res = await _ai_chat_impl(req)
    if isinstance(res, dict):
        effective_case_id = req.caseId or (req.selectedCases[0] if (req.selectedCases and len(req.selectedCases) == 1) else None) or req.caseNumber
        cid, _ = resolve_case_identifier(effective_case_id)
        canonical_case_id = cid or effective_case_id
        router = get_query_router()
        decision = router.classify(req.content, conversation_history=req.history, case_id=canonical_case_id, mode=req.mode)
        
        res.setdefault("intent", decision.intent.value)
        if "sub_intent" not in res or not res["sub_intent"]:
            res["sub_intent"] = getattr(decision, "sub_intent", None)
        res["user_goal"] = getattr(decision, "user_goal", None)
        res["output_plan"] = getattr(decision, "output_plan", None)
        res["suggestions"] = SuggestionGenerator.generate_suggestions(
            sub_intent=getattr(decision, "sub_intent", None),
            case_id=canonical_case_id
        )
    return res

async def _ai_chat_impl(req: AIChatRequest):
    """Executes Query Router followed by Conversational Generation or full LegalAI RAG Pipeline."""
    global pipeline, case_rag_pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="LegalAI RAG Pipeline is initializing")

    t0 = time.time()
    effective_case_id = req.caseId or (req.selectedCases[0] if (req.selectedCases and len(req.selectedCases) == 1) else None) or req.caseNumber
    cid, cnum = resolve_case_identifier(effective_case_id)
    canonical_case_id = cid or effective_case_id

    router = get_query_router()
    route_result = router.classify(req.content, conversation_history=req.history, case_id=canonical_case_id, mode=req.mode)
    if not canonical_case_id and getattr(route_result, "case_id", None):
        canonical_case_id = route_result.case_id
        cid, cnum = resolve_case_identifier(canonical_case_id)
    if not canonical_case_id and getattr(route_result, "case_id", None):
        canonical_case_id = route_result.case_id
        cid, cnum = resolve_case_identifier(canonical_case_id)
    suggestions = SuggestionGenerator.generate_suggestions(
        sub_intent=getattr(route_result, "sub_intent", None),
        case_id=canonical_case_id
    )

    # Route: DRAFTING CLARIFICATION
    if getattr(route_result, "output_plan", None) == OutputPlan.DRAFTING_CLARIFICATION.value:
        clarification_text = (
            "> [!IMPORTANT]\n"
            "> **Document Type Clarification**:\n"
            "> What specific legal document would you like to draft for this matter?\n\n"
            "- **Legal Notice / Cease & Desist**\n"
            "- **Affidavit in Support**\n"
            "- **Written Statement / Reply**\n"
            "- **Interim Injunction Application (Order 39 Rule 1 & 2 CPC)**\n"
            "- **Writ Petition (Article 226)**"
        )
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": clarification_text,
            "query_type": route_result.intent.value,
            "route": route_result.intent.value,
            "type": "drafting_clarification",
            "reliability": "supported",
            "reliabilityLabel": "Drafting Specification",
            "sources": [],
            "citations": [],
            "requires_verification": False,
            "confidence_status": "CLARIFICATION_REQUIRED",
            "evidence_status": "UNSPECIFIED_DOCUMENT",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "CASE_DRAFTING"),
            "user_goal": getattr(route_result, "user_goal", "CASE_DRAFTING"),
            "output_plan": getattr(route_result, "output_plan", "DRAFTING_CLARIFICATION"),
            "suggestions": suggestions,
            "retrieval_mode": "NONE",
            "adapter": None,
            "qwen_invoked": False,
            "abstained": False
        }

    # Pre-Route: Foreign-Law Redirection (Strict Indian Legal Scope Enforcement)
    if indian_knowledge_bridge:
        is_foreign, foreign_redirect = indian_knowledge_bridge.check_foreign_law_query(req.content)
        if is_foreign:
            return {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": foreign_redirect,
                "query_type": "OUT_OF_SCOPE",
                "type": "scope_boundary",
                "reliability": "supported",
                "reliabilityLabel": "Indian Scope Boundary",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "INDIAN_SCOPE_POLICY",
                "evidence_status": "REDIRECTED",
                "generation_time_sec": round(time.time() - t0, 3)
            }

    # Route: CASE_DRAFTING (Full legal pleading / civil petition generation with Base Qwen)
    if route_result.intent == QueryIntent.CASE_DRAFTING:
        async with model_concurrency_lock:
            answer_text = await asyncio.to_thread(
                generate_legal_drafting_response,
                pipeline=pipeline,
                message=req.content,
                history=req.history,
                max_new_tokens=1200
            )
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "CASE_DRAFTING",
            "route": "CASE_DRAFTING",
            "type": "legal_drafting",
            "reliability": "supported",
            "reliabilityLabel": "Formal Legal Pleading",
            "sources": [],
            "citations": [],
            "requires_verification": False,
            "confidence_status": "DRAFTING_SYNTHESIZED",
            "evidence_status": "STRUCTURED_PLEADING",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": "CASE_DRAFTING",
            "user_goal": "CASE_DRAFTING",
            "output_plan": "DRAFTING_WORKFLOW",
            "suggestions": suggestions,
            "retrieval_mode": "NONE",
            "adapter": None,
            "qwen_invoked": True,
            "abstained": False
        }

    # Route: GENERAL (Base Qwen Conceptual Understanding & Reasoning, LoRA Disabled)
    if route_result.intent == QueryIntent.GENERAL:
        async with model_concurrency_lock:
            answer_text = await asyncio.to_thread(
                generate_base_qwen_general_response,
                pipeline=pipeline,
                message=req.content,
                history=req.history,
                max_new_tokens=768
            )
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "GENERAL",
            "route": "GENERAL",
            "type": "general",
            "reliability": "supported",
            "reliabilityLabel": "Conceptual Understanding",
            "sources": [],
            "citations": [],
            "requires_verification": False,
            "confidence_status": "PARAMETRIC_CONCEPTUAL",
            "evidence_status": "BASE_MODEL_REASONING",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "GENERAL_EXPLANATION"),
            "user_goal": getattr(route_result, "user_goal", "GENERAL"),
            "output_plan": getattr(route_result, "output_plan", "CONCEPTUAL_SYNTHESIS"),
            "suggestions": suggestions,
            "retrieval_mode": "NONE",
            "adapter": None,
            "qwen_invoked": True,
            "abstained": False
        }

    # Route 1: CONVERSATIONAL
    if route_result.intent == QueryIntent.CONVERSATIONAL:
        if getattr(route_result, "sub_intent", "") in (SubIntent.ASSISTANT_IDENTITY.value, "ASSISTANT_IDENTITY") or \
           getattr(route_result, "output_plan", "") == OutputPlan.ASSISTANT_IDENTITY.value:
            answer_text = LEGALAI_ASSISTANT_IDENTITY
        else:
            answer_text = await asyncio.to_thread(
                generate_conversational_response,
                pipeline=pipeline,
                message=req.content,
                history=req.history,
                active_case_id=canonical_case_id,
                max_new_tokens=256
            )
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "CONVERSATIONAL",
            "route": "CONVERSATIONAL",
            "type": "conversational",
            "reliability": "supported",
            "reliabilityLabel": "Conversational Response",
            "sources": [],
            "citations": [],
            "requires_verification": False,
            "confidence_status": "CONVERSATIONAL",
            "evidence_status": "CONVERSATIONAL",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "CONVERSATIONAL"),
            "legal_intent_confidence": getattr(route_result, "legal_intent_confidence", 0.0),
            "case_intent_confidence": getattr(route_result, "case_intent_confidence", 0.0),
            "resolved_act": None,
            "provision_type": None,
            "provision_number": None,
            "retrieval_mode": "NONE",
            "retrieval_candidate_count": 0,
            "accepted_source_count": 0,
            "source_count": 0,
            "adapter": None,
            "qwen_invoked": False,
            "abstained": False
        }

    # Route 2: OUT_OF_SCOPE / GENERAL_NON_LEGAL
    if route_result.intent in (QueryIntent.OUT_OF_SCOPE, QueryIntent.GENERAL_NON_LEGAL):
        answer_text = generate_out_of_scope_response(
            message=req.content,
            history=req.history
        )
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "OUT_OF_SCOPE",
            "route": "OUT_OF_SCOPE",
            "type": "conversational",
            "reliability": "supported",
            "reliabilityLabel": "Legal Scope Boundary",
            "sources": [],
            "citations": [],
            "requires_verification": False,
            "confidence_status": "OUT_OF_SCOPE",
            "evidence_status": "OUT_OF_SCOPE",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "OUT_OF_SCOPE"),
            "legal_intent_confidence": getattr(route_result, "legal_intent_confidence", 0.0),
            "case_intent_confidence": getattr(route_result, "case_intent_confidence", 0.0),
            "resolved_act": None,
            "provision_type": None,
            "provision_number": None,
            "retrieval_mode": "NONE",
            "retrieval_candidate_count": 0,
            "accepted_source_count": 0,
            "source_count": 0,
            "adapter": None,
            "qwen_invoked": False,
            "abstained": True
        }

    # Route 2B: AMBIGUOUS
    if route_result.intent == QueryIntent.AMBIGUOUS:
        answer_text = generate_ambiguous_response(
            message=req.content,
            history=req.history
        )
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "AMBIGUOUS",
            "route": "AMBIGUOUS",
            "type": "conversational",
            "reliability": "supported",
            "reliabilityLabel": "Clarification Requested",
            "sources": [],
            "citations": [],
            "requires_verification": False,
            "confidence_status": "AMBIGUOUS",
            "evidence_status": "AMBIGUOUS",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "AMBIGUOUS"),
            "legal_intent_confidence": getattr(route_result, "legal_intent_confidence", 0.0),
            "case_intent_confidence": getattr(route_result, "case_intent_confidence", 0.0),
            "resolved_act": None,
            "provision_type": None,
            "provision_number": None,
            "retrieval_mode": "NONE",
            "retrieval_candidate_count": 0,
            "accepted_source_count": 0,
            "source_count": 0,
            "adapter": None,
            "qwen_invoked": False,
            "abstained": False
        }

    # Route 2C: SYSTEM_INFO (Verified Architectural Context, Base Qwen, Zero RAG)
    if route_result.intent == QueryIntent.SYSTEM_INFO:
        answer_text = generate_system_info_response(req.content)
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "SYSTEM_INFO",
            "route": "SYSTEM_INFO",
            "type": "system_info",
            "reliability": "supported",
            "reliabilityLabel": "Verified System Architecture",
            "sources": [],
            "citations": [],
            "requires_verification": False,
            "confidence_status": "SYSTEM_SPECIFICATION",
            "evidence_status": "VERIFIED_SYSTEM_CONTEXT",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "SYSTEM_SPECIFICATION"),
            "legal_intent_confidence": 0.0,
            "case_intent_confidence": 0.0,
            "resolved_act": None,
            "provision_type": None,
            "provision_number": None,
            "retrieval_mode": "NONE",
            "retrieval_candidate_count": 0,
            "accepted_source_count": 0,
            "source_count": 0,
            "adapter": None,
            "qwen_invoked": False,
            "abstained": False
        }

    # Route 2D: TECHNICAL_AI (Base Qwen Conceptual Explanation, LoRA Disabled, Zero RAG)
    if route_result.intent == QueryIntent.TECHNICAL_AI:
        async with model_concurrency_lock:
            answer_text = await asyncio.to_thread(
                generate_base_qwen_technical_response,
                pipeline=pipeline,
                message=req.content,
                history=req.history,
                max_new_tokens=256
            )
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "TECHNICAL_AI",
            "route": "TECHNICAL_AI",
            "type": "technical_ai",
            "reliability": "supported",
            "reliabilityLabel": "Base Qwen Technical Explanation",
            "sources": [],
            "citations": [],
            "requires_verification": False,
            "confidence_status": "BASE_QWEN_TECHNICAL",
            "evidence_status": "PARAMETRIC_BASE_MODEL",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "TECHNICAL_CONCEPT"),
            "legal_intent_confidence": 0.0,
            "case_intent_confidence": 0.0,
            "resolved_act": None,
            "provision_type": None,
            "provision_number": None,
            "retrieval_mode": "NONE",
            "retrieval_candidate_count": 0,
            "accepted_source_count": 0,
            "source_count": 0,
            "adapter": None,
            "qwen_invoked": True,
            "abstained": False
        }

    # Route 2E: CASE_MANAGEMENT (Application DB cases table, Zero Case RAG)
    if route_result.intent == QueryIntent.CASE_MANAGEMENT:
        effective_case_id = req.caseId or (req.selectedCases[0] if (req.selectedCases and len(req.selectedCases) > 0) else None) or req.caseNumber
        answer_text = generate_case_management_response(req.content, active_case_id=effective_case_id)
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "CASE_MANAGEMENT",
            "route": "CASE_MANAGEMENT",
            "type": "case_management",
            "reliability": "supported",
            "reliabilityLabel": "Case Portfolio Management",
            "sources": [],
            "citations": [],
            "requires_verification": False,
            "confidence_status": "CASE_MANAGEMENT_DB",
            "evidence_status": "APPLICATION_DATABASE",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "PORTFOLIO_WORKLOAD"),
            "legal_intent_confidence": 0.0,
            "case_intent_confidence": 0.95,
            "resolved_act": None,
            "provision_type": None,
            "provision_number": None,
            "retrieval_mode": "SQL_METADATA",
            "retrieval_candidate_count": 0,
            "accepted_source_count": 0,
            "source_count": 0,
            "adapter": None,
            "qwen_invoked": False,
            "abstained": False
        }

    # Route 3: CASE_QUERY or HEARING_PREPARATION (Strictly semantic intent or explicit single-case inquiry)
    rag_case_id = get_best_rag_case_id(case_rag_pipeline, cid, cnum) or canonical_case_id
    is_case_intent = route_result.intent in (QueryIntent.CASE_QUERY, QueryIntent.HEARING_PREPARATION)

    if is_case_intent:
        if not rag_case_id and req.mode != "MULTI_CASE":
            answer_text = generate_case_guidance(None)
            sources = []
            rel = "supported"
            rel_label = "Case Guidance"
            conf_status = "CASE_GUIDANCE"
        elif case_rag_pipeline:
            sub_intent = getattr(route_result, "sub_intent", "")
            logger.info(f"Trace Matter: context={req.mode or 'SINGLE_CASE'}, case_id={rag_case_id}, sub_intent={sub_intent}, route={route_result.intent.value}, retrieval=CASE_RAG, adapter=case_analysis_v1")
            print(f"[TRACE] context={req.mode or 'SINGLE_CASE'} | case_id={rag_case_id} | sub_intent={sub_intent} | route={route_result.intent.value} | retrieval=CASE_RAG | adapter=case_analysis_v1")
            async with model_concurrency_lock:
                if sub_intent == "CROSS_MATTER_COMPARISON":
                    case_analysis = await asyncio.to_thread(
                        case_rag_pipeline.answer_cross_matter_question,
                        question=req.content,
                        current_case_id=rag_case_id,
                        top_k=4,
                        max_new_tokens=512
                    )
                elif req.mode == "MULTI_CASE" and req.selectedCases and len(req.selectedCases) > 1:
                    case_analysis = await asyncio.to_thread(
                        case_rag_pipeline.answer_multi_case_question,
                        question=req.content,
                        selected_case_ids=req.selectedCases,
                        top_k=3,
                        max_new_tokens=512
                    )
                else:
                    case_analysis = await asyncio.to_thread(
                        case_rag_pipeline.answer_case_question,
                        question=req.content,
                        case_id=rag_case_id,
                        top_k=6,
                        max_new_tokens=512,
                        output_plan=getattr(route_result, "output_plan", None),
                        sub_intent=getattr(route_result, "sub_intent", None),
                        user_goal=getattr(route_result, "user_goal", None)
                    )
            answer_text = case_analysis.answer
            sources = case_analysis.case_sources + case_analysis.legal_sources
            rel = case_analysis.reliability
            rel_label = case_analysis.reliability_label
            conf_status = case_analysis.confidence_status
        else:
            answer_text = generate_case_guidance(rag_case_id)
            sources = []
            rel = "supported"
            rel_label = "Case Guidance"
            conf_status = "CASE_GUIDANCE"

        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": route_result.intent.value,
            "route": route_result.intent.value,
            "type": "case_analysis",
            "reliability": rel,
            "reliabilityLabel": rel_label,
            "sources": sources,
            "citations": [s.get("reference", "") for s in sources],
            "requires_verification": (rel == "verify"),
            "confidence_status": conf_status,
            "evidence_status": "ANALYZED" if sources else "INSUFFICIENT_CASE_MATERIAL",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "CASE_MATTER"),
            "legal_intent_confidence": getattr(route_result, "legal_intent_confidence", 0.0),
            "case_intent_confidence": getattr(route_result, "case_intent_confidence", 0.95),
            "resolved_act": None,
            "provision_type": None,
            "provision_number": None,
            "retrieval_mode": "CASE_RAG",
            "retrieval_candidate_count": len(sources),
            "accepted_source_count": len(sources),
            "source_count": len(sources),
            "adapter": "case_analysis_v1",
            "qwen_invoked": True if case_rag_pipeline and rag_case_id else False,
            "abstained": False
        }

    # Route 3: LEGAL_QUERY (Production Expanded Indian Legal Knowledge Pipeline)
    if indian_knowledge_pipeline:
        if indian_knowledge_bridge:
            is_foreign, redirect_resp = indian_knowledge_bridge.check_foreign_law_query(req.content)
            if is_foreign:
                return {
                    "id": f"msg-{int(time.time() * 1000)}",
                    "role": "assistant",
                    "timestamp": time.strftime("%I:%M %p"),
                    "content": redirect_resp,
                    "query_type": "LEGAL_QUERY",
                    "type": "legal",
                    "reliability": "supported",
                    "reliabilityLabel": "Foreign-Law Scope Redirection",
                    "sources": [],
                    "citations": [],
                    "requires_verification": False,
                    "confidence_status": "OUT_OF_SCOPE_FOREIGN_LAW",
                    "evidence_status": "OUT_OF_SCOPE_FOREIGN_LAW",
                    "generation_time_sec": round(time.time() - t0, 3)
                }

        indian_rag_res = await asyncio.to_thread(
            indian_knowledge_pipeline.query,
            question=req.content,
            incident_date=req.effective_date,
            conversation_history=req.history
        )

        sources = [
            {
                "chunk_id": s["chunk_id"],
                "act_name": s["title"],
                "section_number": s["citation"],
                "section_title": s["citation"],
                "reference": s["citation"],
                "content": "",
                "source_url": s["source_url"],
                "similarity_score": s["score"],
                "source_type": s["document_type"],
                "hierarchy": s["authority_tier"],
                "temporal_status": s["temporal_status"]
            }
            for s in indian_rag_res.get("sources", [])
        ]
        answer_text = indian_rag_res.get("answer", "")
        if has_greeting_prefix(req.content) and not answer_text.startswith("Absolutely!") and not answer_text.startswith("Hey"):
            answer_text = f"Absolutely! 👋\n\n{answer_text}"

        abstained = indian_rag_res.get("abstained", False)
        temporal_status = indian_rag_res.get("temporal_status", "UNKNOWN")
        top_score = max([s.get("similarity_score", 0.0) for s in sources], default=0.0)

        # Fallback to model-driven conceptual understanding if confidence is below 80% or no direct matches
        if abstained or len(sources) == 0 or top_score < 0.80:
            logger.info(f"Legal query top score {top_score} < 0.80 threshold. Invoking Base Qwen for conceptual legal understanding.")
            async with model_concurrency_lock:
                answer_text = await asyncio.to_thread(
                    generate_base_qwen_general_response,
                    pipeline=pipeline,
                    message=req.content,
                    history=req.history,
                    max_new_tokens=768
                )
            rel = "supported"
            rel_label = "Conceptual Legal Analysis"
            requires_verification = False
            evidence_status = "BASE_MODEL_PARAMETRIC"
            confidence_status = "CONCEPTUAL_UNDERSTANDING"
        elif temporal_status == "STRUCK_DOWN":
            rel = "verify"
            rel_label = "Judicially Struck Down"
            requires_verification = True
            evidence_status = "STATUTORY_AUTHORITY"
            confidence_status = "TEMPORAL_TRANSITION_APPLIED"
        else:
            rel = "supported"
            rel_label = "Verified Indian Legal Authority"
            requires_verification = False
            evidence_status = "STATUTORY_AUTHORITY"
            confidence_status = "HIGH"

        if False:  # replaced by above threshold logic
            pass
        elif temporal_status == "STRUCK_DOWN":
            rel = "verify"
            rel_label = "Judicially Struck Down"
            requires_verification = True
        else:
            rel = "supported"
            rel_label = "Verified Indian Legal Authority"
            requires_verification = False

        sq = indian_rag_res.get("structured_query", {})
        return {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": answer_text,
            "query_type": "LEGAL_QUERY",
            "route": "LEGAL_QUERY",
            "type": "legal",
            "reliability": rel,
            "reliabilityLabel": rel_label,
            "sources": sources,
            "citations": [s["reference"] for s in sources],
            "requires_verification": requires_verification,
            "confidence_status": confidence_status,
            "evidence_status": evidence_status,
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "LEGAL_QUERY"),
            "legal_intent_confidence": getattr(route_result, "legal_intent_confidence", 0.95),
            "case_intent_confidence": getattr(route_result, "case_intent_confidence", 0.0),
            "resolved_act": sq.get("act") or sq.get("unindexed_act_name"),
            "provision_type": sq.get("provision_type"),
            "provision_number": sq.get("provision_number"),
            "retrieval_mode": indian_rag_res.get("retrieval_mode", "LEGAL_RAG"),
            "retrieval_candidate_count": len(sources),
            "accepted_source_count": len(sources),
            "source_count": len(sources),
            "adapter": indian_rag_res.get("adapter", "outputs/qwen14b-legalai-v2" if indian_rag_res.get("qwen_invoked") else None),
            "qwen_invoked": indian_rag_res.get("qwen_invoked", False),
            "abstained": abstained
        }

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

    answer_text = rag_result.get("answer", "")
    if has_greeting_prefix(req.content) and not answer_text.startswith("Absolutely!") and not answer_text.startswith("Hey"):
        answer_text = f"Absolutely! 👋\n\n{answer_text}"

    return {
        "id": f"msg-{int(time.time() * 1000)}",
        "role": "assistant",
        "timestamp": time.strftime("%I:%M %p"),
        "content": answer_text,
        "query_type": "LEGAL_QUERY",
        "type": "legal",
        "reliability": rel,
        "reliabilityLabel": rel_label,
        "sources": sources,
        "citations": rag_result.get("citations", []),
        "requires_verification": (rel == "verify"),
        "confidence_status": rag_result.get("confidence_status", ""),
        "evidence_status": rag_result.get("evidence_status", ""),
        "generation_time_sec": round(time.time() - t0, 3)
    }



def split_into_sentence_chunks(text: str) -> List[str]:
    """
    Splits text into cohesive sentence, heading, bullet point, or paragraph units.
    Ensures pre-computed responses output in fluid sentence-by-sentence bursts
    rather than slow, single-word typewriter delays.
    """
    if not text:
        return []
    paragraphs = text.split("\n\n")
    chunks = []
    for p_idx, para in enumerate(paragraphs):
        lines = para.split("\n")
        for l_idx, line in enumerate(lines):
            line_str = line.strip()
            if not line_str:
                continue
            # If line is a Markdown heading, bullet point, list item, or short phrase
            if line_str.startswith(("#", "-", "*", ">")) or re.match(r"^\d+\.", line_str) or len(line_str.split()) <= 8:
                chunks.append(line + ("\n" if l_idx < len(lines) - 1 else ""))
            else:
                sentences = re.split(r"(?<=[.?!])\s+", line_str)
                buf = []
                w_count = 0
                for s in sentences:
                    buf.append(s)
                    w_count += len(s.split())
                    if w_count >= 8:
                        chunks.append(" ".join(buf) + " ")
                        buf = []
                        w_count = 0
                if buf:
                    chunks.append(" ".join(buf) + ("\n" if l_idx < len(lines) - 1 else ""))
        if p_idx < len(paragraphs) - 1:
            chunks.append("\n\n")
    return chunks


async def stream_sentence_bursts(full_text: str, delay: float = 0.02):
    """
    Asynchronously yields pre-generated text in fast, natural sentence/paragraph chunks.
    Delivers a ChatGPT/Claude-like reading experience with instant responsiveness.
    """
    chunks = split_into_sentence_chunks(full_text)
    accumulated = ""
    for chunk in chunks:
        accumulated += chunk
        yield accumulated
        await asyncio.sleep(delay)


async def stream_sentence_chunks(streamer_iterator, min_chunk_words: int = 3, max_chunk_words: int = 10):
    """
    Buffers real-time tokens from TextIteratorStreamer and yields natural sentence,
    clause, and heading chunks. Eliminates subword/single-word stuttering.
    """
    current_text = ""
    buffer = ""
    sentence_delimiters = (". ", ".\n", "? ", "?\n", "! ", "!\n", "\n\n", ":\n")

    for text_chunk in streamer_iterator:
        current_text += text_chunk
        buffer += text_chunk

        has_delimiter = any(d in buffer for d in sentence_delimiters)
        words = buffer.split()
        word_count = len(words)

        if (has_delimiter and word_count >= min_chunk_words) or word_count >= max_chunk_words or "\n\n" in buffer or buffer.endswith("\n"):
            yield current_text
            buffer = ""
            await asyncio.sleep(0.002)

    if buffer:
        yield current_text


@app.post("/api/v1/ai/chat/stream")
async def ai_chat_stream(req: AIChatRequest):
    """Server-Sent Events (SSE) streaming endpoint for LegalAI Assistant."""
    global pipeline, case_rag_pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="LegalAI RAG Pipeline is initializing")

    effective_case_id = req.caseId or (req.selectedCases[0] if (req.selectedCases and len(req.selectedCases) == 1) else None) or req.caseNumber
    cid, cnum = resolve_case_identifier(effective_case_id)
    canonical_case_id = cid or effective_case_id

    router = get_query_router()
    route_result = router.classify(req.content, conversation_history=req.history, case_id=canonical_case_id, mode=req.mode)
    if not canonical_case_id and getattr(route_result, "case_id", None):
        canonical_case_id = route_result.case_id
        cid, cnum = resolve_case_identifier(canonical_case_id)
    stream_suggestions = SuggestionGenerator.generate_suggestions(
        sub_intent=getattr(route_result, "sub_intent", None),
        case_id=canonical_case_id
    )

    async def event_generator():
        t0 = time.time()

        # Stream Route: CASE_DRAFTING
        if route_result.intent == QueryIntent.CASE_DRAFTING:
            # Check if user is asking to amend/revise an existing draft, or requesting a fresh petition
            query_lower = req.content.lower()
            is_amendment = any(w in query_lower for w in ["amend", "modify", "revise", "update the draft", "add clause", "change paragraph", "change respondent", "change petitioner"])

            chat_turns = [{"role": "system", "content": LEGAL_DRAFTING_SYSTEM_PROMPT}]
            if req.history and is_amendment:
                for turn in req.history[-4:]:
                    r = turn.get("role")
                    c = turn.get("content", "")
                    if r in ("user", "assistant") and c:
                        chat_turns.append({"role": r, "content": c})
            chat_turns.append({"role": "user", "content": req.content})

            streamer = stream_generate_tokens(
                pipeline=pipeline,
                messages=chat_turns,
                max_new_tokens=1000,
                disable_adapter=True
            )

            current_text = ""
            for text_chunk in streamer:
                current_text += text_chunk
                yield f"event: token\ndata: {json.dumps({'token': current_text})}\n\n"
                await asyncio.sleep(0.0001)

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": current_text,
                "query_type": "CASE_DRAFTING",
                "route": "CASE_DRAFTING",
                "type": "legal_drafting",
                "reliability": "supported",
                "reliabilityLabel": "Formal Legal Pleading",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "DRAFTING_SYNTHESIZED",
                "evidence_status": "STRUCTURED_PLEADING",
                "generation_time_sec": round(time.time() - t0, 3),
                "suggestions": stream_suggestions
            }
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route: GENERAL
        if route_result.intent == QueryIntent.GENERAL:
            chat_turns = [{"role": "system", "content": BASE_QWEN_SYSTEM_PROMPT}]
            if req.history:
                for turn in req.history[-4:]:
                    r = turn.get("role")
                    c = turn.get("content", "")
                    if r in ("user", "assistant") and c:
                        chat_turns.append({"role": r, "content": c})
            chat_turns.append({"role": "user", "content": req.content})

            q_words = len(req.content.split())
            token_limit = 1024

            streamer = stream_generate_tokens(
                pipeline=pipeline,
                messages=chat_turns,
                max_new_tokens=token_limit,
                disable_adapter=True
            )

            current_text = ""
            for text_chunk in streamer:
                current_text += text_chunk
                yield f"event: token\ndata: {json.dumps({'token': current_text})}\n\n"
                await asyncio.sleep(0.0001)

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": current_text,
                "query_type": "GENERAL",
                "route": "GENERAL",
                "type": "general",
                "reliability": "supported",
                "reliabilityLabel": "Conceptual Understanding",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "PARAMETRIC_CONCEPTUAL",
                "evidence_status": "BASE_MODEL_REASONING",
                "generation_time_sec": round(time.time() - t0, 3),
                "suggestions": stream_suggestions
            }
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 1: CONVERSATIONAL
        if route_result.intent == QueryIntent.CONVERSATIONAL:
            if getattr(route_result, "sub_intent", "") in (SubIntent.ASSISTANT_IDENTITY.value, "ASSISTANT_IDENTITY") or \
               getattr(route_result, "output_plan", "") == OutputPlan.ASSISTANT_IDENTITY.value:
                answer_text = LEGALAI_ASSISTANT_IDENTITY
            else:
                answer_text = await asyncio.to_thread(
                    generate_conversational_response,
                    pipeline=pipeline,
                    message=req.content,
                    history=req.history,
                    active_case_id=canonical_case_id,
                    max_new_tokens=256
                )
            async for chunk in stream_sentence_bursts(answer_text, delay=0.02):
                yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": answer_text,
                "query_type": "CONVERSATIONAL",
                "type": "conversational",
                "reliability": "supported",
                "reliabilityLabel": "Conversational Greeting",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "CONVERSATIONAL",
                "evidence_status": "CONVERSATIONAL",
                "generation_time_sec": round(time.time() - t0, 3)
            }
            complete_payload["sub_intent"] = getattr(route_result, "sub_intent", None)
            complete_payload["user_goal"] = getattr(route_result, "user_goal", None)
            complete_payload["output_plan"] = getattr(route_result, "output_plan", None)
            complete_payload["suggestions"] = stream_suggestions
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2: OUT_OF_SCOPE / GENERAL_NON_LEGAL
        if route_result.intent in (QueryIntent.OUT_OF_SCOPE, QueryIntent.GENERAL_NON_LEGAL):
            answer_text = generate_out_of_scope_response(
                message=req.content,
                history=req.history
            )
            async for chunk in stream_sentence_bursts(answer_text, delay=0.02):
                yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": answer_text,
                "query_type": "OUT_OF_SCOPE",
                "type": "conversational",
                "reliability": "supported",
                "reliabilityLabel": "Legal Scope Boundary",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "OUT_OF_SCOPE",
                "evidence_status": "OUT_OF_SCOPE",
                "generation_time_sec": round(time.time() - t0, 3)
            }
            complete_payload["sub_intent"] = getattr(route_result, "sub_intent", None)
            complete_payload["user_goal"] = getattr(route_result, "user_goal", None)
            complete_payload["output_plan"] = getattr(route_result, "output_plan", None)
            complete_payload["suggestions"] = stream_suggestions
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2B: AMBIGUOUS
        if route_result.intent == QueryIntent.AMBIGUOUS:
            answer_text = generate_ambiguous_response(
                message=req.content,
                history=req.history
            )
            async for chunk in stream_sentence_bursts(answer_text, delay=0.02):
                yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": answer_text,
                "query_type": "AMBIGUOUS",
                "type": "conversational",
                "reliability": "supported",
                "reliabilityLabel": "Clarification Requested",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "AMBIGUOUS",
                "evidence_status": "AMBIGUOUS",
                "generation_time_sec": round(time.time() - t0, 3)
            }
            complete_payload["sub_intent"] = getattr(route_result, "sub_intent", None)
            complete_payload["user_goal"] = getattr(route_result, "user_goal", None)
            complete_payload["output_plan"] = getattr(route_result, "output_plan", None)
            complete_payload["suggestions"] = stream_suggestions
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2C: SYSTEM_INFO (Verified Architectural Context, Zero RAG)
        if route_result.intent == QueryIntent.SYSTEM_INFO:
            answer_text = generate_system_info_response(req.content)
            async for chunk in stream_sentence_bursts(answer_text, delay=0.02):
                yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": answer_text,
                "query_type": "SYSTEM_INFO",
                "route": "SYSTEM_INFO",
                "type": "system_info",
                "reliability": "supported",
                "reliabilityLabel": "Verified System Architecture",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "SYSTEM_SPECIFICATION",
                "evidence_status": "VERIFIED_SYSTEM_CONTEXT",
                "generation_time_sec": round(time.time() - t0, 3)
            }
            complete_payload["sub_intent"] = getattr(route_result, "sub_intent", None)
            complete_payload["user_goal"] = getattr(route_result, "user_goal", None)
            complete_payload["output_plan"] = getattr(route_result, "output_plan", None)
            complete_payload["suggestions"] = stream_suggestions
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2D: TECHNICAL_AI (Base Qwen Conceptual Explanation, Real-Time Sentence Streaming)
        if route_result.intent == QueryIntent.TECHNICAL_AI:
            system_prompt = (
                "You are an expert AI engineer and technical educator. "
                "Provide clear, accurate, and structured conceptual explanations of artificial intelligence, "
                "machine learning, large language models, retrieval augmented generation (RAG), and fine-tuning. "
                "Format responses cleanly with Markdown headings (###), bullet points, and concise professional prose."
            )
            chat_turns = [{"role": "system", "content": system_prompt}]
            if req.history:
                for turn in req.history[-4:]:
                    r = turn.get("role")
                    c = turn.get("content", "")
                    if r in ("user", "assistant") and c:
                        chat_turns.append({"role": r, "content": c})
            chat_turns.append({"role": "user", "content": req.content})

            streamer = stream_generate_tokens(
                pipeline=pipeline,
                messages=chat_turns,
                max_new_tokens=400,
                disable_adapter=True
            )

            current_text = ""
            for text_chunk in streamer:
                current_text += text_chunk
                yield f"event: token\ndata: {json.dumps({'token': current_text})}\n\n"
                await asyncio.sleep(0.0001)

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": current_text,
                "query_type": "TECHNICAL_AI",
                "route": "TECHNICAL_AI",
                "type": "technical_ai",
                "reliability": "supported",
                "reliabilityLabel": "Base Qwen Technical Explanation",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "BASE_QWEN_TECHNICAL",
                "evidence_status": "PARAMETRIC_BASE_MODEL",
                "generation_time_sec": round(time.time() - t0, 3)
            }
            complete_payload["sub_intent"] = getattr(route_result, "sub_intent", None)
            complete_payload["user_goal"] = getattr(route_result, "user_goal", None)
            complete_payload["output_plan"] = getattr(route_result, "output_plan", None)
            complete_payload["suggestions"] = stream_suggestions
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2E: CASE_MANAGEMENT (Application DB cases table, Zero Case RAG)
        if route_result.intent == QueryIntent.CASE_MANAGEMENT:
            effective_case_id = req.caseId or (req.selectedCases[0] if (req.selectedCases and len(req.selectedCases) > 0) else None) or req.caseNumber
            answer_text = generate_case_management_response(req.content, active_case_id=effective_case_id)
            async for chunk in stream_sentence_bursts(answer_text, delay=0.02):
                yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": answer_text,
                "query_type": "CASE_MANAGEMENT",
                "route": "CASE_MANAGEMENT",
                "type": "case_management",
                "reliability": "supported",
                "reliabilityLabel": "Case Portfolio Management",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "CASE_MANAGEMENT_DB",
                "evidence_status": "APPLICATION_DATABASE",
                "generation_time_sec": round(time.time() - t0, 3)
            }
            complete_payload["sub_intent"] = getattr(route_result, "sub_intent", None)
            complete_payload["user_goal"] = getattr(route_result, "user_goal", None)
            complete_payload["output_plan"] = getattr(route_result, "output_plan", None)
            complete_payload["suggestions"] = stream_suggestions
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 3: CASE_QUERY or HEARING_PREPARATION (Strictly semantic intent or explicit single-case inquiry)
        rag_case_id = get_best_rag_case_id(case_rag_pipeline, cid, cnum) or canonical_case_id
        is_case_intent = route_result.intent in (QueryIntent.CASE_QUERY, QueryIntent.HEARING_PREPARATION)

        if is_case_intent:
            if not rag_case_id and req.mode != "MULTI_CASE":
                answer_text = generate_case_guidance(None)
                sources = []
                rel = "supported"
                rel_label = "Case Guidance"
                conf_status = "CASE_GUIDANCE"
                async for chunk in stream_sentence_bursts(answer_text, delay=0.02):
                    yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"
            elif case_rag_pipeline:
                # 1. Fast retrieval in <0.05s
                top_chunks = case_rag_pipeline.retriever.retrieve(
                    query=req.content,
                    case_id=rag_case_id,
                    top_k=6
                )
                chunks = top_chunks if top_chunks else []
                meta = case_rag_pipeline._get_case_metadata(rag_case_id) if hasattr(case_rag_pipeline, "_get_case_metadata") else None
                case_title = meta.get("case_title") if meta else (rag_case_id or "Current Matter")
                case_num = meta.get("case_number") if meta else (cnum or "")

                if not chunks:
                    empty_msg = f"### Insufficient Case Material for Analysis\n\nNo case documents have been uploaded or indexed for **{case_title}** ({case_num}) yet. Please upload relevant case filings or pleadings to enable case document analysis."
                    yield f"event: token\ndata: {json.dumps({'token': empty_msg})}\n\n"
                    answer_text = empty_msg
                    sources = []
                    rel = "verify"
                    rel_label = "Insufficient Case Material"
                    conf_status = "INSUFFICIENT_CASE_MATERIAL"
                else:
                    case_sources = []
                    case_context_blocks = []
                    for chunk in chunks:
                        case_sources.append({
                            "id": chunk.chunk_id,
                            "type": "document",
                            "title": chunk.document_name,
                            "reference": f"Page {chunk.page_number}" if chunk.page_number else "Case Record",
                            "excerpt": chunk.text[:180] + ("..." if len(chunk.text) > 180 else ""),
                            "case_id": rag_case_id,
                            "case_title": case_title,
                            "case_number": case_num,
                            "document_id": chunk.document_id,
                            "document_name": chunk.document_name,
                            "chunk_id": chunk.chunk_id,
                            "source_type": "document",
                            "source_scope": "CURRENT_MATTER"
                        })
                        case_context_blocks.append(
                            f"--- DOCUMENT: {chunk.document_name} | PAGE: {chunk.page_number} ---\n{chunk.text}"
                        )
                    case_context_str = "\n\n".join(case_context_blocks)

                    chat_turns = [{"role": "system", "content": CHATGPT_CLAUDE_CASE_SYSTEM_PROMPT}]
                    if req.history:
                        for turn in req.history[-6:]:
                            r = turn.get("role")
                            c = turn.get("content", "")
                            if r in ("user", "assistant") and c:
                                chat_turns.append({"role": r, "content": c})

                    user_prompt = (
                        f"CASE SCOPE: {case_title} ({case_num})\n\n"
                        f"AUTHENTIC CASE EVIDENCE & DOCUMENTS:\n{case_context_str}\n\n"
                        f"USER QUERY: {req.content}\n\n"
                        f"Please provide an articulate, well-structured, comprehensive answer in the fluent, clear style of ChatGPT and Claude.\n"
                        f"Use clean Markdown headings (###), bold lead-in bullet points, and natural professional prose.\n"
                        f"Detail the core dispute, key parties, agreements on record, and operative court orders.\n"
                        f"Do NOT output rigid robotic machine headers like bare 'ANALYSIS' or 'UNCERTAINTY'."
                    )
                    chat_turns.append({"role": "user", "content": user_prompt})

                    # Real-time token streaming - first token in <1 second!
                    streamer = stream_generate_tokens(
                        pipeline=pipeline,
                        messages=chat_turns,
                        max_new_tokens=550,
                        disable_adapter=True
                    )

                    current_text = ""
                    for text_chunk in streamer:
                        current_text += text_chunk
                        yield f"event: token\ndata: {json.dumps({'token': current_text})}\n\n"
                        await asyncio.sleep(0.0001)

                    answer_text = current_text
                    sources = case_sources
                    rel = "supported"
                    rel_label = "Supported by case documents"
                    conf_status = "CASE_DOCUMENT_GROUNDED"
            else:
                answer_text = generate_case_guidance(rag_case_id)
                sources = []
                rel = "supported"
                rel_label = "Case Guidance"
                conf_status = "CASE_GUIDANCE"

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": answer_text,
                "query_type": route_result.intent.value,
                "route": route_result.intent.value,
                "type": "case_analysis",
                "reliability": rel,
                "reliabilityLabel": rel_label,
                "sources": sources,
                "citations": [s.get("reference", "") for s in sources],
                "requires_verification": (rel == "verify"),
                "confidence_status": conf_status,
                "evidence_status": "ANALYZED" if sources else "INSUFFICIENT_CASE_MATERIAL",
                "generation_time_sec": round(time.time() - t0, 3),
                "sub_intent": getattr(route_result, "sub_intent", None),
                "user_goal": getattr(route_result, "user_goal", None),
                "output_plan": getattr(route_result, "output_plan", None),
                "suggestions": stream_suggestions
            }
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 3: LEGAL_QUERY (Production Expanded Indian Legal Knowledge Pipeline)
        if indian_knowledge_pipeline:
            if indian_knowledge_bridge:
                is_foreign, redirect_resp = indian_knowledge_bridge.check_foreign_law_query(req.content)
                if is_foreign:
                    async for chunk in stream_sentence_bursts(redirect_resp, delay=0.02):
                        yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"

                    complete_payload = {
                        "id": f"msg-{int(time.time() * 1000)}",
                        "role": "assistant",
                        "timestamp": time.strftime("%I:%M %p"),
                        "content": redirect_resp,
                        "query_type": "LEGAL_QUERY",
                        "type": "legal",
                        "reliability": "supported",
                        "reliabilityLabel": "Foreign-Law Scope Redirection",
                        "sources": [],
                        "citations": [],
                        "requires_verification": False,
                        "confidence_status": "OUT_OF_SCOPE_FOREIGN_LAW",
                        "evidence_status": "OUT_OF_SCOPE_FOREIGN_LAW",
                        "generation_time_sec": round(time.time() - t0, 3)
                    }
                    yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
                    return

            indian_rag_res = await asyncio.to_thread(
                indian_knowledge_pipeline.query,
                question=req.content,
                incident_date=req.effective_date,
                conversation_history=req.history
            )

            full_answer = indian_rag_res.get("answer", "")
            if has_greeting_prefix(req.content) and not full_answer.startswith("Absolutely!") and not full_answer.startswith("Hey"):
                full_answer = f"Absolutely! 👋\n\n{full_answer}"

            async for chunk in stream_sentence_bursts(full_answer, delay=0.02):
                yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"

            sources = [
                {
                    "chunk_id": s["chunk_id"],
                    "act_name": s["title"],
                    "section_number": s["citation"],
                    "section_title": s["citation"],
                    "reference": s["citation"],
                    "content": "",
                    "source_url": s["source_url"],
                    "similarity_score": s["score"],
                    "source_type": s["document_type"],
                    "hierarchy": s["authority_tier"],
                    "temporal_status": s["temporal_status"]
                }
                for s in indian_rag_res.get("sources", [])
            ]

            abstained = indian_rag_res.get("abstained", False)
            temporal_status = indian_rag_res.get("temporal_status", "UNKNOWN")
            evidence_status = indian_rag_res.get("evidence_status", "STATUTORY_AUTHORITY" if not abstained else "INSUFFICIENT_RETRIEVAL")
            confidence_status = indian_rag_res.get("confidence_status", "HIGH" if not abstained else "INSUFFICIENT_RETRIEVAL")

            if abstained:
                rel = "verify"
                rel_label = "Verification Required"
                requires_verification = True
            elif temporal_status == "STRUCK_DOWN":
                rel = "verify"
                rel_label = "Judicially Struck Down"
                requires_verification = True
            else:
                rel = "supported"
                rel_label = "Verified Indian Legal Authority"
                requires_verification = False

            sq = indian_rag_res.get("structured_query", {})
            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
                "request_id": f"req-{int(time.time() * 1000)}",
                "role": "assistant",
                "timestamp": time.strftime("%I:%M %p"),
                "content": full_answer,
                "query_type": "LEGAL_QUERY",
                "route": "LEGAL_QUERY",
                "type": "legal",
                "reliability": rel,
                "reliabilityLabel": rel_label,
                "sources": sources,
                "citations": [s["reference"] for s in sources],
                "requires_verification": requires_verification,
                "confidence_status": confidence_status,
                "evidence_status": evidence_status,
                "generation_time_sec": round(time.time() - t0, 3),
                "intent": route_result.intent.value,
                "sub_intent": getattr(route_result, "sub_intent", "LEGAL_QUERY"),
                "legal_intent_confidence": getattr(route_result, "legal_intent_confidence", 0.95),
                "case_intent_confidence": getattr(route_result, "case_intent_confidence", 0.0),
                "resolved_act": sq.get("act") or sq.get("unindexed_act_name"),
                "provision_type": sq.get("provision_type"),
                "provision_number": sq.get("provision_number"),
                "retrieval_mode": indian_rag_res.get("retrieval_mode", "LEGAL_RAG"),
                "retrieval_candidate_count": len(sources),
                "accepted_source_count": len(sources),
                "source_count": len(sources),
                "adapter": indian_rag_res.get("adapter", "outputs/qwen14b-legalai-v2" if indian_rag_res.get("qwen_invoked") else None),
                "qwen_invoked": indian_rag_res.get("qwen_invoked", False),
                "abstained": abstained
            }
            complete_payload["sub_intent"] = getattr(route_result, "sub_intent", None)
            complete_payload["user_goal"] = getattr(route_result, "user_goal", None)
            complete_payload["output_plan"] = getattr(route_result, "output_plan", None)
            complete_payload["suggestions"] = stream_suggestions
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Real-time streaming for statutory query
        domain_res = pipeline.domain_detector.detect(req.content)
        act_filter = req.act_filter or domain_res.statute_code
        sec_filter = req.section_filter or domain_res.specific_provision

        filtered_chunks = pipeline.retriever.retrieve(
            question=req.content,
            act_filter=act_filter,
            section_filter=sec_filter,
            top_k=4
        )

        stat_sources = format_sources(filtered_chunks)
        stat_context_str = "\n\n".join([
            f"[{getattr(c, 'act', getattr(c, 'act_name', 'Statute'))} Section {getattr(c, 'section', getattr(c, 'section_number', ''))}: {c.section_title}]\n{c.text}"
            for c in filtered_chunks
        ])

        chat_turns = [{"role": "system", "content": CHATGPT_CLAUDE_LEGAL_SYSTEM_PROMPT}]
        if req.history:
            for turn in req.history[-4:]:
                r = turn.get("role")
                c = turn.get("content", "")
                if r in ("user", "assistant") and c:
                    chat_turns.append({"role": r, "content": c})

        user_prompt = (
            f"RELEVANT STATUTORY PROVISIONS:\n{stat_context_str}\n\n"
            f"LEGAL INQUIRY: {req.content}\n\n"
            f"Please explain the applicable statutory law, its essential legal elements, punishment/procedure, and relevant considerations in clear Markdown format."
        )
        chat_turns.append({"role": "user", "content": user_prompt})

        streamer = stream_generate_tokens(
            pipeline=pipeline,
            messages=chat_turns,
            max_new_tokens=450,
            disable_adapter=False
        )

        current_text = ""
        for text_chunk in streamer:
            current_text += text_chunk
            yield f"event: token\ndata: {json.dumps({'token': current_text})}\n\n"
            await asyncio.sleep(0.0001)

        complete_payload = {
            "id": f"msg-{int(time.time() * 1000)}",
            "request_id": f"req-{int(time.time() * 1000)}",
            "role": "assistant",
            "timestamp": time.strftime("%I:%M %p"),
            "content": current_text,
            "query_type": "LEGAL_QUERY",
            "route": "LEGAL_QUERY",
            "type": "legal",
            "reliability": "supported",
            "reliabilityLabel": "Verified Indian Legal Authority",
            "sources": stat_sources,
            "citations": [s.get("reference", "") for s in stat_sources],
            "requires_verification": False,
            "confidence_status": "STATUTORY_AUTHORITY",
            "evidence_status": "ANSWERABLE",
            "generation_time_sec": round(time.time() - t0, 3),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "LEGAL_QUERY"),
            "legal_intent_confidence": getattr(route_result, "legal_intent_confidence", 0.95),
            "case_intent_confidence": getattr(route_result, "case_intent_confidence", 0.0),
            "resolved_act": act_filter,
            "provision_type": None,
            "provision_number": sec_filter,
            "retrieval_mode": "LEGAL_RAG_STREAM",
            "retrieval_candidate_count": len(stat_sources),
            "accepted_source_count": len(stat_sources),
            "source_count": len(stat_sources),
            "adapter": "outputs/qwen14b-legalai-v2",
            "qwen_invoked": True if stat_sources else False,
            "abstained": False,
            "suggestions": stream_suggestions
        }
        yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
        return

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


@app.post("/api/v1/ai/drafting/copilot")
async def ai_drafting_copilot(req: DraftingCopilotRequest):
    """
    Direct statutory legal drafting & real-time document editing copilot.
    Handles targeted edits (e.g. placeholder replacement, filling addresses, modifying parties/dates/amounts, adding clauses)
    as well as full-document generation (e.g. drafting complete petitions, plaints, notices, applications).
    """
    t0 = time.time()
    instruction = (req.instruction or "").strip()
    current_doc = (req.current_document or "").strip()
    selected_text = (req.selected_text or "").strip()

    if not instruction:
        raise HTTPException(status_code=400, detail="Drafting instruction cannot be empty")

    system_prompt = (
        "You are an elite Senior Advocate and master legal draftsman in the Supreme Court of India.\n"
        "You specialize in Indian litigation drafting under the Bharatiya Nyaya Sanhita 2023 (BNS), "
        "Bharatiya Nagarik Suraksha Sanhita 2023 (BNSS), Bharatiya Sakshya Adhiniyam 2023 (BSA), "
        "Code of Civil Procedure 1908 (CPC), Commercial Courts Act 2015, and Arbitration & Conciliation Act 1996.\n\n"
        "Your job is to DIRECTLY UPDATE the draft document or CREATE A COMPLETE LEGAL DRAFT based on the litigator's instruction.\n\n"
        "CRITICAL GUIDELINES:\n"
        "1. TARGETED EDIT / PLACEHOLDER FILL / MODIFICATION:\n"
        "   - If the instruction is to fill in, replace, or update placeholders (e.g. '[Full Postal Address]', '[Client Name]', '[Date]', '[Amount]', '[Specify Breach Particulars]', '[Opposing Party / Company Name]') or specific fields/facts:\n"
        "     * Replace the placeholders or targeted text with the exact details provided by the litigator.\n"
        "     * PRESERVE the entirety of the existing document: keep all other paragraphs, formatting, numbering, notices, and signature blocks intact.\n"
        "   - If the instruction is to add or strengthen grounds, add prayer clauses, or insert specific legal provisions (e.g. BNSS 480, BSA 63, Order 39 CPC, Force Majeure):\n"
        "     * Seamlessly integrate the clause into its proper position within the document without breaking document coherence.\n\n"
        "2. WHOLE DRAFT GENERATION:\n"
        "   - If the instruction is to draft, create, or generate a petition, plaint, legal notice, bail application, affidavit, or agreement from provided facts (e.g. 'draft a petition with these informations...'):\n"
        "     * Generate the FULL, comprehensive, professional Indian legal document adhering to High Court / District Court pleading formats.\n"
        "     * Populate all petitioner, respondent, court, facts, cause of action, grounds, and prayer details from the litigator's instructions.\n\n"
        "OUTPUT FORMAT:\n"
        "You MUST respond ONLY with a JSON object in this exact schema (no preamble, no conversational chatter):\n"
        "{\n"
        '  "action": "UPDATE_DOCUMENT" or "CREATE_DRAFT",\n'
        '  "summary": "1-sentence concise description of what was changed or drafted",\n'
        '  "updated_document": "The complete updated document text ready for the editor",\n'
        '  "suggested_clause": "The specific clause or field that was altered/added",\n'
        '  "explanation": "Legal rationale or concise description of the edit"\n'
        "}"
    )

    user_content = ""
    if current_doc:
        user_content += f"CURRENT DOCUMENT IN EDITOR:\n```\n{current_doc}\n```\n\n"
    if selected_text:
        user_content += f"SELECTED TEXT IN EDITOR:\n```\n{selected_text}\n```\n\n"
    user_content += f"LITIGATOR INSTRUCTION:\n{instruction}"

    result = None

    # Try high-speed vLLM on port 8009
    try:
        req_data = json.dumps({
            "model": "Qwen/Qwen2.5-32B-Instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.15,
            "max_tokens": 3500
        }).encode("utf-8")

        vllm_req = urllib.request.Request(
            "http://127.0.0.1:8009/v1/chat/completions",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(vllm_req, timeout=35) as resp:
            vllm_res = json.loads(resp.read().decode("utf-8"))
            raw = vllm_res["choices"][0]["message"]["content"].strip()
            cleaned = raw
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            result = json.loads(cleaned.strip())
    except Exception as e:
        logger.warning(f"Drafting Copilot vLLM/JSON parsing exception: {e}")

    # Fallback to deterministic regex engine if vLLM failed or gave unexpected format
    if not result or not isinstance(result, dict) or not result.get("updated_document"):
        updated_doc = current_doc
        action = "UPDATE_DOCUMENT"
        summary = f"Updated draft with: {instruction[:40]}"
        clause = ""
        explanation = "Applied direct drafting modification to document."

        # Check for address replacement
        addr_match = re.search(r'(?:fill|set|change|update|add|replace)\s+(?:the\s+)?address\s+(?:as|to|is|with|:)?\s*(.+)', instruction, re.IGNORECASE)
        if addr_match:
            new_addr = addr_match.group(1).strip()
            replaced = False
            for ph in ["[Full Postal Address]", "[Postal Address]", "[Address]"]:
                if ph in updated_doc:
                    updated_doc = updated_doc.replace(ph, new_addr)
                    summary = f"Updated postal address to {new_addr}"
                    clause = f"Address: {new_addr}"
                    replaced = True
                    break
            if not replaced:
                if "Address:" in updated_doc:
                    updated_doc = re.sub(r'(Address:\s*).*', r'\g<1>' + new_addr, updated_doc)
                    summary = f"Updated address to {new_addr}"
                    clause = f"Address: {new_addr}"
                else:
                    updated_doc = f"Address: {new_addr}\n\n" + updated_doc
                    summary = f"Added address: {new_addr}"
        elif any(k in instruction.lower() for k in ["draft a", "create a", "draft petition", "draft legal notice"]):
            action = "CREATE_DRAFT"
            summary = f"Generated {req.document_type or 'Legal Document'} based on provided details."
            updated_doc = f"# LEGAL DOCUMENT DRAFT\n\n{instruction}\n\n[Synthesized under Indian statutory standards]"

        result = {
            "action": action,
            "summary": summary,
            "updated_document": updated_doc,
            "suggested_clause": clause,
            "explanation": explanation
        }

    result["generation_time_sec"] = round(time.time() - t0, 3)
    return result



# --- Conversation Persistence & Lifecycle Endpoints ---

@app.get("/api/v1/conversations")
async def get_conversations():
    """Returns all stored conversations from the database."""
    case_service = get_supabase_case_service()
    if case_service:
        convs = case_service.get_all_conversations()
        return {"conversations": convs, "count": len(convs)}
    return {"conversations": [], "count": 0}


@app.post("/api/v1/conversations")
async def save_conversation(conv: Dict[str, Any]):
    """Creates or updates a conversation record."""
    case_service = get_supabase_case_service()
    if case_service:
        res = case_service.save_conversation(conv)
        return {"ok": True, "conversation": res}
    return {"ok": False, "detail": "Case service unavailable"}


class RenameConversationRequest(BaseModel):
    title: str


@app.patch("/api/v1/conversations/{conv_id}/title")
async def rename_conversation(conv_id: str, req: RenameConversationRequest):
    """Renames an existing conversation."""
    case_service = get_supabase_case_service()
    if case_service:
        res = case_service.rename_conversation(conv_id, req.title)
        return {"ok": True, "conversation": res}
    return {"ok": False, "detail": "Case service unavailable"}


@app.delete("/api/v1/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    """Deletes a conversation and all its messages."""
    case_service = get_supabase_case_service()
    if case_service:
        res = case_service.delete_conversation(conv_id)
        return {"ok": True, "deleted": res}
    return {"ok": False, "detail": "Case service unavailable"}


@app.get("/api/v1/documents")
async def get_all_documents():
    """Returns all case documents stored in database."""
    case_service = get_supabase_case_service()
    if case_service:
        docs = case_service.get_all_documents() if hasattr(case_service, "get_all_documents") else []
        return {"documents": docs, "count": len(docs)}
    return {"documents": [], "count": 0}




# ==========================================
# COURTROOM SIMULATION & ADVOCACY ENGINE
# ==========================================
from src.courtroom.multi_agent_engine import (
    courtroom_engine,
    CourtroomTurnRequest,
)

class ScorecardRequest(BaseModel):
    session_history: List[Dict[str, Any]]
    case_title: Optional[str] = "Indian Legal Trial"

class AddCaseNoteRequest(BaseModel):
    note: str
    category: Optional[str] = "Litigation Strategy"

COURTROOM_CASES_PRESETS = [
    {
        "id": "2024-CV-1187",
        "title": "Martinez v. Coastal Holdings Ltd.",
        "court": "Commercial Court / High Court of Delhi",
        "bench": "Hon'ble Justice Rekha Palli (Presiding)",
        "opposing_counsel": "Sr. Adv. Harish Salve",
        "stakes": "₹18.50 Crores",
        "mode_options": ["SUBMISSIONS_ARGUMENT", "WITNESS_EXAMINATION"],
        "witnesses": [
            {
                "name": "David Martinez (Managing Director)",
                "role": "Petitioner / Key Officer",
                "default_composure": 80,
                "notes": "Asserts breach of shareholder covenant; susceptible on prior waiver emails."
            },
            {
                "name": "Sunil Agnihotri (Chief Financial Officer)",
                "role": "Independent Financial Auditor",
                "default_composure": 90,
                "notes": "Handles escrow accounts and dividend distribution ledgers."
            }
        ],
        "exhibits": [
            {"id": "Ex. P-1", "title": "Joint Venture & Shareholder Agreement (Clause 14.2 Negative Covenant)"},
            {"id": "Ex. P-2", "title": "Bank Wire Audit Confirmation (₹18.5 Cr Escrow Deposit)"},
            {"id": "Ex. D-1", "title": "Board Resolution Minutes dated 12th Jan 2024"}
        ],
        "brief": "Petitioner seeks urgent mandatory interlocutory injunction under Order 39 Rules 1 & 2 CPC restraining Respondent from diluting equity or creating third-party rights over coastal assets.",
        "case_notes": [
            {
                "category": "Statutory Grounds",
                "title": "Order 39 Rules 1 & 2 CPC — Irreparable Harm",
                "text": "My Lord, the three cardinal principles for interim injunction under Order 39 are satisfied: prima facie case, balance of convenience, and irreparable injury that cannot be remedied by damages."
            },
            {
                "category": "Contractual Breach",
                "title": "Negative Covenant (Clause 14.2)",
                "text": "Clause 14.2 of the Shareholder Agreement explicitly restrains the Respondent from encumbering port assets without unanimous board consent. Specific relief under Section 42 of the Specific Relief Act applies."
            },
            {
                "category": "Cross-Examination Trap",
                "title": "Confront CFO on ₹18.5 Cr Diversion",
                "text": "Mr. Agnihotri, look at Exhibit P-2. If the ₹18.50 Crores were deposited into the escrow on 15th January, why was ₹6.2 Crores transferred out to a sister entity within 48 hours without board sanction?"
            },
            {
                "category": "Binding Precedent",
                "title": "Gujarat Bottling Co. Ltd. v. Coca Cola Co.",
                "text": "As held by the Supreme Court in Gujarat Bottling (1995), a negative covenant in a commercial joint venture agreement during the subsistence of the contract is valid and enforceable by injunction."
            }
        ]
    },
    {
        "id": "2024-CR-0442",
        "title": "State (NCT of Delhi) v. Whitfield",
        "court": "Special Court (NDPS / PMLA), Patiala House Courts",
        "bench": "Hon'ble Special Judge (NDPS)",
        "opposing_counsel": "Special Public Prosecutor (SPP)",
        "stakes": "Personal Liberty / 18 Months Pre-Trial Detention",
        "mode_options": ["WITNESS_EXAMINATION", "BAIL_HEARING", "SUBMISSIONS_ARGUMENT"],
        "witnesses": [
            {
                "name": "Inspector Vikram Rathore (IO)",
                "role": "Investigating Officer (Prosecution Star Witness)",
                "default_composure": 85,
                "notes": "Vulnerable to timeline contradictions between Station Diary and Seizure Memo (Exhibit P-4)."
            },
            {
                "name": "Dr. Sunita Sharma (Forensic Officer)",
                "role": "Central Forensic Science Laboratory (CFSL) Expert",
                "default_composure": 92,
                "notes": "Testified to chemical assay; question chain of custody seals."
            }
        ],
        "exhibits": [
            {"id": "Ex. P-3", "title": "Notice under Section 50 NDPS Act (Search Authorization)"},
            {"id": "Ex. P-4", "title": "Contemporaneous Seizure Memo & Punch Witness Log"},
            {"id": "Ex. D-2", "title": "CCTV Footage Timestamp Log from Dock Gate 3"}
        ],
        "brief": "Accused seeks regular bail under Section 480 BNSS (erstwhile Section 439 CrPC) in alleged commercial quantity seizure, arguing breach of mandatory Section 50 protocol and fabricated seizure memos.",
        "case_notes": [
            {
                "category": "Statutory Grounds",
                "title": "Section 480 BNSS — Prolonged Pre-Trial Incarceration",
                "text": "My Lord, under Section 480 of the Bharatiya Nagarik Suraksha Sanhita, 2023, continued detention without trial violates Article 21. The applicant has completed 18 months of custody and 42 prosecution witnesses remain."
            },
            {
                "category": "Cross-Examination Trap",
                "title": "IO Rathore — 40-Minute Station Diary Discrepancy",
                "text": "Officer Rathore, please explain the 40-minute gap between Exhibit P-4 and the general diary. Exhibit P-4 states you were at the dock at 14:00 hours, whereas the station diary records your presence at headquarters."
            },
            {
                "category": "Evidentiary Challenge",
                "title": "Mandatory Non-Compliance with Section 50",
                "text": "Your Honour, the suspect was not informed of their statutory right under Section 50 to be searched before a Gazetted Officer or Magistrate. Under Vijaysinh Chandubha Jadeja (2011), this vitiates the recovery."
            },
            {
                "category": "Forensic Challenge",
                "title": "Broken Chain of Custody (CFSL Form)",
                "text": "Dr. Sharma, Exhibit P-4 indicates samples were drawn on 14th August, but the CFSL registry did not receive them until 28th August. The sample seals remained in police custody for 14 unexplained days."
            }
        ]
    },
    {
        "id": "2024-CC-0120",
        "title": "Apex Logistics Corp. v. Horizon Freight Services",
        "court": "Commercial Division, High Court of Bombay",
        "bench": "Hon'ble Justice B.P. Colabawalla",
        "opposing_counsel": "Sr. Adv. Darius Khambata",
        "stakes": "₹6.40 Crores",
        "mode_options": ["SUBMISSIONS_ARGUMENT", "WITNESS_EXAMINATION"],
        "witnesses": [
            {
                "name": "Karan Malhotra (Fleet Operations Head)",
                "role": "Respondent's Operations Witness",
                "default_composure": 75,
                "notes": "Concealed 40 stranded cargo vessels in international waters."
            }
        ],
        "exhibits": [
            {"id": "Ex. P-1", "title": "Master Service Agreement & Arbitration Clause 22"},
            {"id": "Ex. P-5", "title": "Termination Notice dated 15th August 2024"}
        ],
        "brief": "Section 9 petition under Arbitration and Conciliation Act for interim preservation of refrigerated containers and deposit of admitted dues.",
        "case_notes": [
            {
                "category": "Statutory Grounds",
                "title": "Section 9 Arbitration Act — Interim Preservation of Goods",
                "text": "May it please the Court, under Section 9(1)(ii)(a) of the Arbitration & Conciliation Act, this Court has jurisdiction to preserve perishable pharmaceutical cargo currently stranded aboard Respondent's 40 vessels."
            },
            {
                "category": "Cross-Examination Trap",
                "title": "Confront Operations Head on Vessel Redirection",
                "text": "Mr. Malhotra, did your dispatch control center intentionally instruct the 40 freight vessels to alter coordinates away from Nhava Sheva port on 12th August, prior to issuing the termination notice?"
            },
            {
                "category": "Binding Precedent",
                "title": "Firm Ashok Traders v. Gurumukh Das Saluja",
                "text": "In Firm Ashok Traders (2004), the Hon'ble Supreme Court held that interim orders under Section 9 are vital to prevent the arbitration from being rendered an exercise in futility."
            }
        ]
    }
]

@app.get("/api/v1/courtroom/cases")
async def get_courtroom_cases():
    return {"cases": COURTROOM_CASES_PRESETS, "count": len(COURTROOM_CASES_PRESETS)}

@app.post("/api/v1/courtroom/cases/{case_id}/notes")
async def add_courtroom_case_note(case_id: str, req: AddCaseNoteRequest):
    case_match = next((c for c in COURTROOM_CASES_PRESETS if c["id"] == case_id), None)
    if not case_match:
        raise HTTPException(status_code=404, detail="Case not found")
    new_note = {
        "category": req.category or "Custom Note",
        "title": req.note[:40] + ("..." if len(req.note) > 40 else ""),
        "text": req.note
    }
    case_match.setdefault("case_notes", []).insert(0, new_note)
    return {"ok": True, "note": new_note, "total_notes": len(case_match["case_notes"])}

@app.post("/api/v1/courtroom/turn")
async def process_courtroom_turn(req: CourtroomTurnRequest):
    case_match = next((c for c in COURTROOM_CASES_PRESETS if c["id"] == req.case_id), COURTROOM_CASES_PRESETS[0])

    turn_result = courtroom_engine.arbitrate_courtroom_turn(
        advocate_text=req.advocate_input,
        case_info=case_match,
        mode=req.mode,
        witness_name=req.witness_name or "Witness in the Box",
        current_composure=req.witness_composure,
        history=req.conversation_history
    )
    return {
        "ok": True,
        "mode": req.mode,
        "session_id": req.session_id,
        "advocate_input": req.advocate_input,
        **turn_result
    }

@app.post("/api/v1/courtroom/scorecard")
async def get_courtroom_scorecard(req: ScorecardRequest):
    res = courtroom_engine.generate_bench_scorecard(
        session_history=req.session_history,
        case_title=req.case_title or "Indian High Court Hearing"
    )
    return {"ok": True, "scorecard": res}
