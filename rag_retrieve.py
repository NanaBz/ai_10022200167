"""
Nanakwaku Boateng Boakye-Akyeampong | Index: 10022200167
Manual retrieval: embeddings, FAISS, similarity, query expansion, re-ranking,
and domain-aware score fusion (innovation: source prior from query intent).
"""

from __future__ import annotations

import json
import logging
import math
import re
from dataclasses import dataclass
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

from rag_config import (
    EMBED_MODEL,
    FAISS_TOP_K,
    INDEX_DIR,
    RERANK_MODEL,
    RERANK_TOP_N,
)
from rag_data import ChunkRecord, build_all_chunks, save_chunk_manifest

log = logging.getLogger(__name__)

# --- Query expansion (lightweight lexical expansion; not a framework) ---
EXPANSIONS: dict[str, list[str]] = {
    "election": ["votes", "candidate", "party", "region", "npp", "ndc", "ballot"],
    "vote": ["votes", "candidate", "party"],
    "npp": ["party", "candidate", "votes"],
    "ndc": ["party", "candidate", "votes"],
    "budget": ["revenue", "expenditure", "fiscal", "deficit", "gdp", "policy"],
    "tax": ["revenue", "customs", "income tax", "vat"],
    "gdp": ["growth", "economy", "macroeconomic"],
    "imf": ["programme", "financing", "fiscal"],
}


def expand_query(q: str) -> str:
    low = q.lower()
    extras: list[str] = []
    for key, terms in EXPANSIONS.items():
        if key in low:
            extras.extend(terms)
    if not extras:
        return q
    return q + " " + " ".join(sorted(set(extras)))


_ELECTION_HINTS = re.compile(
    r"\b(election|vote|npp|ndc|candidate|party|region|constituency|ballot)\b", re.I
)
_BUDGET_HINTS = re.compile(
    r"\b(budget|fiscal|revenue|expenditure|tax|gdp|macro|debt|deficit|imf|policy|mofep)\b",
    re.I,
)


def domain_source_boost(query: str, chunk: ChunkRecord) -> float:
    """
    Innovation: domain-specific prior — nudge scores toward the corpus that
    matches query intent (election CSV vs budget PDF) without blocking cross-domain.
    """
    el = bool(_ELECTION_HINTS.search(query))
    bd = bool(_BUDGET_HINTS.search(query))
    if el and not bd:
        return 1.15 if chunk.source == "election_csv" else 0.95
    if bd and not el:
        return 1.15 if chunk.source == "budget_pdf" else 0.95
    return 1.0


def lexical_overlap_score(query: str, text: str) -> float:
    q_tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
    t_tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
    if not q_tokens:
        return 0.0
    inter = len(q_tokens & t_tokens)
    return inter / math.sqrt(len(q_tokens) * max(len(t_tokens), 1))


@dataclass
class RetrievedChunk:
    chunk: ChunkRecord
    faiss_score: float
    rerank_score: float | None
    fused_score: float


class VectorIndex:
    def __init__(
        self,
        chunks: list[ChunkRecord],
        embedder: SentenceTransformer,
        index: faiss.Index,
        embeddings: np.ndarray,
    ):
        self.chunks = chunks
        self.embedder = embedder
        self.index = index
        self.embeddings = embeddings

    @staticmethod
    def build(chunks: list[ChunkRecord], embedder: SentenceTransformer) -> "VectorIndex":
        texts = [c.text for c in chunks]
        log.info("Encoding %d chunks...", len(texts))
        emb = embedder.encode(
            texts,
            batch_size=64,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        emb = np.asarray(emb, dtype="float32")
        dim = emb.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(emb)
        return VectorIndex(chunks=chunks, embedder=embedder, index=index, embeddings=emb)

    def save(self, base: Path) -> None:
        base.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(base / "faiss.index"))
        np.save(base / "embeddings.npy", self.embeddings)
        meta = [c.to_dict() for c in self.chunks]
        (base / "chunks.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, base: Path, embedder: SentenceTransformer) -> "VectorIndex":
        index = faiss.read_index(str(base / "faiss.index"))
        emb = np.load(base / "embeddings.npy")
        raw = json.loads((base / "chunks.json").read_text(encoding="utf-8"))
        chunks = [
            ChunkRecord(
                chunk_id=d["chunk_id"],
                text=d["text"],
                source=d["source"],
                meta=d.get("meta", {}),
            )
            for d in raw
        ]
        return cls(chunks=chunks, embedder=embedder, index=index, embeddings=emb)

    def search_faiss(self, query: str, k: int) -> list[tuple[int, float]]:
        qv = self.embedder.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        qv = np.asarray(qv, dtype="float32")
        scores, idx = self.index.search(qv, k)
        pairs: list[tuple[int, float]] = []
        for i, s in zip(idx[0], scores[0]):
            if i < 0:
                continue
            pairs.append((int(i), float(s)))
        return pairs


def fuse_scores(cosine: float, lex: float, domain_b: float) -> float:
    # cosine in [0,1] for normalized IP; blend with sparse lexical signal
    return float(cosine) * 0.65 + float(lex) * 0.25 + (float(domain_b) - 1.0) * 0.2


class RetrievalPipeline:
    def __init__(
        self,
        vindex: VectorIndex,
        cross_encoder: CrossEncoder | None,
    ):
        self.vindex = vindex
        self.cross_encoder = cross_encoder

    def retrieve(
        self,
        raw_query: str,
        boosted_sources: set[str] | None = None,
    ) -> tuple[list[RetrievedChunk], dict]:
        """
        Returns retrieved chunks and a debug trace for UI/logging.
        boosted_sources: session feedback — sources user marked helpful (innovation).
        """
        trace: dict = {"stages": []}
        q_expanded = expand_query(raw_query)
        trace["stages"].append(
            {"name": "query_expansion", "in": raw_query, "out": q_expanded}
        )

        faiss_hits = self.vindex.search_faiss(q_expanded, FAISS_TOP_K)
        trace["stages"].append({"name": "faiss_topk", "k": FAISS_TOP_K, "hits": len(faiss_hits)})

        candidates: list[RetrievedChunk] = []
        for idx_i, cos in faiss_hits:
            ch = self.vindex.chunks[idx_i]
            lex = lexical_overlap_score(raw_query, ch.text)
            dom = domain_source_boost(raw_query, ch)
            if boosted_sources and ch.source in boosted_sources:
                dom *= 1.12
            fused = fuse_scores(cos, lex, dom)
            candidates.append(
                RetrievedChunk(
                    chunk=ch,
                    faiss_score=cos,
                    rerank_score=None,
                    fused_score=fused,
                )
            )
        candidates.sort(key=lambda x: x.fused_score, reverse=True)
        trace["stages"].append({"name": "fusion_sort", "n": len(candidates)})

        top_for_rerank = candidates[: max(RERANK_TOP_N * 4, RERANK_TOP_N)]

        if self.cross_encoder and top_for_rerank:
            pairs = [[raw_query, r.chunk.text] for r in top_for_rerank]
            ce_scores = self.cross_encoder.predict(pairs, show_progress_bar=False)
            for r, s in zip(top_for_rerank, ce_scores):
                r.rerank_score = float(s)
            top_for_rerank.sort(
                key=lambda x: (x.rerank_score or 0.0) * 0.7 + x.fused_score * 0.3,
                reverse=True,
            )
            trace["stages"].append({"name": "cross_encoder_rerank", "n": len(pairs)})
        else:
            trace["stages"].append({"name": "cross_encoder_rerank", "skipped": True})

        final = top_for_rerank[:RERANK_TOP_N]
        trace["stages"].append({"name": "final_cut", "n": len(final)})
        return final, trace


def default_index_dir() -> Path:
    return INDEX_DIR / "default_bundle"


def try_load_or_build_index(
    force_rebuild: bool = False,
) -> tuple[VectorIndex, CrossEncoder | None]:
    bundle = default_index_dir()
    embedder = SentenceTransformer(EMBED_MODEL)
    cross = CrossEncoder(RERANK_MODEL)

    if not force_rebuild and (bundle / "faiss.index").exists():
        log.info("Loading index from %s", bundle)
        return VectorIndex.load(bundle, embedder), cross

    chunks = build_all_chunks()
    save_chunk_manifest(chunks, bundle / "manifest.jsonl")
    vindex = VectorIndex.build(chunks, embedder)
    vindex.save(bundle)
    return vindex, cross
