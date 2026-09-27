# 🛡️ VERITAS: Multi-Agent Fact-Checking & Misinformation Detection Pipeline

An enterprise-grade, multi-agent misinformation detection and fact-verification platform built with **FastAPI**, **LangGraph**, **Model Context Protocol (MCP)**, **Tavily Live Web Search**, and a **React + Tailwind CSS** professional editorial desk interface.

---

## 📋 Table of Contents
1. [Overview & Objectives](#overview--objectives)
2. [Multi-Agent Architecture (LangGraph)](#multi-agent-architecture-langgraph)
3. [Model Context Protocol (MCP) Tools](#model-context-protocol-mcp-tools)
4. [RAG Knowledge Base & Source Credibility](#rag-knowledge-base--source-credibility)
5. [Safety Guardrails & IFCN Standards](#safety-guardrails--ifcn-standards)
6. [Design System & Architecture Compliance](#design-system--architecture-compliance)
7. [Directory Structure](#directory-structure)
8. [Getting Started & Installation](#getting-started--installation)
9. [API Endpoints](#api-endpoints)
10. [Benchmark & Accuracy Evaluation](#benchmark--accuracy-evaluation)

---

## 1. Overview & Objectives
Misinformation and synthetic hoaxes proliferate rapidly through messaging applications (e.g., WhatsApp, Telegram) and social platforms. Verifying claims manually requires cross-referencing multiple primary sources, assessing publisher reliability, and evaluating counter-evidence—demands that exceed the time available to most readers.

**VERITAS** automates this workflow for journalists, students, educators, and the public by:
- Deconstructing raw messages into discrete, checkable factual claims.
- Retrieving dual-sided evidence across live search (**Tavily**) and verified historical databases (**RAG Archive**).
- Adjudicating verdicts (**True**, **False**, **Misleading**, or **Unverifiable**) with rigorous source citations.
- Subjecting conclusions to an **Editorial Critic Reflection Loop** that audits for media bias and missing counter-evidence.
- Compiling periodic intelligence digests and exporting reports via **Model Context Protocol (MCP)**.

---

## 2. Multi-Agent Architecture (LangGraph)

The core verification workflow operates as a stateful computational graph with an active reflection loop:

```
                          ┌────────────────────────┐
                          │  Raw User Input Text   │
                          └───────────┬────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │  1. Claim Extractor Node  │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
     ┌─────────────────►┌───────────────────────────┐
     │                  │ 2. Evidence Retriever     │
     │                  │ (Tavily + RAG Knowledge)  │
     │                  └─────────────┬─────────────┘
     │                                │
     │ Reflection Loop                ▼
(Needs Counter-Evidence) ┌───────────────────────────┐
     │                  │  3. Verdict Judge Node    │
     │                  │  (Dual-Sided IFCN Weigh)  │
     │                  └─────────────┬─────────────┘
     │                                │
     │                                ▼
     └──────────────────┤    4. Critic Node         │
       (Rounds < Max)   └─────────────┬─────────────┘
                                      │ (Approved / Max Depth)
                                      ▼
                        ┌───────────────────────────┐
                        │  5. Finalizer & MCP Store │
                        │  (Persist Claim to DB)    │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │  6. Digest Writer (MCP)   │
                        │  (Export Markdown Report) │
                        └───────────────────────────┘
```

### Agent Node Responsibilities
1. **Claim Extractor**: Parses forwarded text, compound statements, or inquiries into atomic, testable propositions.
2. **Evidence Retriever**: Queries Tavily live search and the internal RAG archive for supporting AND refuting sources.
3. **Verdict Judge**: Applies credibility-weighted evidence scoring to reach a reasoned verdict:
   - `True`: Empirically validated by high-credibility primary records or institutional consensus.
   - `False`: Explicitly refuted by official statements or scientific consensus.
   - `Misleading`: Partially accurate but distorted, exaggerated, or lacking vital context.
   - `Unverifiable`: Default guardrail when evidence is sparse, vague, or disputed without consensus.
4. **Critic (Reflection)**: Audits verdicts for confirmation bias and weak citations. If critical opposing evidence is missing, it formulates targeted queries and triggers an iteration back to the Evidence Retriever.
5. **Digest Writer**: Compiles batch claims into structured Markdown daily digests and persists them via MCP.

---

## 3. Model Context Protocol (MCP) Tools

The backend implements three standard MCP tools accessible internally and over the MCP protocol (`mcp.server.fastmcp`):

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| `save_digest` | `topic`, `date_str`, `markdown_content`, `title` | Persists a compiled daily digest to the SQLite database. |
| `get_saved_claims` | `query`, `verdict`, `limit`, `offset` | Retrieves previously verified claims and their evidentiary breakdown. |
| `export_markdown` | `target_type` (`claim` \| `digest`), `item_id` | Exports a verified claim report or digest to a structured Markdown file. |

Run standalone MCP server:
```bash
PYTHONPATH=backend backend/.venv/bin/python backend/app/mcp/server.py
```

---

## 4. RAG Knowledge Base & Source Credibility

The system maintains a verified index of authoritative publishers and scientific institutions:
- **Major Wire Services**: Reuters (0.98), Associated Press (0.98), AFP Fact Check (0.96)
- **Fact-Checking Networks**: Snopes (0.94), PolitiFact (0.94), FactCheck.org (0.96), Full Fact (0.95)
- **Scientific & Health Authorities**: World Health Organization (0.99), CDC (0.97), Nature (0.99), The Lancet (0.99), NASA (0.99)

Every piece of evidence gathered is automatically mapped against this registry to compute a credibility-weighted score.

---

## 5. Safety Guardrails & IFCN Standards

1. **"Unverifiable" Mandate**: Rather than hallucinating or speculating on unproven rumors, the system strictly outputs `Unverifiable` with low confidence.
2. **Mandatory Dual-Sided Balance**: Verdict cards present both supporting and contradicting evidence columns.
3. **Transparent Citations**: Every claim features direct hyperlinks to sources, publisher domains, and reliability ratings.
4. **Bias Audit**: The Critic node evaluates whether counter-arguments were thoroughly researched.

---

## 6. Design System & Architecture Compliance

Adhering strictly to [Rules.md](file:///home/brooklyn/Projects/Citizen_Scheme_Elegiblity/Rules.md):
- **Solid Professional Color Palette**: Strictly no loud gradients. Employs an editorial solid palette:
  - Background: Solid Slate-50 (`#f8fafc`)
  - Masthead & Borders: Solid Slate-900 (`#0f172a`) and Slate-200 (`#e2e8f0`)
  - True: Solid Emerald (`#047857`)
  - False: Solid Crimson (`#b91c1c`)
  - Misleading: Solid Amber (`#b45309`)
  - Unverifiable: Solid Slate-600 (`#475569`)
- **Modular Separation of Concerns**:
  - `routes/` decouple HTTP transport from business logic.
  - `controllers/` coordinate operations, state management, and SSE streaming.
  - `agents/` house isolated LangGraph nodes.
  - `services/` manage search engines, RAG lookup, and database interfaces.

---

## 7. Directory Structure

```
.
├── Rules.md                      # UI and Backend architectural constraints
├── Task.md                       # Component specifications & agent design
├── README.md                     # Complete project documentation
├── backend/
│   ├── run.py                    # Fast development server launcher
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variables template
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint with CORS & SQLite lifespan
│   │   ├── core/
│   │   │   ├── config.py         # Settings & environment configuration
│   │   │   ├── database.py       # SQLite schema, tables & seeding
│   │   │   └── llm.py            # Multi-provider LLM connector & heuristic fallback
│   │   ├── schemas/              # Pydantic schemas (claim, digest, eval)
│   │   ├── services/
│   │   │   ├── tavily_service.py # Tavily web search with fallback engine
│   │   │   └── rag_service.py    # Archive similarity search & source credibility
│   │   ├── mcp/
│   │   │   ├── tools.py          # save_digest, get_saved_claims, export_markdown
│   │   │   └── server.py         # FastMCP protocol server
│   │   ├── agents/
│   │   │   ├── state.py          # LangGraph AgentState TypedDict
│   │   │   ├── claim_extractor.py
│   │   │   ├── evidence_retriever.py
│   │   │   ├── verdict_judge.py
│   │   │   ├── critic.py         # Reflection conditional edge
│   │   │   ├── digest_writer.py
│   │   │   └── graph.py          # Compiled LangGraph workflow
│   │   ├── controllers/          # Business logic coordinators
│   │   │   ├── fact_check_controller.py
│   │   │   ├── digest_controller.py
│   │   │   ├── archive_controller.py
│   │   │   └── eval_controller.py
│   │   ├── routes/               # FastAPI route modules
│   │   └── data/
│   │       ├── trusted_sources.json
│   │       ├── seed_fact_checks.json
│   │       └── eval_claims.json
└── Frontend/
    ├── package.json
    ├── vite.config.js            # Vite configuration with API proxy to backend
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx               # Main layout & router
    │   ├── index.css             # Tailwind CSS v4 solid styles
    │   ├── api/
    │   │   └── apiClient.js      # Centralized HTTP & SSE stream client
    │   ├── controllers/          # React hooks managing view logic
    │   │   ├── useFactCheckController.js
    │   │   ├── useDigestController.js
    │   │   ├── useArchiveController.js
    │   │   └── useEvalController.js
    │   ├── components/           # Reusable UI components
    │   │   ├── Navbar.jsx
    │   │   ├── StatusBadge.jsx
    │   │   ├── PipelineVisualizer.jsx
    │   │   ├── ClaimVerdictCard.jsx
    │   │   └── ConfigModal.jsx
    │   └── routes/               # High-level view pages
    │       ├── FactCheckView.jsx
    │       ├── DigestView.jsx
    │       ├── ArchiveView.jsx
    │       └── EvaluationView.jsx
```

---

## 8. Getting Started & Installation

### Prerequisites
- Python 3.12+ (managed automatically via `uv`)
- Node.js 18+ and `npm`

### Step 1: Set Up Backend
```bash
# In project root:
uv pip install --python backend/.venv -r backend/requirements.txt

# Start backend server:
PYTHONPATH=backend backend/.venv/bin/python backend/run.py
```
*Backend will be running at `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`).*

### Step 2: Set Up Frontend
```bash
# In another terminal:
npm --prefix Frontend install
npm --prefix Frontend run dev
```
*Frontend will be running at `http://localhost:5173` with automatic `/api` proxy.*

---

## 9. API Endpoints

### Fact-Checking
- `POST /api/fact-check`: Execute fact check synchronously.
- `POST /api/fact-check/stream`: Execute fact check with real-time SSE event stream for LangGraph nodes and reflections.

### Daily Digest
- `POST /api/digest/generate`: Compile verified claims into Markdown digest.
- `GET /api/digest/list`: List compiled digests.
- `GET /api/digest/{id}/export`: Download digest Markdown file.

### Knowledge Archive & Sources (MCP)
- `GET /api/archive/claims`: Retrieve saved claims with optional keyword and verdict filters.
- `GET /api/archive/claims/{id}/export`: Download individual claim verification report.
- `GET /api/archive/sources`: List accredited sources in RAG registry.

### Benchmark Evaluation
- `GET /api/eval/dataset`: View labeled ground-truth test cases.
- `POST /api/eval/run`: Run automated accuracy and guardrail verification benchmark.

---

## 10. Benchmark & Accuracy Evaluation

The evaluation suite tests the full pipeline against standard test cases:
- Viral health myths (e.g. *Hot water viral cures* -> `False`)
- Scientific discoveries (e.g. *JWST WASP-96b atmospheric water* -> `True`)
- Social media hoaxes (e.g. *UNESCO best anthem* -> `False`)
- Historical distortions (e.g. *Carrots night vision* -> `Misleading`)
- Vague rumors (e.g. *Classified alien wreckage in unnamed trench* -> `Unverifiable` guardrail test)

Access the **Benchmark Evaluation** tab in the web UI to run this live and view the accuracy percentage and guardrail compliance rate.
