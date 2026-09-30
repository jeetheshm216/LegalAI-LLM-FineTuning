"""
src/api/llm_fallback.py

Unified Multi-Provider LLM Client with Strict Priority:
1. Primary: Local NVIDIA DGX vLLM (Qwen 32B + Custom LoRA on http://127.0.0.1:8009)
2. Automatic Fallback (Only if DGX is disconnected/declined): Google Gemini API (gemini-3.5-flash / gemini-3.1-flash-lite)
"""

import json
import logging
import os
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("LegalAI-LLMFallback")

VLLM_URL = os.getenv("VLLM_URL", "http://127.0.0.1:8009/v1/chat/completions")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_PREFERRED_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite"
]


def call_vllm(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 1500) -> Optional[str]:
    """Attempts generation via local DGX vLLM."""
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
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.warning(f"vLLM query failed or timed out: {e}. Falling back to Cloud API...")
        return None


def call_gemini(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 1500) -> Optional[str]:
    """Fallback to Google Gemini API (tested and verified with user key)."""
    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        return None

    system_instruction = ""
    contents = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            system_instruction += content + "\n\n"
        elif role == "assistant":
            contents.append({"role": "model", "parts": [{"text": content}]})
        else:
            contents.append({"role": "user", "parts": [{"text": content}]})

    for model_name in GEMINI_PREFERRED_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        if system_instruction.strip():
            body["systemInstruction"] = {
                "parts": [{"text": system_instruction.strip()}]
            }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        logger.info(f"Successfully generated response using Google Gemini fallback ({model_name}).")
                        return parts[0].get("text", "").strip()
        except Exception as e:
            logger.warning(f"Gemini model {model_name} call failed: {e}. Trying next...")
            continue

    return None


def query_llm_with_fallback(
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 1500
) -> str:
    """
    STRICT PRIORITY:
    1. Local DGX NVIDIA GPU (vLLM Qwen 32B + Custom LoRA)
    2. Google Gemini API (Only if DGX NVIDIA GPU is offline or unavailable)
    """
    # 1. Primary: Local NVIDIA GPU vLLM
    result = call_vllm(messages, temperature=temperature, max_tokens=max_tokens)
    if result:
        return result

    # 2. Secondary: Gemini Fallback
    result = call_gemini(messages, temperature=temperature, max_tokens=max_tokens)
    if result:
        return result

    return (
        "Inference Notice: Local NVIDIA GPU service is currently unreachable and Gemini fallback quota was exceeded."
    )
