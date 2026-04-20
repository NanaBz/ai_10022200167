"""
Nanakwaku Boateng Boakye-Akyeampong | Index: 10022200167
CS4241 — Streamlit UI for manual RAG (retrieval + prompt + LLM + logging).
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

import streamlit as st

from rag_config import FINAL_CONTEXT_CHUNKS, LOG_DIR, PROJECT_ROOT
from rag_llm import generate_baseline_no_context, generate_rag_answer
from rag_prompt import build_messages, format_conversation_memory, prompt_for_display
from rag_retrieve import RetrievalPipeline, try_load_or_build_index

# --- Logging setup (Part D: pipeline logging) ---
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "rag_pipeline.log"


def _setup_file_logging() -> None:
    root = logging.getLogger()
    if getattr(root, "_rag_file_handler_configured", False):
        return
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    root.addHandler(fh)
    root.setLevel(logging.INFO)
    root._rag_file_handler_configured = True  # type: ignore[attr-defined]


_setup_file_logging()
log = logging.getLogger("ca_10022200167")

# --- Product copy (UI only; logic keys unchanged) ---
APP_NAME = "Nkabom Lens"
APP_TAGLINE = "Grounded answers from Ghana’s election data & the 2025 national budget."
STYLE_LABELS = {
    "strict_anti_hallucination": "Thorough — prefers quotes & source tags",
    "concise_not_found": "Brief — tight ‘not found’ when unsure",
}


def _inject_app_styles() -> None:
    st.markdown(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', 'Segoe UI', system-ui, sans-serif; }
  [data-testid="stAppViewContainer"] {
    background: radial-gradient(1200px 600px at 10% -10%, rgba(201,162,39,0.08), transparent),
                radial-gradient(800px 400px at 90% 0%, rgba(46,125,95,0.12), transparent),
                linear-gradient(180deg, #0c0f14 0%, #121820 100%);
  }
  [data-testid="stHeader"] { background: transparent; }
  div.block-container { padding-top: 1.75rem; }
  .nk-hero {
    border: 1px solid rgba(201,162,39,0.25);
    border-radius: 16px;
    padding: 1.25rem 1.5rem 1.1rem 1.5rem;
    margin-bottom: 1.25rem;
    background: linear-gradient(135deg, rgba(21,26,34,0.95), rgba(18,22,30,0.85));
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
  }
  .nk-hero h1 {
    margin: 0 0 0.35rem 0;
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #f2e6c9, #c9a227);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .nk-tagline { margin: 0; color: #9aa3b2; font-size: 1rem; line-height: 1.45; }
  .nk-foot { font-size: 0.78rem; color: #6b7280; margin-top: 0.75rem; }
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #121820 0%, #0e1218 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
  }
  [data-testid="stSidebar"] .stMarkdown h2 { font-size: 0.95rem; color: #c9a227; letter-spacing: 0.02em; }
  div[data-testid="stExpander"] details summary { font-weight: 600; }
</style>
""",
        unsafe_allow_html=True,
    )


def _retrieval_query_with_memory(
    user_q: str,
    prior_pairs: list[tuple[str, str]],
    memory_on: bool,
) -> str:
    """
    When conversational memory is on, anchor short / anaphoric follow-ups to the
    last explicit user question so FAISS sees terms like region/year/candidate.
    Displayed chat text stays `user_q`; only the retrieval embedding uses this.
    """
    if not memory_on or not prior_pairs:
        return user_q.strip()
    last_q = prior_pairs[-1][0].strip()
    return f"{last_q}\nFollow-up: {user_q.strip()}"


def _init_session() -> None:
    if "boosted_sources" not in st.session_state:
        st.session_state.boosted_sources = set()
    if "run_log" not in st.session_state:
        st.session_state.run_log = []
    if "turns" not in st.session_state:
        st.session_state.turns = []
    if "pipeline_ready" not in st.session_state:
        st.session_state.pipeline_ready = False
    if "use_conversational_memory" not in st.session_state:
        st.session_state.use_conversational_memory = False


@st.cache_resource(show_spinner=True)
def _load_index_bundle(force_rebuild: bool):
    return try_load_or_build_index(force_rebuild=force_rebuild)


def _render_turn(turn: dict) -> None:
    with st.chat_message("user"):
        st.write(turn["query"])
    with st.chat_message("assistant"):
        st.markdown("**Answer**")
        st.write(turn["answer"])
        with st.expander("Source passages & scores", expanded=False):
            for ch in turn["chunks"]:
                st.markdown(
                    f"**{ch['id']}** · `{ch['source']}` · "
                    f"faiss={ch['faiss']:.4f} · rerank={ch['rerank']} · fused={ch['fused']:.4f}"
                )
                prev = ch.get("preview", "")
                st.caption(prev + ("…" if ch.get("truncated_preview") else ""))
        with st.expander("Full prompt sent to the model"):
            st.code(turn["prompt"], language="text")
        with st.expander("Run trace (JSON)"):
            st.json(turn["run_entry"])
        if turn.get("baseline"):
            with st.expander("Comparison: same question, no documents"):
                st.write(turn["baseline"]["text"])
                st.json(turn["baseline"]["meta"])


def main() -> None:
    st.set_page_config(
        page_title=f"{APP_NAME} · Grounded Q&A",
        page_icon="◉",
        layout="wide",
    )
    _inject_app_styles()
    _init_session()

    st.markdown(
        f"""
<div class="nk-hero">
  <h1>{APP_NAME}</h1>
  <p class="nk-tagline">{APP_TAGLINE}</p>
  <p class="nk-foot">Built for CS4241 · Nanakwaku Boateng Boakye-Akyeampong · 10022200167</p>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("##### Settings")
        api_key = st.text_input(
            "OpenAI API key",
            type="password",
            placeholder="sk-…",
            help="Only stored in this browser session unless you set OPENAI_API_KEY on your machine.",
        )
        if api_key.strip():
            os.environ["OPENAI_API_KEY"] = api_key.strip()

        force_rebuild = st.checkbox("Rebuild search index from files", value=False)
        if st.button("Reload index", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

        st.markdown("---")
        st.markdown("##### Prefer a data source")
        st.caption("Nudge retrieval toward election tables or budget text for this session.")
        b_election = st.checkbox("Election results (CSV)", value=False)
        b_budget = st.checkbox("2025 budget (PDF)", value=False)
        st.session_state.boosted_sources = set()
        if b_election:
            st.session_state.boosted_sources.add("election_csv")
        if b_budget:
            st.session_state.boosted_sources.add("budget_pdf")

        st.markdown("---")
        st.markdown("##### Conversation")
        use_conversational_memory = st.checkbox(
            "Remember earlier turns this session",
            value=False,
            help=(
                "Helps short follow-ups (“What about the runner-up?”) by carrying prior "
                "questions into retrieval and the prompt. Turn off for isolated questions."
            ),
        )
        st.session_state.use_conversational_memory = use_conversational_memory

        st.markdown("---")
        with st.expander("Paths (debug)"):
            st.code(str(PROJECT_ROOT), language=None)
            st.code(str(LOG_FILE), language=None)

    with st.spinner("Loading embedding models and FAISS index (first run may download data)..."):
        vindex, cross = _load_index_bundle(force_rebuild=force_rebuild)
    retriever = RetrievalPipeline(vindex, cross)
    st.session_state.pipeline_ready = True

    c1, c2 = st.columns([1, 1])
    with c1:
        run_baseline = st.toggle(
            "Also show answer without your documents",
            value=False,
            help="Runs the same question through the model alone — useful to compare grounded vs guesswork.",
        )
    with c2:
        prompt_variant = st.selectbox(
            "Answer style",
            options=["strict_anti_hallucination", "concise_not_found"],
            index=0,
            format_func=lambda k: STYLE_LABELS[k],
        )

    st.success(
        "Behind the scenes: semantic search over your files, re-ranking, then a careful prompt "
        "so replies stay tied to what was retrieved — not free invention."
    )

    for turn in st.session_state.turns:
        _render_turn(turn)

    user_q = st.chat_input(
        "Ask about regions, parties, votes, or the 2025 budget…",
        key="main_chat",
    )
    if not user_q:
        return

    prior_pairs = [(t["query"], t["answer"]) for t in st.session_state.turns]
    mem_on = bool(st.session_state.get("use_conversational_memory"))
    retrieval_q = _retrieval_query_with_memory(user_q, prior_pairs, mem_on)

    log.info("CHAT_QUERY: %s", user_q)
    log.info("RETRIEVAL_QUERY: %s", retrieval_q)
    results, trace = retriever.retrieve(
        retrieval_q,
        boosted_sources=st.session_state.boosted_sources,
    )
    log.info("RETRIEVAL_TRACE: %s", json.dumps(trace, default=str)[:8000])
    trimmed = results[:FINAL_CONTEXT_CHUNKS]
    mem_text: str | None = None
    if mem_on:
        mem_text = format_conversation_memory(prior_pairs) or None

    bp = build_messages(
        user_q,
        trimmed,
        prompt_variant=prompt_variant,
        conversation_memory=mem_text,
    )
    disp_prompt = prompt_for_display(bp)
    log.info("PROMPT_TRUNCATED=%s CONTEXT_BLOCKS=%d", bp.truncated, len(bp.context_blocks))

    answer, meta = generate_rag_answer(bp)
    log.info("LLM_META: %s", json.dumps({k: str(v) for k, v in meta.items()}))

    run_entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "query": user_q,
        "retrieval_query_effective": retrieval_q,
        "prompt_variant": prompt_variant,
        "conversational_memory_enabled": mem_on,
        "prior_turns_in_memory": len(prior_pairs),
        "retrieval_trace": trace,
        "chunks": [
            {
                "id": r.chunk.chunk_id,
                "source": r.chunk.source,
                "faiss": r.faiss_score,
                "rerank": r.rerank_score,
                "fused": r.fused_score,
                "preview": r.chunk.text[:240].replace("\n", " "),
            }
            for r in trimmed
        ],
        "prompt": disp_prompt,
        "answer": answer,
        "llm_meta": meta,
    }

    baseline_payload = None
    if run_baseline:
        baseline_text, baseline_meta = generate_baseline_no_context(user_q)
        run_entry["baseline"] = {"text": baseline_text, "meta": baseline_meta}
        baseline_payload = {"text": baseline_text, "meta": baseline_meta}
        log.info("BASELINE_META: %s", baseline_meta)

    st.session_state.run_log.append(run_entry)
    with LOG_FILE.open("a", encoding="utf-8") as lf:
        lf.write(json.dumps(run_entry, ensure_ascii=False) + "\n")

    chunk_ui = []
    for r in trimmed:
        prev = r.chunk.text[:600].replace("\n", " ")
        chunk_ui.append(
            {
                "id": r.chunk.chunk_id,
                "source": r.chunk.source,
                "faiss": float(r.faiss_score),
                "rerank": r.rerank_score,
                "fused": float(r.fused_score),
                "preview": prev,
                "truncated_preview": len(r.chunk.text) > 600,
            }
        )

    turn = {
        "query": user_q,
        "answer": answer,
        "chunks": chunk_ui,
        "prompt": disp_prompt,
        "run_entry": run_entry,
        "baseline": baseline_payload,
    }
    st.session_state.turns.append(turn)
    st.rerun()


if __name__ == "__main__":
    main()
