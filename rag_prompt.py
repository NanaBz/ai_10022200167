"""
Nanakwaku Boateng Boakye-Akyeampong | Index: 10022200167
Prompt construction and context window management (truncate / rank).
"""

from __future__ import annotations

from dataclasses import dataclass

from rag_config import MAX_CONTEXT_CHARS
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
    user = (
        f"USER QUESTION:\n{user_query.strip()}\n\n"
        f"CONTEXT:\n{context_str}\n\n"
        "Answer the question using the context. If context lacks the answer, say you cannot find it."
    )
    return BuiltPrompt(system=system, user=user, context_blocks=blocks, truncated=truncated)


def prompt_for_display(bp: BuiltPrompt) -> str:
    return f"[SYSTEM]\n{bp.system}\n\n[USER]\n{bp.user}"
