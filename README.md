# 🤖 Multi-Agent Research & Report Writer

A multi-agent system built with **LangGraph**, **Groq** (production), and **Ollama** (local dev)
that researches any topic and produces a structured report with inline citations.
Deployed at [marks-pi.com/ai-researcher](https://marks-pi.com/ai-researcher)

---

## Architecture

```
User Query
    │
    ▼
┌─────────────┐
│   Planner   │  Breaks query into 3-5 specific, search-optimized subtasks
│    Agent    │  (structured JSON output)
└──────┬──────┘
       │  subtasks[]
       ▼
┌──────────────────────────────────────────┐
│         Parallel Researcher Agents       │
│                                          │
│  Researcher 1 │ Researcher 2 │ ...       │  Concurrent DuckDuckGo search + LLM synthesis
│  (subtask 1)  │ (subtask 2)  │           │  per subtask via LangGraph Send API
└──────────────────────────┬───────────────┘
                           │  research_results[] + sources[]
                           ▼
              ┌─────────────────────┐
              │    Writer Agent     │  Deduplicates sources, synthesizes findings
              │                     │  into a structured report with inline citations
              └─────────┬───────────┘
                        │
                        ▼
          ┌─────────────────────────┐
          │  PDF  │  DOCX  │  TXT   │  Downloadable report formats
          └─────────────────────────┘
```

State is passed immutably between nodes via `AgentState` (TypedDict) with `operator.add`
annotated fields for parallel result accumulation. The graph is compiled once and reused.

---

## Key Technical Features

- **Parallel agent execution** — Researcher nodes fan out concurrently via LangGraph `Send` API, reducing research time from O(n subtasks) to O(1)
- **Real-time WebSocket streaming** — Live progress updates broadcast to the client as each agent completes
- **Source deduplication** — Duplicate citations filtered before writer synthesis
- **Multi-format export** — Reports generated as PDF, DOCX, and TXT
- **Dual LLM backend** — Groq (llama-3.3-70b-versatile) in production, Ollama locally via `USE_LOCAL` env var

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| Backend | FastAPI |
| Frontend | React + Vite |
| LLM (prod) | Groq — llama-3.3-70b-versatile |
| LLM (local) | Ollama — llama3.1:8b |
| Search | DuckDuckGo (no API key required) |
| Real-time | WebSockets |
| Deployment | Raspberry Pi 5 + Cloudflare Tunnel |

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Add your GROQ_API_KEY, set USE_LOCAL=true for local dev

# 3a. Local dev (Ollama)
ollama serve
ollama pull llama3.1:8b
python server.py

# 3b. Production (Groq)
USE_LOCAL=false python server.py
```

---

## Environment Variables

```bash
GROQ_API_KEY=your_key
USE_LOCAL=true                        # true = Ollama, false = Groq
GROQ_MODEL_LARGE=llama-3.3-70b-versatile
GROQ_MODEL_SMALL=llama-3.1-8b-instant
```

---

## Project Structure

```
AI-Researcher/
├── backend/
│   ├── server.py          # FastAPI app, WebSocket manager, endpoints
│   ├── graph.py           # LangGraph graph definition & compilation
│   ├── state.py           # AgentState (TypedDict)
│   ├── agents/
│   │   ├── planner.py     # Subtask decomposition
│   │   ├── researcher.py  # Parallel search + LLM synthesis per subtask
│   │   └── writer.py      # Report synthesis + file export
│   ├── reports/           # Generated PDF, DOCX, TXT outputs
│   └── requirements.txt
└── frontend/
    ├── src/
    └── vite.config.js
```

---
