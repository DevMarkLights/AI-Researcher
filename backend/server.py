import asyncio
import uuid

from fastapi import FastAPI, File, UploadFile, Body, Form, WebSocket, WebSocketDisconnect
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from ConnectionManager import manager
from fastapi.responses import FileResponse


from langgraph.graph import StateGraph, END
from state import AgentState
from agents.planner import planner_node
from agents.researcher import researcher_node
from agents.writer import writer_node
from pathlib import Path
from agents.loadModel import llm_small, llm_large #load model one time

import logging

logging.basicConfig(level=logging.ERROR)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)

BASE_DIR = Path(__file__).parent
reports_dir = BASE_DIR / "reports"
reports_dir.mkdir(exist_ok=True)

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
    
    
    client_id = query["clientID"]
    result = await ai_researcher.ainvoke({"query": query['question'], "clientID":client_id})
    
    Path('output/report.txt').parent.mkdir(parents=True, exist_ok=True)
    Path('output/report.txt').write_text(result["report"])

    await manager.broadcast(message={"message":"Report Finished","done":True}, client_id=client_id)
    return {"report": result["report"]}

@app.get("/ai-researcher/file")
async def getFile(clientID:str,format:str,filename:str):
    file_path = f'reports/{clientID}_report.{format}'
    
    if format == 'pdf': #fix for mobile devices opening new page instead of just downloading pdfs
        return FileResponse(
            file_path,
            filename=f"{filename}.pdf",
            media_type="application/octet-stream"  # forces download instead of open
        )
    
    return FileResponse(path=file_path,filename=filename+'.'+format)
    


@app.websocket("/ai-researcher/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: str=None):
    await manager.connect(websocket,client_id=client_id)
    

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
            await websocket.receive() # keep alive
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f'Websocket error {e}')
    
    finally:
        manager.disconnect(websocket=websocket,clientID=client_id)
        # when client disconnets remove all the files they generated from server
        folder = BASE_DIR / 'reports'
        for file in folder.glob(f"{client_id}*"):
            file.unlink()
        task.cancel()
        
        

app.mount("/ai-researcher", StaticFiles(directory="dist", html=True), name="static")



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8085,
        log_level="debug",
        reload=True,
        ws_ping_interval=30, 
        ws_ping_timeout=300
    )

