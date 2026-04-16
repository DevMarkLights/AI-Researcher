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
from .loadModel import llm_small as llm
import re
import asyncio
from ddgs import DDGS



SYSTEM_PROMPT = """You are a focused researcher. Given a specific research question and 
optionally some web search snippets, provide a thorough and detailed summary of the key facts.
Write 6-8 sentences covering the main concepts, important nuances, real-world implications,
and any relevant examples. Be factual and comprehensive."""


async def _search(query: str, client_id: str) -> str:
    """DuckDuckGo search — no API key needed."""
    try:
        def do_search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=1))
            
        results = await asyncio.to_thread(do_search)
        if not results:
            return ([],"")
        snippets = "\n".join(f"- {r['title']}: {r['body']}" for r in results)
        
        formatted = ""
        for r in results:
            formatted = f"{r['title']} - {r['href']}"
        
        return (formatted,snippets)
    except Exception as e:
        print(f"   ⚠️  Search failed ({e}), using LLM knowledge only")
        return ([],"")


async def researcher_node(state: AgentState) -> AgentState:
    
    subtask = state["subtask"]
    index = state['subtask_index']
    await manager.broadcast(message={"message" : f"Researcher {index}: Investigating subtasks..."}, client_id=state['clientID'])
    await manager.broadcast(message={"message" : f"     {subtask}"}, client_id=state['clientID'])

    f, snippets = await _search(subtask,client_id=state['clientID'])
    
    formatted = f

    context = f"Research question: {subtask}"
    if snippets:
        context += f"\n\nWeb search results:\n{snippets}"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=context)
    ]

    response = await llm.ainvoke(messages)
    results = (f"## {subtask}\n\n{response.content.strip()}")
    


    return {"research_results": [results], 'sources': [formatted]}


def clean_snippet(text: str) -> str:
    # Insert space before capital letters that are jammed together
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Fix lowercase words jammed together (harder, but this helps common cases)
    text = re.sub(r'([a-zA-Z])of([a-zA-Z])', r'\1 of \2', text)
    text = re.sub(r'([a-zA-Z])in([A-Z])', r'\1 in \2', text)
    return text