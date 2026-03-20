# 🤖 Multi-Agent Research & Report Writer

A multi-agent system built with **LangGraph** and **Ollama for local** and **Groq** for produciton that researches any topic and produces a structured markdown or txt report.

## Architecture

```
User Query
    │
    ▼
┌─────────────┐
│   Planner   │  Breaks query into 3-5 focused subtasks
│    Agent    │  (structured JSON output)
└──────┬──────┘
       │  subtasks[]
       ▼
┌─────────────┐
│ Researcher  │  For each subtask: DuckDuckGo search → LLM synthesis
│    Agent    │  Falls back to LLM knowledge if search unavailable
└──────┬──────┘
       │  research_results[]
       ▼
┌─────────────┐
│   Writer    │  Synthesizes all findings into a markdown report
│    Agent    │
└──────┬──────┘
       │
       ▼
  report.md
```

Each agent is a **LangGraph node**. State is passed immutably between nodes via `AgentState` (TypedDict). The graph is compiled once and reused.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure Ollama is running with llama3.2:3b
ollama serve
ollama pull llama3.2:3b

# 3. Run
python graph.py "What is retrieval-augmented generation and why does it matter?"
```

Output is written to `output/report.txt` by default.

```bash
# Custom output path
python graph.py "History of transformer architectures" --output my_report.txt
```
