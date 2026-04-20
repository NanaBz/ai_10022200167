"""
Nanakwaku Boateng Boakye-Akyeampong | Index: 10022200167
Project: CS4241 manual RAG — shared configuration.
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
INDEX_DIR = PROJECT_ROOT / "index_store"
LOG_DIR = PROJECT_ROOT / "logs"

CSV_URL = (
    "https://raw.githubusercontent.com/GodwinDansoAcity/acitydataset/"
    "main/Ghana_Election_Result.csv"
)
PDF_URL = (
    "https://mofep.gov.gh/sites/default/files/budget-statements/"
    "2025-Budget-Statement-and-Economic-Policy_v4.pdf"
)

LOCAL_CSV = DATA_DIR / "Ghana_Election_Result.csv"
LOCAL_PDF = DATA_DIR / "budget_2025.pdf"

# --- Chunking (Part A defaults; justify overlap in README) ---
PDF_CHUNK_CHARS = 1200
PDF_CHUNK_OVERLAP = 200

# --- Retrieval ---
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
FAISS_TOP_K = 40
RERANK_TOP_N = 8
FINAL_CONTEXT_CHUNKS = 6

# --- Context window (rough char budget for retrieved text in prompt) ---
MAX_CONTEXT_CHARS = 6000

# --- Conversational RAG (session memory in prompt only; optional) ---
MEMORY_MAX_TURNS = 6
MEMORY_MAX_CHARS = 2500
MEMORY_ANSWER_PREVIEW_CHARS = 450

# --- LLM ---
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
