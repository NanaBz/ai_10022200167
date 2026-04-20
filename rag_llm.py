"""
Nanakwaku Boateng Boakye-Akyeampong | Index: 10022200167
LLM generation via OpenAI API (no LangChain).
"""

from __future__ import annotations

import logging
import os
from typing import Any

from openai import OpenAI

from rag_config import OPENAI_MODEL
from rag_prompt import BuiltPrompt

log = logging.getLogger(__name__)


def _usage_to_dict(usage: Any) -> dict[str, Any] | None:
    """OpenAI returns CompletionUsage objects; JSON logs need plain dicts."""
    if usage is None:
        return None
    if isinstance(usage, dict):
        return usage
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "dict"):  # older pydantic
        return usage.dict()
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }


def get_client() -> OpenAI | None:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    return OpenAI(api_key=key)


def generate_rag_answer(bp: BuiltPrompt) -> tuple[str, dict[str, Any]]:
    client = get_client()
    meta: dict[str, Any] = {"model": OPENAI_MODEL, "mode": "rag"}
    if client is None:
        return (
            "OPENAI_API_KEY is not set. Add your key to the environment (or use the "
            "sidebar field in the Streamlit app) to enable generation. Retrieval still works.",
            {**meta, "error": "missing_api_key"},
        )
    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": bp.system},
                {"role": "user", "content": bp.user},
            ],
            temperature=0.2,
        )
        text = (resp.choices[0].message.content or "").strip()
        meta["usage"] = _usage_to_dict(getattr(resp, "usage", None))
        return text, meta
    except Exception as e:
        log.exception("OpenAI call failed")
        return f"LLM error: {e}", {**meta, "error": str(e)}


def generate_baseline_no_context(user_query: str) -> tuple[str, dict[str, Any]]:
    """Pure LLM path for Part E comparisons (no retrieval)."""
    client = get_client()
    meta: dict[str, Any] = {"model": OPENAI_MODEL, "mode": "baseline_no_context"}
    if client is None:
        return (
            "OPENAI_API_KEY not set; cannot run baseline.",
            {**meta, "error": "missing_api_key"},
        )
    prompt = (
        "Answer briefly. WARNING: no external context is provided; do not invent "
        f"specific Ghana election or 2025 budget facts.\n\nQUESTION:\n{user_query}"
    )
    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        text = (resp.choices[0].message.content or "").strip()
        meta["usage"] = _usage_to_dict(getattr(resp, "usage", None))
        return text, meta
    except Exception as e:
        return f"LLM error: {e}", {**meta, "error": str(e)}
