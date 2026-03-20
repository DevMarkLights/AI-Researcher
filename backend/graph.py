"""
Multi-Agent Research & Report Writer
LangGraph + Ollama (llama3.2:3b)
"""

from langgraph.graph import StateGraph, END
from state import AgentState
from agents.planner import planner_node
from agents.researcher import researcher_node
from agents.writer import writer_node



def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", END)

    return graph.compile()

    
# running standalone
if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Multi-agent research writer")
    parser.add_argument("query", type=str, help="Research topic or question")
    parser.add_argument("--output", type=str, default="output/report.txt", help="Output file path")
    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)

    app = build_graph()

    print(f"\n🔍 Starting research on: {args.query}\n")
    result = app.invoke({"query": args.query})

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(result["report"])

    print(f"\n✅ Report written to {args.output}")
    print(f"\n--- Subtasks planned ---")
    for t in result.get("subtasks", []):
        print(f"  • {t}")
