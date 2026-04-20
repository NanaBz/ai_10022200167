# Nkabom Lens

**Grounded Q&A over Ghana election results and the 2025 national budget**

| | |
|---|---|
| **Author** | Nanakwaku Boateng Boakye-Akyeampong |
| **Index** | 10022200167 |
| **Course** | CS4241 — Introduction to Artificial Intelligence |
| **Entry point** | `ca_10022200167.py` |

**Live app:** *Add your deployed URL here after publishing.*

---

## Overview

**Nkabom Lens** is a retrieval-augmented generation (RAG) assistant that answers questions using two official-style corpora: a **CSV** of Ghana presidential election results and the **PDF** of Ghana’s *2025 Budget Statement and Economic Policy*.  

The stack is implemented **without** end-to-end RAG frameworks (no LangChain or LlamaIndex). Chunking, embeddings, vector search, scoring, prompts, and logging are written directly in Python for transparency and coursework traceability.

---

## Features

- **Dual corpus** — Election data (tabular, one row per chunk) and budget text (sliding windows with configurable overlap).
- **Semantic search** — Sentence Transformers embeddings with a **FAISS** index (inner product on normalised vectors).
- **Hybrid-style scoring** — Dense similarity combined with lexical overlap and optional **domain-aware** priors (election vs budget intent).
- **Re-ranking** — Cross-encoder rescoring of top candidates for sharper relevance.
- **Query expansion** — Lightweight term expansion for domain keywords.
- **Strict prompting** — Context-only answers with selectable **answer styles**; greedy context packing under a character budget.
- **Session tools** — Prefer election CSV or budget PDF for the current session; optional **multi-turn memory** so short follow-ups stay coherent (with retrieval anchoring to the prior question).
- **Transparency** — UI shows retrieved passages, similarity-related scores, the full prompt sent to the model, and an optional **no-documents** comparison on the same question.
- **Logging** — Structured run traces appended to `logs/rag_pipeline.log`.

---

## Tech stack

| Layer | Choice |
|--------|--------|
| UI | Streamlit (`ca_10022200167.py`) |
| PDF | `pypdf` |
| Embeddings | `sentence-transformers` (e.g. `all-MiniLM-L6-v2`) |
| Vector store | FAISS (`IndexFlatIP`) |
| Re-ranking | Cross-encoder (`ms-marco-MiniLM-L-6-v2`) |
| Generation | OpenAI Chat Completions API |

Datasets are downloaded from the URLs in `rag_config.py` and cached under `data/`. The FAISS index and embeddings are stored under `index_store/` after the first build.

---

## Running locally

Requirements: **Python 3.11+** recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set your API key (or paste it in the app sidebar for the session only):

```powershell
$env:OPENAI_API_KEY = "your-key-here"
streamlit run ca_10022200167.py
```

The first launch may take several minutes while Hugging Face models download and the search index is built.

Optional environment variable: `OPENAI_MODEL` (defaults to `gpt-4o-mini` in `rag_config.py`).

---

## Deployment

The app is Streamlit-compatible. Point your host at `ca_10022200167.py`, install dependencies from `requirements.txt`, and provide `OPENAI_API_KEY` via the platform’s secret or environment configuration. A `streamlit/config.toml` theme file is included for consistent styling.

---

## Repository layout

| Path | Role |
|------|------|
| `ca_10022200167.py` | Streamlit application |
| `rag_config.py` | URLs, paths, hyperparameters |
| `rag_data.py` | Download, cleaning, chunking |
| `rag_retrieve.py` | Embeddings, FAISS, retrieval pipeline |
| `rag_prompt.py` | Prompt templates, conversation memory formatting |
| `rag_llm.py` | OpenAI client (RAG and baseline paths) |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | Streamlit theme |
| `data/`, `index_store/`, `logs/` | Generated at runtime (not required in Git) |

---

## Licence & data

Election and budget content retain their original sources and usage terms. This repository provides software only; it does not claim ownership of the underlying datasets.
