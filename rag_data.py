"""
Nanakwaku Boateng Boakye-Akyeampong | Index: 10022200167
Data engineering: download, clean, and chunk CSV + PDF (no framework RAG).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from pypdf import PdfReader

from rag_config import CSV_URL, DATA_DIR, LOCAL_CSV, LOCAL_PDF, PDF_URL
from rag_config import PDF_CHUNK_CHARS, PDF_CHUNK_OVERLAP

log = logging.getLogger(__name__)


@dataclass
class ChunkRecord:
    chunk_id: str
    text: str
    source: str
    meta: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _ensure_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    log.info("Downloading %s -> %s", url, dest)
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    dest.write_bytes(r.content)


def load_raw_sources() -> tuple[Path, Path]:
    _ensure_file(CSV_URL, LOCAL_CSV)
    _ensure_file(PDF_URL, LOCAL_PDF)
    return LOCAL_CSV, LOCAL_PDF


def _clean_csv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Strip whitespace, normalize column names
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    # Drop fully empty rows
    df = df.dropna(how="all")
    # Core columns for election file
    core = [c for c in ["Year", "Candidate", "Party", "Votes"] if c in df.columns]
    if core:
        df = df.dropna(subset=core, how="all")
    return df


def csv_to_chunks(csv_path: Path) -> list[ChunkRecord]:
    df = pd.read_csv(csv_path, encoding="utf-8", encoding_errors="replace")
    df = _clean_csv(df)
    chunks: list[ChunkRecord] = []
    cols = list(df.columns)
    for i, row in df.iterrows():
        parts = []
        for c in cols:
            v = row.get(c, "")
            if pd.isna(v) or str(v).strip() == "" or str(v).lower() == "nan":
                continue
            parts.append(f"{c}: {v}")
        text = " | ".join(parts)
        text = re.sub(r"\s+", " ", text).strip()
        cid = f"csv:{i}"
        meta = {"row_index": int(i), "type": "election_csv"}
        chunks.append(ChunkRecord(chunk_id=cid, text=text, source="election_csv", meta=meta))
    log.info("CSV chunks: %d", len(chunks))
    return chunks


def _extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages_text: list[str] = []
    for pnum, page in enumerate(reader.pages):
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            pages_text.append(f"[Page {pnum + 1}] {t}")
    return "\n".join(pages_text)


def _split_pdf_text(text: str, chunk_size: int, overlap: int) -> list[tuple[str, int]]:
    """Sliding windows over flattened PDF text; returns (chunk_text, start_char_offset)."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    out: list[tuple[str, int]] = []
    start = 0
    n = len(text)
    step = max(chunk_size - overlap, 1)
    while start < n:
        end = min(start + chunk_size, n)
        piece = text[start:end].strip()
        if piece:
            out.append((piece, start))
        if end >= n:
            break
        start += step
    return out


def pdf_to_chunks(
    pdf_path: Path,
    chunk_chars: int | None = None,
    chunk_overlap: int | None = None,
) -> list[ChunkRecord]:
    cc = chunk_chars if chunk_chars is not None else PDF_CHUNK_CHARS
    co = chunk_overlap if chunk_overlap is not None else PDF_CHUNK_OVERLAP
    raw = _extract_pdf_text(pdf_path)
    windows = _split_pdf_text(raw, cc, co)
    chunks: list[ChunkRecord] = []
    for i, (piece, off) in enumerate(windows):
        cid = f"pdf:{i}"
        meta = {"char_offset": off, "type": "budget_pdf"}
        chunks.append(ChunkRecord(chunk_id=cid, text=piece, source="budget_pdf", meta=meta))
    log.info("PDF chunks: %d", len(chunks))
    return chunks


def build_all_chunks(
    pdf_chunk_chars: int | None = None,
    pdf_chunk_overlap: int | None = None,
) -> list[ChunkRecord]:
    csv_path, pdf_path = load_raw_sources()
    return csv_to_chunks(csv_path) + pdf_to_chunks(
        pdf_path,
        chunk_chars=pdf_chunk_chars,
        chunk_overlap=pdf_chunk_overlap,
    )


def save_chunk_manifest(chunks: list[ChunkRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")


def load_chunk_manifest(path: Path) -> list[ChunkRecord]:
    out: list[ChunkRecord] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            out.append(
                ChunkRecord(
                    chunk_id=d["chunk_id"],
                    text=d["text"],
                    source=d["source"],
                    meta=d.get("meta", {}),
                )
            )
    return out
