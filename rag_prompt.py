"""
Nanakwaku Boateng Boakye-Akyeampong | Index: 10022200167
Prompt construction and context window management (truncate / rank).
"""

from __future__ import annotations

from dataclasses import dataclass

from rag_config import (
    MAX_CONTEXT_CHARS,
    MEMORY_ANSWER_PREVIEW_CHARS,
    MEMORY_MAX_CHARS,
    MEMORY_MAX_TURNS,
)
from rag_retrieve import RetrievedChunk


SYSTEM_PROMPT_STRICT = """You are an assistant for Academic City University.
Answer using ONLY the provided CONTEXT. If the context is insufficient, say so clearly
and do not invent numbers, candidates, parties, budget figures, or policies.
When you use facts, tie them to the source tag shown in brackets (e.g. [election_csv] or [budget_pdf]).
Write clearly and concisely."""

SYSTEM_PROMPT_CONCISE = """You are an assistant for Academic City University.
Use ONLY the CONTEXT. If missing, reply: "Not found in provided documents."
Keep answers under 120 words. Reference chunk tags when stating numbers."""

PROMPT_VARIANTS = {
    "strict_anti_hallucination": SYSTEM_PROMPT_STRICT,
    "concise_not_found": SYSTEM_PROMPT_CONCISE,
}


def format_conversation_memory(
    prior_turns: list[tuple[str, str]],
    max_turns: int = MEMORY_MAX_TURNS,
    max_total_chars: int = MEMORY_MAX_CHARS,
    answer_preview: int = MEMORY_ANSWER_PREVIEW_CHARS,
) -> str:
    """
    Turn (query, answer) pairs from earlier in the browser session.
    Used for follow-up resolution only; does not replace retrieved CONTEXT.
    """
    if not prior_turns:
        return ""
    tail = prior_turns[-max_turns:]
    blocks: list[str] = []
    total = 0
    for i, (q, a) in enumerate(tail, 1):
        a_short = (a[:answer_preview] + "…") if len(a) > answer_preview else a
        block = f"[Turn {i}] User: {q.strip()}\nAssistant: {a_short.strip()}"
        if total + len(block) + 2 > max_total_chars and blocks:
            break
        blocks.append(block)
        total += len(block) + 2
    return "\n\n".join(blocks)


def _tagged_block(r: RetrievedChunk) -> str:
    tag = r.chunk.source
    return f"[{tag} | id={r.chunk.chunk_id}]\n{r.chunk.text.strip()}"


@dataclass
class BuiltPrompt:
    system: str
    user: str
    context_blocks: list[str]
    truncated: bool


def build_messages(
    user_query: str,
    retrieved: list[RetrievedChunk],
    max_chars: int = MAX_CONTEXT_CHARS,
    prompt_variant: str = "strict_anti_hallucination",
    conversation_memory: str | None = None,
) -> BuiltPrompt:
    """
    Context window management: chunks are already ranked; we add in order until
    max_chars is reached (greedy packing).
    """
    blocks: list[str] = []
    used = 0
    truncated = False
    for r in retrieved:
        piece = _tagged_block(r)
        sep_len = 2
        if used + len(piece) + sep_len > max_chars:
            truncated = True
            break
        blocks.append(piece)
        used += len(piece) + sep_len

    context_str = "\n\n".join(blocks) if blocks else "(no context retrieved)"
    system = PROMPT_VARIANTS.get(prompt_variant, PROMPT_VARIANTS["strict_anti_hallucination"])
    mem = (conversation_memory or "").strip()
    memory_block = ""
    if mem:
        memory_block = (
            "PRIOR CONVERSATION (session memory — use only to interpret follow-up questions, "
            "ellipsis, and pronouns. Do not treat prior assistant replies as ground truth; "
            "confirm numbers and names against CONTEXT below.)\n"
            f"{mem}\n\n"
        )
    user = (
        f"{memory_block}"
        f"CURRENT USER QUESTION:\n{user_query.strip()}\n\n"
        f"CONTEXT (retrieved documents):\n{context_str}\n\n"
        "Answer CURRENT USER QUESTION using CONTEXT. If CONTEXT lacks the answer, say so."
    )
    return BuiltPrompt(system=system, user=user, context_blocks=blocks, truncated=truncated)


def prompt_for_display(bp: BuiltPrompt) -> str:
    return f"[SYSTEM]\n{bp.system}\n\n[USER]\n{bp.user}"
