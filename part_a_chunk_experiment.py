"""
Nanakwaku Boateng Boakye-Akyeampong | Index: 10022200167
Part A — automated chunking comparison: builds two PDF chunking configs, runs the
same fixed queries, writes a Markdown report (tables + top-k previews).

Run (from project root, venv active):
    python part_a_chunk_experiment.py
    python part_a_chunk_experiment.py --max-queries 3
    python part_a_chunk_experiment.py --no-rerank

`--no-rerank` skips the cross-encoder (faster, less RAM); tables show None for rerank.

Output:
    reports/part_a_chunk_comparison_autogen.md

UI screenshots for Figure A1/A2 are still manual; use this file as evidence + captions.
"""

from __future__ import annotations

import argparse
import gc
import logging
import traceback
from datetime import datetime, timezone

from sentence_transformers import CrossEncoder, SentenceTransformer

from rag_config import EMBED_MODEL, FINAL_CONTEXT_CHUNKS, RERANK_MODEL, REPORTS_DIR
from rag_data import build_all_chunks
from rag_retrieve import RetrievalPipeline, VectorIndex

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("part_a_experiment")

CONFIGS: list[dict[str, int | str]] = [
    {"name": "A_baseline", "pdf_chunk_chars": 1200, "pdf_chunk_overlap": 200},
    {"name": "B_smaller_window", "pdf_chunk_chars": 800, "pdf_chunk_overlap": 100},
]

QUERIES: list[str] = [
    "In the 2020 results, how many votes did Nana Akufo Addo get in the Ahafo Region?",
    "What does the 2025 budget say about revenue or tax policy?",
    "Who won the presidential election?",
    "What is the fiscal deficit outlook mentioned in the budget?",
    "Compare NPP and NDC votes for the Ahafo Region in 2020.",
]


def _preview(text: str, n: int = 160) -> str:
    t = text.replace("\n", " ").strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def _append(path, text: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def main() -> None:
    ap = argparse.ArgumentParser(description="Part A chunking ablation report")
    ap.add_argument(
        "--max-queries",
        type=int,
        default=0,
        help="Use only the first N queries (0 = all).",
    )
    ap.add_argument(
        "--no-rerank",
        action="store_true",
        help="Skip cross-encoder (faster, lower memory).",
    )
    args = ap.parse_args()

    queries = QUERIES[: args.max_queries] if args.max_queries > 0 else QUERIES

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "part_a_chunk_comparison_autogen.md"
    err_path = REPORTS_DIR / "part_a_last_error.txt"

    out_path.write_text("", encoding="utf-8")
    if err_path.exists():
        err_path.unlink()

    lines = [
        "# Part A — Automated chunking comparison\n",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}`\n",
        f"Options: max_queries={args.max_queries or 'all'}, no_rerank={args.no_rerank}\n",
        "\n## Configurations\n",
        "| Config | PDF_CHUNK_CHARS | PDF_CHUNK_OVERLAP |",
        "|--------|-----------------|-------------------|",
    ]
    for c in CONFIGS:
        lines.append(
            f"| **{c['name']}** | {c['pdf_chunk_chars']} | {c['pdf_chunk_overlap']} |"
        )
    lines.append("\n## Corpus sizes (after chunking)\n")
    out_path.write_text("\n".join(lines), encoding="utf-8")

    embedder = SentenceTransformer(EMBED_MODEL)
    cross = None if args.no_rerank else CrossEncoder(RERANK_MODEL)

    try:
        for c in CONFIGS:
            name = str(c["name"])
            chars = int(c["pdf_chunk_chars"])
            ov = int(c["pdf_chunk_overlap"])
            log.info("Building chunks for %s (chars=%s overlap=%s)", name, chars, ov)
            chunks = build_all_chunks(pdf_chunk_chars=chars, pdf_chunk_overlap=ov)
            n_csv = sum(1 for x in chunks if x.source == "election_csv")
            n_pdf = sum(1 for x in chunks if x.source == "budget_pdf")
            _append(
                out_path,
                f"- **{name}**: total chunks = **{len(chunks)}** "
                f"(`election_csv` = {n_csv}, `budget_pdf` = {n_pdf})\n",
            )

            vindex = VectorIndex.build(chunks, embedder)
            retriever = RetrievalPipeline(vindex, cross)

            buf: list[str] = [
                "\n---\n\n",
                f"## Retrieval results — `{name}`\n",
            ]
            for q in queries:
                results, _trace = retriever.retrieve(q, boosted_sources=set())
                top = results[:FINAL_CONTEXT_CHUNKS]
                buf.append(f"\n### Query\n{q}\n\n")
                buf.append(
                    "| Rank | Source | Chunk ID | faiss | rerank | fused | Preview |\n"
                )
                buf.append(
                    "|:----:|--------|----------|------:|-------:|------:|---------|\n"
                )
                for i, r in enumerate(top, 1):
                    rr = r.rerank_score
                    rr_s = "None" if rr is None else str(round(float(rr), 4))
                    buf.append(
                        f"| {i} | `{r.chunk.source}` | `{r.chunk.chunk_id}` | "
                        f"{round(r.faiss_score, 4)} | {rr_s} | {round(r.fused_score, 4)} | "
                        f"{_preview(r.chunk.text)} |\n"
                    )
                buf.append("\n")

            _append(out_path, "".join(buf))
            log.info("Appended results for %s", name)

            del retriever, vindex, chunks
            gc.collect()

        _append(
            out_path,
            "\n---\n\n*Automated run complete. Pair with UI screenshots (Figure A1/A2).*",
        )
        log.info("Wrote %s", out_path.resolve())

    except Exception:
        err_path.write_text(traceback.format_exc(), encoding="utf-8")
        log.exception("part_a_chunk_experiment failed; see %s", err_path)
        raise


if __name__ == "__main__":
    main()
