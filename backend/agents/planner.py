"""
Planner Agent
Breaks the user query into focused research subtasks.
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from state import AgentState
import json
import re
import os
from dotenv import load_dotenv
load_dotenv()

from ConnectionManager import manager
import asyncio



if os.getenv("USE_LOCAL") == "true":
    print('local model')
    llm = ChatOllama(model="llama3.2:3b", temperature=0)
else:
    print('cloud model')
    llm = ChatGroq(model=os.getenv("GROQ_MODEL"), temperature=0)


SYSTEM_PROMPT = """You are a research planner. Given a research topic, break it down into
3-5 focused subtasks that a researcher should investigate.

Respond ONLY with a JSON array of strings. No explanation, no markdown, no code blocks.
Example: ["What is X?", "History of X", "Current applications of X"]"""


async def planner_node(state: AgentState) -> AgentState:
    # print("🗂️  Planner: Breaking down query into subtasks...")
    await manager.broadcast({"message": "🗂️  Planner: Breaking down query into subtasks..."})


    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Research topic: {state['query']}")
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()

    try:
        subtasks = json.loads(raw)
        if not isinstance(subtasks, list):
            raise ValueError("Expected a list")
    except (json.JSONDecodeError, ValueError):
        # Fallback: extract lines that look like subtask strings
        subtasks = [line.strip().strip('"').strip("'") 
                    for line in raw.splitlines() 
                    if line.strip() and line.strip() not in ("{", "}")]

    # print(f"   → {len(subtasks)} subtasks identified")
    await manager.broadcast({"message" : f"   → {len(subtasks)} subtasks identified"})


    return {**state, "subtasks": subtasks}
