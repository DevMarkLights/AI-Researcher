"""
Researcher Agent
For each subtask, uses DuckDuckGo search to gather real information.
Falls back to LLM knowledge if search fails.
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from state import AgentState
import os
from dotenv import load_dotenv
load_dotenv()
from ConnectionManager import manager
from .loadModel import llm


SYSTEM_PROMPT = """You are a focused researcher. Given a specific research question and 
optionally some web search snippets, provide a thorough and detailed summary of the key facts.
Write 6-8 sentences covering the main concepts, important nuances, real-world implications,
and any relevant examples. Be factual and comprehensive."""


async def _search(query: str) -> str:
    """DuckDuckGo search — no API key needed."""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return ""
        snippets = "\n".join(f"- {r['title']}: {r['body']}" for r in results)
        return snippets
    except Exception as e:
        # print(f"   ⚠️  Search failed ({e}), using LLM knowledge only")
        await manager.broadcast({"message" : f"Search failed ({e}), using LLM knowledge only"})
        return ""


async def researcher_node(state: AgentState) -> AgentState:
    # print("🔬 Researcher: Investigating subtasks...")
    await manager.broadcast({"message" : "Researcher: Investigating subtasks..."})


    results = []
    for i, subtask in enumerate(state["subtasks"]):
        # print(f"   [{i+1}/{len(state['subtasks'])}] {subtask}")
        await manager.broadcast({"message" : f"   [{i+1}/{len(state['subtasks'])}] {subtask}"})

        snippets = await _search(subtask)

        context = f"Research question: {subtask}"
        if snippets:
            context += f"\n\nWeb search results:\n{snippets}"

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=context)
        ]

        response = llm.invoke(messages)
        results.append(f"## {subtask}\n\n{response.content.strip()}")

    return {**state, "research_results": results}
