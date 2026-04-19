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
from rag_prompt import build_messages, prompt_for_display
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


def _init_session() -> None:
    if "boosted_sources" not in st.session_state:
        st.session_state.boosted_sources = set()
    if "run_log" not in st.session_state:
        st.session_state.run_log = []
    if "turns" not in st.session_state:
        st.session_state.turns = []
    if "pipeline_ready" not in st.session_state:
        st.session_state.pipeline_ready = False


@st.cache_resource(show_spinner=True)
def _load_index_bundle(force_rebuild: bool):
    return try_load_or_build_index(force_rebuild=force_rebuild)


def _render_turn(turn: dict) -> None:
    with st.chat_message("user"):
        st.write(turn["query"])
    with st.chat_message("assistant"):
        st.subheader("Final response")
        st.write(turn["answer"])
        with st.expander("Retrieved chunks (scores)", expanded=False):
            for ch in turn["chunks"]:
                st.markdown(
                    f"**{ch['id']}** · `{ch['source']}` · "
                    f"faiss={ch['faiss']:.4f} · rerank={ch['rerank']} · fused={ch['fused']:.4f}"
                )
                prev = ch.get("preview", "")
                st.caption(prev + ("…" if ch.get("truncated_preview") else ""))
        with st.expander("Final prompt sent to the LLM"):
            st.code(turn["prompt"], language="text")
        with st.expander("Pipeline JSON (this turn)"):
            st.json(turn["run_entry"])
        if turn.get("baseline"):
            with st.expander("Baseline: same query, no retrieval"):
                st.write(turn["baseline"]["text"])
                st.json(turn["baseline"]["meta"])


def main() -> None:
    st.set_page_config(
        page_title="ACity RAG Assistant",
        page_icon="🎓",
        layout="wide",
    )
    _init_session()

    st.title("Academic City — Manual RAG Assistant")
    st.caption(
        "CS4241 demo — Nanakwaku Boateng Boakye-Akyeampong (10022200167) — "
        "Election CSV + 2025 Budget PDF"
    )

    with st.sidebar:
        st.subheader("Configuration")
        api_key = st.text_input(
            "OpenAI API key (optional)",
            type="password",
            help="Stored only in this browser session via environment variable override.",
        )
        if api_key.strip():
            os.environ["OPENAI_API_KEY"] = api_key.strip()

        force_rebuild = st.checkbox("Rebuild vector index", value=False)
        if st.button("Load / rebuild index"):
            st.cache_resource.clear()
            st.rerun()

        st.markdown("---")
        st.subheader("Innovation: relevance feedback")
        st.caption(
            "Boost sources you trust for the rest of this session "
            "(domain-aware retrieval prior)."
        )
        b_election = st.checkbox("Boost election CSV", value=False)
        b_budget = st.checkbox("Boost budget PDF", value=False)
        st.session_state.boosted_sources = set()
        if b_election:
            st.session_state.boosted_sources.add("election_csv")
        if b_budget:
            st.session_state.boosted_sources.add("budget_pdf")

        st.markdown("---")
        st.text(f"Project: {PROJECT_ROOT}")
        st.text(f"Logs: {LOG_FILE}")

    with st.spinner("Loading embedding models and FAISS index (first run may download data)..."):
        vindex, cross = _load_index_bundle(force_rebuild=force_rebuild)
    retriever = RetrievalPipeline(vindex, cross)
    st.session_state.pipeline_ready = True

    run_baseline = st.toggle("Also run pure-LLM baseline (Part E)", value=False)
    prompt_variant = st.selectbox(
        "Prompt variant (Part C experiments)",
        options=["strict_anti_hallucination", "concise_not_found"],
        index=0,
    )

    st.info(
        "Manual RAG stack: custom chunking, SentenceTransformers embeddings, "
        "FAISS IndexFlatIP, query expansion, cross-encoder re-ranking, "
        "domain-aware score fusion, and a strict anti-hallucination prompt."
    )

    for turn in st.session_state.turns:
        _render_turn(turn)

    user_q = st.chat_input("Ask about Ghana election results or the 2025 budget statement...")
    if not user_q:
        return

    log.info("QUERY: %s", user_q)
    results, trace = retriever.retrieve(
        user_q,
        boosted_sources=st.session_state.boosted_sources,
    )
    log.info("RETRIEVAL_TRACE: %s", json.dumps(trace, default=str)[:8000])
    trimmed = results[:FINAL_CONTEXT_CHUNKS]

    bp = build_messages(user_q, trimmed, prompt_variant=prompt_variant)
    disp_prompt = prompt_for_display(bp)
    log.info("PROMPT_TRUNCATED=%s CONTEXT_BLOCKS=%d", bp.truncated, len(bp.context_blocks))

    answer, meta = generate_rag_answer(bp)
    log.info("LLM_META: %s", json.dumps({k: str(v) for k, v in meta.items()}))

    run_entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "query": user_q,
        "prompt_variant": prompt_variant,
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
