# 🤖 Multi-Agent Research & Report Writer

A multi-agent system built with **LangGraph** and **Ollama** that researches any topic and produces a structured markdown report.

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

Output is written to `output/report.md` by default.

```bash
# Custom output path
python graph.py "History of transformer architectures" --output my_report.md
```

## Migrating to a Cloud Provider

The LLM is instantiated in one place per agent. To switch from local to cloud:

```python
# LOCAL (current)
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2:3b", temperature=0)

# ANTHROPIC (cheapest: claude-haiku-4-5)
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0)

# OPENAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

Nothing else needs to change — LangGraph is model-agnostic.

## Adding Observability (LangSmith)

```bash
export LANGSMITH_API_KEY=your_key   # free tier available
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT=research-agent
```

Every graph run will now appear in LangSmith with full node-by-node traces.

## Project Structure

```
research-agent/
├── graph.py          # LangGraph graph definition & entrypoint
├── state.py          # Shared AgentState (TypedDict)
├── requirements.txt
├── agents/
│   ├── planner.py    # Subtask decomposition
│   ├── researcher.py # Search + summarization per subtask
│   └── writer.py     # Report synthesis
└── output/           # Generated reports
```

## Interview Talking Points

- **Why LangGraph over CrewAI?** LangGraph gives explicit control over the graph topology and state transitions, which matters for production systems where you need to debug failure modes.
- **Why TypedDict for state?** It's the LangGraph convention — typed, serializable, and works with LangSmith tracing out of the box.
- **How would you scale this?** Add a supervisor node that routes subtasks to parallel researcher nodes, reducing latency from O(n) to O(1).
- **How would you eval this?** Score report quality with an LLM-as-judge on dimensions: factual grounding, coverage of subtasks, coherence.
