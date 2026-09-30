"""
src/courtroom/multi_agent_engine.py

Neural Courtroom Multi-Agent Simulation Engine powered by Qwen 32B.
Arbiter of turn-taking, procedural intent, anti-hallucination case grounding,
evidentiary objections, judicial reprimands, and live bench scoring.
"""

import json
import logging
import random
import re
import urllib.request
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.courtroom.speech_normalizer import normalize_courtroom_speech

logger = logging.getLogger("LegalAI-Courtroom")

VLLM_URL = "http://127.0.0.1:8009/v1/chat/completions"


class CourtroomTurnRequest(BaseModel):
    session_id: str
    case_id: Optional[str] = "2024-CV-1187"
    mode: str = "WITNESS_EXAMINATION"  # "WITNESS_EXAMINATION" | "SUBMISSIONS_ARGUMENT" | "BAIL_HEARING"
    advocate_input: str
    advocate_audio_url: Optional[str] = None
    witness_name: Optional[str] = "Inspector Vikram Rathore (IO)"
    witness_composure: int = 85
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)


def query_llm(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 400) -> str:
    """Send prompt to active local LLM (vLLM Qwen2.5-32B) with graceful timeout handling."""
    payload = {
        "model": "Qwen/Qwen2.5-32B-Instruct",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        req = urllib.request.Request(
            VLLM_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.warning(f"vLLM query failed or timed out: {e}.")
        return ""


def clean_json_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Robustly extracts JSON object from LLM output, handling markdown blocks or extraneous text."""
    if not raw_text:
        return None
    try:
        m = re.search(r"(\{[\s\S]*\})", raw_text)
        if m:
            clean_str = m.group(1).strip()
            return json.loads(clean_str)
    except Exception as e:
        logger.error(f"Failed to parse JSON from LLM: {e}. Raw text: {raw_text[:200]}")
    return None


class CourtroomSimulationEngine:
    def __init__(self):
        pass

    def arbitrate_courtroom_turn(
        self,
        advocate_text: str,
        case_info: Dict[str, Any],
        mode: str,
        witness_name: str,
        current_composure: int,
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Master neural arbiter using Qwen 32B to understand the situation deeply:
          - Analyzes the advocate's submission in light of case pleadings, jurisdiction, and procedural stage.
          - Decides who speaks, when to speak, and when to interrupt.
          - Returns a strictly ordered sequence of events to speak sequentially without voice collision.
        """
        clean_input = normalize_courtroom_speech(advocate_text.strip())
        case_title = case_info.get("title", "Martinez v. Coastal Holdings Ltd.")
        case_court = case_info.get("court", "Commercial Division, High Court of Delhi")
        case_bench = case_info.get("bench", "Hon'ble Justice Rekha Palli (Presiding)")
        opp_counsel = case_info.get("opposing_counsel", "Sr. Adv. Harish Salve")
        case_brief = case_info.get("brief", "Commercial suit seeking urgent interim injunction under Order 39 CPC against alienation of coastal logistics assets.")

        system_prompt = f"""You are the Master Judicial Arbiter and Simulation Engine for an Indian Courtroom hearing {case_title}.
Court: {case_court}
Bench: {case_bench}
Opposing Counsel: {opp_counsel}
Witness in the Box: {witness_name}
Case Brief: {case_brief}
Current Hearing Mode: {mode}

ROLES:
- The human user is the ADVOCATE appearing for the Petitioner / Applicant.
- OPPONENT is Senior Advocate appearing for the Respondent.
- JUDGE is the Hon'ble Presiding Judge.

DEEP PROCEDURAL & CONVERSATIONAL REASONING RULES:
1. COURTROOM ETIQUETTE, APOLOGIES & DEFERENCE (turn_category: "DECORUM_APOLOGY"):
   - When the Advocate apologizes, acknowledges a correction, or expresses deference (e.g. "I'm sorry my Lord", "I apologize", "I stand corrected", "Forgive me, My Lord", "Much obliged", "As Your Lordship pleases"):
     * Who speaks: ONLY the JUDGE.
     * Opposing Counsel: Remains seated and silent. (An apology is NEVER an "irrelevant allegation" or grounds for objection!).
     * Judge Response: Acknowledges the apology with judicial decorum and invites counsel to proceed with their next substantive point on the merits.
     * score_delta: 0 (or +5 for restoring composure and respecting court etiquette).

2. COUNSEL APPEARANCE / INTRODUCTION (turn_category: "APPEARANCE"):
   - When the Advocate states their name or enters appearance (e.g. "I am Jeethesh", "My name is Jitesh appearing for the petitioner", "Good morning My Lord"):
     * Who speaks: The JUDGE speaks FIRST to record appearance on the cause list and ask counsel to state the urgent relief.
     * Opposing Counsel merely enters their appearance on behalf of the Respondent.
     * CRITICAL: DO NOT hallucinate a 5-paragraph merits rebuttal or cite statutory precedents when counsel has only stated their name!

3. FACTUAL / JURISDICTIONAL BLUNDER (turn_category: "BLUNDER"):
   - When the Advocate raises scandalous, off-case, or criminal claims in a civil/commercial dispute (e.g. alleging murder, stabbing, blood, homicide, or narcotics):
     * Who speaks: The OPPOSING COUNSEL immediately interrupts with a fierce objection ('Scandalous and irrelevant allegation!').
     * Followed by the JUDGE reprimanding counsel for abusing judicial time and failing to read the pleadings.
     * score_delta MUST be -15.

4. WITNESS CROSS-EXAMINATION (turn_category: "CROSS_EXAMINATION"):
   - When asking questions to the witness in the box:
     * If question is argumentative or hearsay: OPPOSING COUNSEL objects, JUDGE rules (Sustained or Overruled).
     * If allowed: The WITNESS answers from the box. Composure degrades by -5 to -20 points if sharp contradiction or documentary exhibit is cited.

5. SUBSTANTIVE LEGAL ARGUMENT (turn_category: "MERITS_ARGUMENT"):
   - Advocate presents arguments on Order 39, Section 9, prima facie case, balance of convenience:
     * OPPOSING COUNSEL delivers a sharp, technical 2-3 sentence counter-rebuttal.
     * JUDGE follows with a challenging bench query.

Respond ONLY with valid JSON in this schema (no markdown outside the JSON):
{{
  "turn_category": "DECORUM_APOLOGY" | "APPEARANCE" | "BLUNDER" | "CROSS_EXAMINATION" | "MERITS_ARGUMENT" | "PROCEDURAL",
  "score_delta": 0,
  "composure_delta": 0,
  "events": [
    {{
      "speaker": "JUDGE" | "OPPONENT" | "WITNESS",
      "speaker_name": "{case_bench}" | "{opp_counsel}" | "{witness_name}",
      "badge": "Short badge title",
      "text": "Exact spoken courtroom dialogue"
    }}
  ]
}}
"""

        messages = [
            {"role": "system", "content": system_prompt}
        ]
        for h in history[-3:]:
            messages.append(h)
        messages.append({"role": "user", "content": f"Advocate for Petitioner says: {clean_input}"})

        raw_llm = query_llm(messages, temperature=0.2, max_tokens=400)
        parsed = clean_json_response(raw_llm)

        if not parsed or not parsed.get("events"):
            logger.warning("Falling back to expert rule-based turn-taking arbiter.")
            parsed = self._fallback_arbitration(
                clean_input=clean_input,
                case_info=case_info,
                mode=mode,
                witness_name=witness_name,
                current_composure=current_composure
            )

        comp_delta = parsed.get("composure_delta", 0)
        new_composure = max(10, min(100, current_composure + comp_delta))

        return {
            "intent": parsed.get("turn_category", "PROCEDURAL"),
            "normalized_input": clean_input,
            "score_delta": parsed.get("score_delta", 0),
            "events": parsed.get("events", []),
            "witness_state": {
                "witness_name": witness_name,
                "composure": new_composure,
                "composure_delta": comp_delta,
                "cornered": new_composure < 40
            }
        }

    def _fallback_arbitration(
        self,
        clean_input: str,
        case_info: Dict[str, Any],
        mode: str,
        witness_name: str,
        current_composure: int
    ) -> Dict[str, Any]:
        """High-reliability parametric fallback if vLLM service experiences temporary latency."""
        lower = clean_input.lower()
        case_title = case_info.get("title", "Martinez v. Coastal Holdings Ltd.")
        case_bench = case_info.get("bench", "Hon'ble Justice Rekha Palli")
        opp_counsel = case_info.get("opposing_counsel", "Sr. Adv. Harish Salve")

        # 1. Apologies & Courtroom Deference
        if any(w in lower for w in ["sorry", "apologize", "apologies", "stand corrected", "forgive me", "much obliged", "as your lordship pleases"]):
            return {
                "turn_category": "DECORUM_APOLOGY",
                "score_delta": 0,
                "composure_delta": 0,
                "events": [
                    {
                        "speaker": "JUDGE",
                        "speaker_name": case_bench,
                        "badge": "⚖️ Decorum Restored",
                        "text": "The apology is accepted, Counsel. Let us maintain professional decorum and proceed directly with your submissions on the merits."
                    }
                ]
            }

        # 2. Appearance / Introduction (exclude apology phrases)
        if any(w in lower for w in ["i am ", "i'm ", "my name is ", "appearing for", "represent", "good morning"]) and not any(w in lower for w in ["sorry", "apologize"]):
            name_m = re.search(r"(?:i am|i'm|my name is)\s+([a-zA-Z]+)", clean_input, re.IGNORECASE)
            counsel_salutation = f"Mr. {name_m.group(1).capitalize()}" if name_m else "Counsel"
            return {
                "turn_category": "APPEARANCE",
                "score_delta": 0,
                "composure_delta": 0,
                "events": [
                    {
                        "speaker": "JUDGE",
                        "speaker_name": case_bench,
                        "badge": "⚖️ Appearance Recorded",
                        "text": f"Good morning, {counsel_salutation}. Your appearance on behalf of the Petitioner is noted on the board. The Court is hearing {case_title}. Please apprise the Bench of the immediate urgency."
                    },
                    {
                        "speaker": "OPPONENT",
                        "speaker_name": opp_counsel,
                        "badge": "👔 Respondent Appearance",
                        "text": "May it please the Court, I appear on behalf of the Respondent, Coastal Holdings Ltd., along with my juniors."
                    }
                ]
            }

        # 3. Blunder (e.g. murder in commercial case)
        if any(w in lower for w in ["murder", "murdered", "killed", "homicide", "blood", "stabbing"]):
            return {
                "turn_category": "BLUNDER",
                "score_delta": -15,
                "composure_delta": 0,
                "events": [
                    {
                        "speaker": "OPPONENT",
                        "speaker_name": opp_counsel,
                        "badge": "⚡ Objection: Irrelevant Allegation",
                        "text": "My Lord, I must vehemently object! This is a commercial equity petition. My learned friend is raising baseless criminal allegations that have zero relevance to the pleadings."
                    },
                    {
                        "speaker": "JUDGE",
                        "speaker_name": case_bench,
                        "badge": "⚠️ Judicial Reprimand",
                        "text": "Sustained. Advocate, you are warned to maintain decorum and stick strictly to the commercial dispute. Points have been docked for scandalous questioning."
                    }
                ]
            }

        # 4. Witness Examination
        if mode == "WITNESS_EXAMINATION" or "witness" in lower or "exhibit" in lower or "log" in lower or "diary" in lower:
            comp_delta = -15 if any(k in lower for k in ["gap", "exhibit", "discrepancy", "contradiction", "log"]) else -5
            return {
                "turn_category": "CROSS_EXAMINATION",
                "score_delta": 0,
                "composure_delta": comp_delta,
                "events": [
                    {
                        "speaker": "WITNESS",
                        "speaker_name": witness_name,
                        "badge": f"Deposition: Composure {current_composure + comp_delta}%",
                        "text": "Sir, to the best of my recollection, the dispatch logs were maintained by the shift supervisor in the regular course of business. There was no intentional omission."
                    }
                ]
            }

        # 5. Merits argument
        return {
            "turn_category": "MERITS_ARGUMENT",
            "score_delta": 0,
            "composure_delta": 0,
            "events": [
                {
                    "speaker": "OPPONENT",
                    "speaker_name": opp_counsel,
                    "badge": "👔 Rebuttal Submission",
                    "text": "My Lord, the petitioner has completely failed to establish a prima facie case. An injunction at this interim stage would cause irreparable commercial prejudice to my client."
                },
                {
                    "speaker": "JUDGE",
                    "speaker_name": case_bench,
                    "badge": "⚖️ Bench Query",
                    "text": "Mr. Counsel, what is your answer to the Respondent's objection regarding the balance of convenience and the availability of damages?"
                }
            ]
        }

    def generate_bench_scorecard(
        self,
        session_history: List[Dict[str, Any]],
        case_title: str
    ) -> Dict[str, Any]:
        """Evaluates the courtroom trial hearing performance and applies penalties for blunders."""
        total_turns = len(session_history)
        if total_turns == 0:
            return {
                "argument_solidity": 70,
                "statutory_accuracy": 70,
                "cross_exam_sharpness": 68,
                "courtroom_demeanor": 75,
                "procedural_compliance": 70,
                "overall_score": 71,
                "bench_verdict": "Orders Reserved",
                "strengths": ["Clear opening articulation"],
                "improvements": ["Cite specific sections under the new Bharatiya Sakshya Adhiniyam, 2023"],
            }

        advocate_texts = [turn.get("advocate_text", "") for turn in session_history]
        combined = " ".join(advocate_texts).lower()

        statute_citations = sum(1 for kw in ["section", "order", "article", "bns", "bnss", "bsa", "cpc", "crpc", "act"] if kw in combined)
        precedent_citations = sum(1 for kw in ["v.", "versus", "supreme court", "high court", "held", "ratio", "bench"] if kw in combined)
        cross_exam_tools = sum(1 for kw in ["exhibit", "contradiction", "statement", "memo", "time", "date", "confront", "diary", "discrepancy"] if kw in combined)

        total_penalties = sum(abs(turn.get("score_delta", 0)) for turn in session_history if turn.get("score_delta", 0) < 0)
        has_blunder = total_penalties > 0 or (any(w in combined for w in ["murder", "murdered", "homicide", "kill"]) and ("martinez" in case_title.lower() or "coastal" in case_title.lower()))
        penalty = max(total_penalties, 25 if has_blunder else 0)

        arg_score = max(30, min(98, 65 + (total_turns * 3) + (precedent_citations * 5) - penalty))
        stat_score = max(30, min(96, 58 + (statute_citations * 6) - penalty))
        cross_score = max(35, min(95, 60 + (cross_exam_tools * 6)))
        demeanor_score = max(35, min(97, 75 + (10 if "my lord" in combined or "your honour" in combined else 0) - (20 if has_blunder else 0)))
        proc_score = max(30, min(94, 68 + (precedent_citations * 4) - penalty))

        overall = round((arg_score + stat_score + cross_score + demeanor_score + proc_score) / 5.0)

        verdict = "Bench Strongly in Favor" if overall >= 85 else ("Orders Reserved (Substantial Merits)" if overall >= 72 else "Bench Skeptical / Notice Declined")

        strengths = []
        if precedent_citations >= 2:
            strengths.append("Effective judicial citation and persuasive reliance on binding precedents.")
        if cross_exam_tools >= 2:
            strengths.append("Sharp witness confrontation with documentary exhibits and contemporaneous records.")
        if "my lord" in combined or "your honour" in combined:
            strengths.append("Exemplary courtroom etiquette and deferential advocacy towards the Bench.")
        if not strengths:
            strengths.append("Maintained consistent line of factual narrative throughout the hearing.")

        improvements = []
        if has_blunder:
            improvements.append("Align arguments strictly with the pleadings; do not confuse commercial corporate disputes with criminal offenses.")
        if statute_citations < 2:
            improvements.append("Directly cite relevant sections under the new Bharatiya Sakshya Adhiniyam, 2023 or Civil Procedure Code.")
        if cross_exam_tools < 1:
            improvements.append("Confront the witness directly with discrepancies in the case diary or prior depositions.")
        if not improvements:
            improvements.append("Refine closing prayer to request specific ad-interim reliefs under Order 39 Rule 2.")

        return {
            "argument_solidity": arg_score,
            "statutory_accuracy": stat_score,
            "cross_exam_sharpness": cross_score,
            "courtroom_demeanor": demeanor_score,
            "procedural_compliance": proc_score,
            "overall_score": overall,
            "bench_verdict": verdict,
            "strengths": strengths,
            "improvements": improvements,
        }


courtroom_engine = CourtroomSimulationEngine()
