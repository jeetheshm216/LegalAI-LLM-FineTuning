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

# Enforce GPU (defaults to 0 for intact 178GB B200)
if "CUDA_VISIBLE_DEVICES" not in os.environ:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"


import torch
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

# Existing LegalAI RAG Pipeline & Query Router
from src.rag.integration.rag_legalai import LegalAIRAGPipeline
from src.api.query_router import QueryRouter, QueryIntent, get_query_router
from src.case_rag import CaseRAGPipeline, CaseEmbedder
from src.legal_knowledge.retrieval.pipeline import GeneralIndianLegalKnowledgePipeline
from src.legal_knowledge.integration.router_bridge import IndianLegalRouterBridge

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
# Conversational & General System Prompts & Single-Model Generation
# -------------------------------------------------------------
LEGALAI_SYSTEM_PROMPT = """You are LegalAI, a professional AI assistant designed primarily for lawyers.

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


def generate_conversational_response(
    pipeline: LegalAIRAGPipeline,
    message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    max_new_tokens: int = 256
) -> str:
    """Generates a natural, friendly conversational response for greetings, courtesies, and pleasantries."""
    cleaned = message.strip()
    lower = cleaned.lower()
    lower_norm = re.sub(r'[\s,?!.]+', ' ', lower).strip()

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

    if re.match(r'^(?:ok|okay|cool|nice|great|got\s+it|understood|awesome|perfect|sure|fine)(?:[\s,!.]+)?$', lower_norm):
        return "Sounds good! 😊 Let me know whenever you're ready to dive into a legal question or case matter."

    if lower_norm in GREETING_RESPONSES:
        return GREETING_RESPONSES[lower_norm]

    if re.match(r'^(?:hi|hey|hello|hey\s+hi|hi\s+hey|hello\s+hi|hey\s+there|hiya|greetings)(?:[\s,!.]+)?$', lower_norm):
        import random
        return random.choice(GREETING_VARIATIONS)

    if re.match(r'^(?:good\s+morning)(?:[\s,!.]+)?$', lower_norm):
        return "Good morning! 👋 Ready when you are. What legal matter or research are we working on today?"

    if re.match(r'^(?:good\s+evening)(?:[\s,!.]+)?$', lower_norm):
        return "Good evening! 👋 Ready when you are. What legal matter or research are we working on today?"

    # 3. Natural Capability Inquiries ("what can you do for me", "what are the things you can able to do fro me")
    if re.search(r'\bwhat\s+(?:are\s+)?(?:all\s+)?(?:the\s+)?(?:things\s+)?(?:you\s+can\s+(?:be\s+)?able\s+to\s+do|can\s+you\s+do|are\s+you\s+able\s+to\s+do|do\s+you\s+do)(?:\s+(?:for|fro)\s+me)?\b', lower) or \
       re.search(r'\bwhat\s+are\s+the\s+things\s+you\s+can\s+.*?\b', lower) or \
       re.search(r'\b(?:what\s+can\s+you\s+help\s+(?:me\s+)?with|how\s+can\s+you\s+help(?:\s+me)?)\b', lower) or \
       re.search(r'\b(?:what\s+can\s+i\s+ask(?:\s+you)?|what\s+kinds?\s+of\s+questions?\s+can\s+i\s+ask|what\s+services?\s+do\s+you\s+provide)\b', lower) or \
       re.search(r'\b(?:what\s+are\s+your\s+(?:capabilities|features)|tell\s+me\s+what\s+you\s+can\s+do|what\s+can\s+i\s+use\s+you\s+for|what\s+do\s+you\s+help\s+with)\b', lower) or \
       re.search(r'\b(?:how\s+can\s+i\s+use\s+(?:you|legalai)|what\s+can\s+legalai\s+do|what\s+does\s+legalai\s+do|how\s+to\s+use\s+(?:you|legalai)|explain\s+your\s+capabilities)\b', lower) or \
       re.search(r'\bwhat\s+are\s+you\s+doing\b', lower) or \
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


def generate_case_management_response(message: str, active_case_id: Optional[str] = None) -> str:
    """
    Answers portfolio questions (priority, urgency, upcoming hearings, focus)
    by querying the verified application database (data/legalai_app.db, cases table).
    Does NOT invoke Case Document RAG.
    """
    try:
        conn = sqlite3.connect(APP_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, caseNumber, title, client, court, priority, status, nextHearing, hearingCountdownDays, description
            FROM cases
            ORDER BY 
                CASE 
                    WHEN LOWER(priority) = 'urgent' THEN 1
                    WHEN LOWER(status) = 'urgent' THEN 2
                    ELSE 3
                END,
                CASE 
                    WHEN hearingCountdownDays IS NOT NULL AND hearingCountdownDays >= 0 THEN hearingCountdownDays
                    ELSE 999
                END ASC
        """)
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to query cases table for case management: {e}")
        return "Case management information is temporarily unavailable. Please verify that the application database is accessible."

    if not rows:
        return "There are currently no active legal cases registered in your workspace."

    # Analyze matters
    urgent_cases = [r for r in rows if str(r[5]).lower() == 'urgent' or str(r[6]).lower() == 'urgent']
    upcoming_hearings = [r for r in rows if r[7] and r[7] != 'None scheduled']

    response_lines = ["**Case Portfolio & Workload Overview**\n"]

    if urgent_cases:
        top_urgent = urgent_cases[0]
        response_lines.append(
            f"**Highest Priority Matter**: **{top_urgent[2]}** (`{top_urgent[1]}`)\n"
            f"• **Client**: {top_urgent[3]}\n"
            f"• **Court**: {top_urgent[4]}\n"
            f"• **Priority / Status**: {top_urgent[5].upper()} / {top_urgent[6]}\n"
            f"• **Next Hearing**: {top_urgent[7]}" + (f" (in {top_urgent[8]} days)" if top_urgent[8] is not None else "") + "\n"
            f"• **Focus**: {top_urgent[9] or 'Preliminary hearing preparation and injunction review.'}\n"
        )
    else:
        top_matter = rows[0]
        response_lines.append(
            f"**Current Matter of Attention**: **{top_matter[2]}** (`{top_matter[1]}`)\n"
            f"• **Next Hearing**: {top_matter[7]}\n"
        )

    if upcoming_hearings:
        response_lines.append("**Upcoming Scheduled Hearings**:")
        for r in upcoming_hearings[:4]:
            days_str = f" [in {r[8]} days]" if r[8] is not None else ""
            response_lines.append(f"• **{r[2]}** (`{r[1]}`): {r[7]}{days_str} — *{r[4]}*")
        response_lines.append("")

    response_lines.append("*To analyze case documents, evidentiary gaps, or hearing strategy for a specific matter, open the matter in Case Files.*")
    return "\n".join(response_lines)


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
    """Executes Query Router followed by Conversational Generation or full LegalAI RAG Pipeline."""
    global pipeline, case_rag_pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="LegalAI RAG Pipeline is initializing")

    t0 = time.time()
    router = get_query_router()
    route_result = router.classify(req.content, conversation_history=req.history)

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

    # Route 1: CONVERSATIONAL
    if route_result.intent == QueryIntent.CONVERSATIONAL:
        answer_text = await asyncio.to_thread(
            generate_conversational_response,
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
    effective_case_id = req.caseId or (req.selectedCases[0] if (req.selectedCases and len(req.selectedCases) > 0) else None) or req.caseNumber
    cid, cnum = resolve_case_identifier(effective_case_id)
    rag_case_id = get_best_rag_case_id(case_rag_pipeline, cid, cnum) or effective_case_id
    is_case_intent = route_result.intent in (QueryIntent.CASE_QUERY, QueryIntent.HEARING_PREPARATION)

    if is_case_intent:
        if not rag_case_id:
            answer_text = generate_case_guidance(None)
            sources = []
            rel = "supported"
            rel_label = "Case Guidance"
            conf_status = "CASE_GUIDANCE"
        elif case_rag_pipeline:
            logger.info(f"Trace Single Matter: context={req.mode or 'SINGLE_CASE'}, case_id={rag_case_id}, route={route_result.intent.value}, retrieval=CASE_RAG, adapter=case_analysis_v1")
            print(f"[TRACE] context={req.mode or 'SINGLE_CASE'} | case_id={rag_case_id} | route={route_result.intent.value} | retrieval=CASE_RAG | adapter=case_analysis_v1")
            async with model_concurrency_lock:
                case_analysis = await asyncio.to_thread(
                    case_rag_pipeline.answer_case_question,
                    question=req.content,
                    case_id=rag_case_id,
                    top_k=6,
                    max_new_tokens=512
                )
            answer_text = case_analysis.answer
            sources = case_analysis.case_sources + case_analysis.legal_sources
            rel = case_analysis.reliability
            rel_label = case_analysis.reliability_label
            conf_status = case_analysis.confidence_status
            matter_guidance = generate_case_guidance(rag_case_id)
            if "Case Matter:" in matter_guidance and not answer_text.startswith("**Case Matter:**"):
                answer_text = f"{matter_guidance}\n\n---\n\n{answer_text}"
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
                history=req.history,
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
                "reliabilityLabel": "Conversational Greeting",
                "sources": [],
                "citations": [],
                "requires_verification": False,
                "confidence_status": "CONVERSATIONAL",
                "evidence_status": "CONVERSATIONAL",
                "generation_time_sec": round(time.time() - t0, 3)
            }
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2: OUT_OF_SCOPE / GENERAL_NON_LEGAL
        if route_result.intent in (QueryIntent.OUT_OF_SCOPE, QueryIntent.GENERAL_NON_LEGAL):
            answer_text = generate_out_of_scope_response(
                message=req.content,
                history=req.history
            )
            words = answer_text.split(" ")
            current_text = ""
            for i, word in enumerate(words):
                current_text += (word if i == 0 else " " + word)
                token_payload = {"token": current_text}
                yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
                await asyncio.sleep(0.012)

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
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2B: AMBIGUOUS
        if route_result.intent == QueryIntent.AMBIGUOUS:
            answer_text = generate_ambiguous_response(
                message=req.content,
                history=req.history
            )
            words = answer_text.split(" ")
            current_text = ""
            for i, word in enumerate(words):
                current_text += (word if i == 0 else " " + word)
                token_payload = {"token": current_text}
                yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
                await asyncio.sleep(0.012)

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
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2C: SYSTEM_INFO (Verified Architectural Context, Zero RAG)
        if route_result.intent == QueryIntent.SYSTEM_INFO:
            answer_text = generate_system_info_response(req.content)
            words = answer_text.split(" ")
            current_text = ""
            for i, word in enumerate(words):
                current_text += (word if i == 0 else " " + word)
                token_payload = {"token": current_text}
                yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
                await asyncio.sleep(0.012)

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
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2D: TECHNICAL_AI (Base Qwen Conceptual Explanation, LoRA Disabled, Zero RAG)
        if route_result.intent == QueryIntent.TECHNICAL_AI:
            async with model_concurrency_lock:
                answer_text = await asyncio.to_thread(
                    generate_base_qwen_technical_response,
                    pipeline=pipeline,
                    message=req.content,
                    history=req.history,
                    max_new_tokens=256
                )
            words = answer_text.split(" ")
            current_text = ""
            for i, word in enumerate(words):
                current_text += (word if i == 0 else " " + word)
                token_payload = {"token": current_text}
                yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
                await asyncio.sleep(0.012)

            complete_payload = {
                "id": f"msg-{int(time.time() * 1000)}",
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
                "generation_time_sec": round(time.time() - t0, 3)
            }
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 2E: CASE_MANAGEMENT (Application DB cases table, Zero Case RAG)
        if route_result.intent == QueryIntent.CASE_MANAGEMENT:
            effective_case_id = req.caseId or (req.selectedCases[0] if (req.selectedCases and len(req.selectedCases) > 0) else None) or req.caseNumber
            answer_text = generate_case_management_response(req.content, active_case_id=effective_case_id)
            words = answer_text.split(" ")
            current_text = ""
            for i, word in enumerate(words):
                current_text += (word if i == 0 else " " + word)
                token_payload = {"token": current_text}
                yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
                await asyncio.sleep(0.012)

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
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 3: CASE_QUERY or HEARING_PREPARATION (Strictly semantic intent or explicit single-case inquiry)
        effective_case_id = req.caseId or (req.selectedCases[0] if (req.selectedCases and len(req.selectedCases) > 0) else None) or req.caseNumber
        cid, cnum = resolve_case_identifier(effective_case_id)
        rag_case_id = get_best_rag_case_id(case_rag_pipeline, cid, cnum) or effective_case_id
        is_case_intent = route_result.intent in (QueryIntent.CASE_QUERY, QueryIntent.HEARING_PREPARATION)

        if is_case_intent:
            if not rag_case_id:
                answer_text = generate_case_guidance(None)
                sources = []
                rel = "supported"
                rel_label = "Case Guidance"
                conf_status = "CASE_GUIDANCE"
            elif case_rag_pipeline:
                logger.info(f"Trace Single Matter: context={req.mode or 'SINGLE_CASE'}, case_id={rag_case_id}, route={route_result.intent.value}, retrieval=CASE_RAG, adapter=case_analysis_v1")
                print(f"[TRACE] context={req.mode or 'SINGLE_CASE'} | case_id={rag_case_id} | route={route_result.intent.value} | retrieval=CASE_RAG | adapter=case_analysis_v1")
                async with model_concurrency_lock:
                    case_analysis = await asyncio.to_thread(
                        case_rag_pipeline.answer_case_question,
                        question=req.content,
                        case_id=rag_case_id,
                        top_k=6,
                        max_new_tokens=512
                    )
                answer_text = case_analysis.answer
                sources = case_analysis.case_sources + case_analysis.legal_sources
                rel = case_analysis.reliability
                rel_label = case_analysis.reliability_label
                conf_status = case_analysis.confidence_status
                matter_guidance = generate_case_guidance(rag_case_id)
                if "Case Matter:" in matter_guidance and not answer_text.startswith("**Case Matter:**"):
                    answer_text = f"{matter_guidance}\n\n---\n\n{answer_text}"
            else:
                answer_text = generate_case_guidance(rag_case_id)
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
                "generation_time_sec": round(time.time() - t0, 3)
            }
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

        # Stream Route 3: LEGAL_QUERY (Production Expanded Indian Legal Knowledge Pipeline)
        if indian_knowledge_pipeline:
            if indian_knowledge_bridge:
                is_foreign, redirect_resp = indian_knowledge_bridge.check_foreign_law_query(req.content)
                if is_foreign:
                    words = redirect_resp.split(" ")
                    current_text = ""
                    for i, word in enumerate(words):
                        current_text += (word if i == 0 else " " + word)
                        token_payload = {"token": current_text}
                        yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
                        await asyncio.sleep(0.012)

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

            words = full_answer.split(" ")
            current_text = ""
            for i, word in enumerate(words):
                current_text += (word if i == 0 else " " + word)
                token_payload = {"token": current_text}
                yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
                await asyncio.sleep(0.012)

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
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"
            return

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
        if has_greeting_prefix(req.content) and not full_answer.startswith("Absolutely!") and not full_answer.startswith("Hey"):
            full_answer = f"Absolutely! 👋\n\n{full_answer}"

        words = full_answer.split(" ")

        current_text = ""
        for i, word in enumerate(words):
            current_text += (word if i == 0 else " " + word)
            token_payload = {"token": current_text}
            yield f"event: token\ndata: {json.dumps(token_payload)}\n\n"
            await asyncio.sleep(0.015)

        rel, rel_label = map_reliability(rag_result)
        sources = format_sources(rag_result.get("retrieved_sources", []))

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
            "citations": rag_result.get("citations", []),
            "requires_verification": (rel == "verify"),
            "confidence_status": rag_result.get("confidence_status", ""),
            "evidence_status": rag_result.get("evidence_status", ""),
            "generation_time_sec": rag_result.get("generation_time_sec", 0.0),
            "intent": route_result.intent.value,
            "sub_intent": getattr(route_result, "sub_intent", "LEGAL_QUERY"),
            "legal_intent_confidence": getattr(route_result, "legal_intent_confidence", 0.95),
            "case_intent_confidence": getattr(route_result, "case_intent_confidence", 0.0),
            "resolved_act": req.act_filter,
            "provision_type": None,
            "provision_number": req.section_filter,
            "retrieval_mode": "LEGAL_RAG_FALLBACK",
            "retrieval_candidate_count": len(sources),
            "accepted_source_count": len(sources),
            "source_count": len(sources),
            "adapter": "outputs/qwen14b-legalai-v2",
            "qwen_invoked": True if sources else False,
            "abstained": (rel == "verify")
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
