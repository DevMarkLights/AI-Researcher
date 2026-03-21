import asyncio

from fastapi import FastAPI, File, UploadFile, Body, Form, WebSocket
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from ConnectionManager import manager

from langgraph.graph import StateGraph, END
from state import AgentState
from agents.planner import planner_node
from agents.researcher import researcher_node
from agents.writer import writer_node
from pathlib import Path
from agents.loadModel import llm #load model one time

import logging

logging.basicConfig(level=logging.ERROR)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # MUST be FALSE
    allow_methods=["*"],
    allow_headers=["*"],
)

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

ai_researcher = build_graph()


@app.post("/ai-researcher/ask")
async def ask_question(query: dict = Body(...)):

    result = await ai_researcher.ainvoke({"query": query['question']})
    
    Path('output/report.txt').parent.mkdir(parents=True, exist_ok=True)
    Path('output/report.txt').write_text(result["report"])

    await manager.broadcast({"message":"Report Finished"})
    return {"report": result["report"]}


@app.websocket("/ai-researcher/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
        
    async def keepalive():
        while True:
            await asyncio.sleep(10)  # ping every 10 seconds for keep alive
            try:
                await websocket.send_json({"ping": True})
            except:
                break

    task = asyncio.create_task(keepalive())
    try:
        while True:
            await asyncio.Future() # keep alive
    except Exception as e:
        print(f'Websocket error {e}')
    finally:
        manager.disconnect(websocket)
        task.cancel()
        
        

app.mount("/ai-researcher", StaticFiles(directory="dist", html=True), name="static")

    


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8085,
        log_level="debug",
        ws_ping_interval=30, 
        ws_ping_timeout=300
    )

