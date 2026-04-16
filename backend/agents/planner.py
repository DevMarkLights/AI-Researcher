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


from .loadModel import llm_small as llm



SYSTEM_PROMPT = """You are a research planner. Given a research topic, break it down into
3-5 focused subtasks that a researcher should investigate.

Each subtask must:
- Be specific to the exact topic provided, not generic
- Include key terminology from the topic
- Be phrased as a search query, not a category label

BAD (too generic):
Topic: "Quantum computing in cryptography"
["Definition of quantum computing", "Applications of quantum computing", "Challenges"]

GOOD (specific):
Topic: "Quantum computing in cryptography"
["How quantum computers break RSA and elliptic curve encryption", "Post-quantum cryptography algorithms like CRYSTALS-Kyber and NTRU", "Timeline for quantum computers threatening current encryption standards"]

Respond ONLY with a JSON array of strings. No explanation, no markdown, no code blocks."""


async def planner_node(state: AgentState) -> AgentState:
    # print("🗂️  Planner: Breaking down query into subtasks...")
    await manager.broadcast(message={"message": "Planner: Breaking down query into subtasks..."}, client_id=state['clientID'])


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
    # await manager.broadcast(message={"message" : f"   → {len(subtasks)} subtasks identified"}, client_id=state['clientID'])


    return {**state, "subtasks": subtasks}
