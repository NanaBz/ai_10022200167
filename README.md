# CS4241 — Manual RAG Assistant (Academic City)

**Student:** Nanakwaku Boateng Boakye-Akyeampong  
**Index number:** 10022200167  
**Repository name (submission):** `ai_10022200167`  
**Main application:** `ca_10022200167.py`

This project implements a **custom** Retrieval-Augmented Generation (RAG) stack for two corpora:

1. **Ghana election results (CSV)** — downloaded from the course dataset URL (raw GitHub file).
2. **2025 Budget Statement and Economic Policy (PDF)** — downloaded from the Ministry of Finance and Economic Planning site.

**Frameworks explicitly not used:** LangChain, LlamaIndex, or any end-to-end RAG framework. Chunking, retrieval, scoring, prompt assembly, and logging are implemented directly in Python.

---

## Quick start (local)

```powershell
cd "C:\Users\ThinkPad\Desktop\Intro to AI\ai_exam"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY = "sk-..."   # optional; can paste in the app sidebar instead
streamlit run ca_10022200167.py
```

First launch downloads Hugging Face models (`all-MiniLM-L6-v2`, `ms-marco` cross-encoder) and builds a FAISS index under `index_store/`. Allow several minutes on a slow connection.

---

## What the code implements (mapping to exam parts)

| Part | Implementation in this repo |
|------|-----------------------------|
| **A — Data & chunking** | `rag_data.py`: CSV cleaning (strip, drop empty), one structured row per chunk; PDF text extraction (`pypdf`) + sliding character windows (`PDF_CHUNK_CHARS`, `PDF_CHUNK_OVERLAP` in `rag_config.py`). |
| **B — Retrieval** | `rag_retrieve.py`: SentenceTransformers embeddings, **FAISS** `IndexFlatIP` on L2-normalized vectors (cosine via inner product), top-`k` search, **query expansion** (`expand_query`), **cross-encoder re-ranking**, plus lexical overlap and **domain-aware source priors**. |
| **C — Prompting** | `rag_prompt.py`: strict system prompt (context-only, anti-hallucination), greedy **context packing** up to `MAX_CONTEXT_CHARS`. |
| **D — Full pipeline + logging** | `ca_10022200167.py`: user query → retrieval trace → prompt → LLM; UI shows chunks, scores, final prompt; JSON lines appended to `logs/rag_pipeline.log`. |
| **G — Innovation** | (1) **Domain-aware score fusion** (election vs budget intent heuristics). (2) **Session relevance feedback**: sidebar checkboxes boost `election_csv` or `budget_pdf` sources for subsequent retrievals. |

---

## Chunk size and overlap (Part A — for your written justification)

- **CSV:** each row is one chunk (tabular facts stay atomic; avoids splitting a single result across windows).
- **PDF:** default **1200 characters** per chunk with **200 overlap** so sentences spanning boundaries remain recoverable in at least one chunk. Adjust in `rag_config.py` and rebuild the index (sidebar: “Rebuild vector index” + “Load / rebuild index”).

For your report’s **comparative analysis**, run at least two configurations (e.g. overlap 0 vs 200, or chunk size 800 vs 1600), keep queries fixed, and record precision@k / qualitative misses in your **manual experiment log** (see below).

---

## Retrieval failure cases and fixes (Part B — evidence for your report)

Typical failures **before** mitigation:

1. **Domain drift:** a vague query (“What was the fiscal position?”) can still retrieve election rows if embeddings overlap on generic words.
2. **Long-budget repetition:** many PDF chunks share similar boilerplate; pure embedding top‑k may return near-duplicate context.

**Fixes implemented:** query expansion for domain keywords, **fusion** of dense similarity with lexical overlap, **cross-encoder re-ranking** on candidate pairs, and **domain / feedback priors** to shift mass toward the intended corpus.

Document concrete queries where retrieval was wrong **before** a change, and improved **after**, in your manual log (screenshots + scores from the UI expanders help).

---

## Part E — Baseline vs RAG (your evidence)

The Streamlit toggle **“Also run pure-LLM baseline (Part E)”** calls `generate_baseline_no_context` in `rag_llm.py` with the same user query and **no** retrieved context. Use identical questions, compare grounded facts vs fabrication, and tabulate **accuracy / hallucination / consistency** in your own words in the manual log (the rubric asks for **non–AI-generated** logs).

---

## Deployment (cloud URL for submission)

Recommended: [Streamlit Community Cloud](https://streamlit.io/cloud)

1. Push this folder to GitHub as repository **`ai_10022200167`** (private or public per course rules).
2. On Streamlit Cloud, “New app” → select the repo, branch, and **Main file path:** `ca_10022200167.py`.
3. Under **Secrets**, add `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`, e.g. `gpt-4o-mini`).
4. Python version **3.11+** recommended; set `requirements.txt` as dependencies.
5. After deploy, copy the public URL for your email to the lecturer.

---

## Email and subject line (you send this)

- **To:** `godwin.danso@acity.edu.gh`  
- **Subject format:** `CS4241-Introduction to Artificial Intelligence-2026:10022200167 Nanakwaku Boateng Boakye-Akyeampong`  
- **Body:** GitHub link + deployed app URL.

---

## Deliverables you still complete manually (checklist)

1. **GitHub:** create `ai_10022200167`, add all project files, verify README header matches your identity on **every submitted file** as required by the brief (Python modules here already include a header comment).
2. **≤ 2 minute video:** screen record: chunking rationale, retrieval stack, show UI with retrieved chunks + scores + prompt, mention innovation. Use OBS / PowerPoint screen recording / Teams clip.
3. **Manual experiment logs:** paper or Markdown **you** write: dates, hyperparameters, queries, observations (not pasted AI summaries). Reference rows from `logs/rag_pipeline.log` as evidence.
4. **Part C experiments:** use the in-app **Prompt variant** selector (maps to `PROMPT_VARIANTS` in `rag_prompt.py`), run the **same query** twice, and record how answers differ in your manual log.
5. **Part E adversarial queries:** design two (ambiguous / misleading / incomplete). Run through UI; paste outputs + your grading into the log.
6. **Part F architecture diagram:** draw in Draw.io / PowerPoint / Excalidraw: **User → Streamlit → Embedder → FAISS → Re-ranker → Prompt builder → OpenAI → Response**, parallel **logs** path. Export PNG/PDF into repo if allowed.
7. **Part B “hybrid” note:** the brief mentions hybrid keyword + vector; this codebase combines **vector** search with a **lexical overlap** signal in `fuse_scores` — cite that as lightweight hybrid retrieval in your documentation.

---

## File map

| File | Role |
|------|------|
| `ca_10022200167.py` | Streamlit UI, session feedback, logging hook-in |
| `rag_config.py` | URLs, paths, hyperparameters |
| `rag_data.py` | Download, clean, chunk |
| `rag_retrieve.py` | Embeddings, FAISS, expansion, fusion, re-rank |
| `rag_prompt.py` | Prompt + context budget |
| `rag_llm.py` | OpenAI chat completions (RAG + baseline) |
| `requirements.txt` | Dependencies |
| `data/` | Cached downloads (gitignored by default) |
| `index_store/` | Persisted FAISS + chunk metadata (gitignored) |
| `logs/` | Append-only JSONL-style run log |

---

## Academic integrity

Write your experiment log, video narration, and written analysis in your own words. Use this codebase as the implementation backbone and cite it in your report.
