from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
from agents.coordinator import CoordinatorAgent, CoordinatorCard
from agents.records import RecordsAgent, RecordsCard
from agents.assist import AssistAgent, AssistCard

app = FastAPI(title="A2A Multi-Agent Service")

class Task(BaseModel):
    input: str

class RouteReply(BaseModel):
    route: str
    messages: List[Dict[str, Any]]

class RecordsReply(BaseModel):
    tool: str
    result: Dict[str, Any]
    messages: List[Dict[str, Any]]

class AssistReply(BaseModel):
    last_step: str
    result: Dict[str, Any]
    missing: List[str]
    messages: List[Dict[str, Any]]

def dump_card(card):
    if hasattr(card, "model_dump"): return card.model_dump()
    if hasattr(card, "dict"): return card.dict()
    return card.__dict__

# ------ AgentCard Endpoints ------
@app.get("/a2a/coordinator/.well-known/agent-card.json")
def card_coord(): return dump_card(CoordinatorCard)

@app.get("/a2a/records/.well-known/agent-card.json")
def card_records(): return dump_card(RecordsCard)

@app.get("/a2a/assist/.well-known/agent-card.json")
def card_assist(): return dump_card(AssistCard)

# ------ Task Endpoints ------
@app.post("/a2a/coordinator/tasks", response_model=RouteReply)
async def tasks_coord(task: Task):
    state = await CoordinatorAgent.ainvoke({
        "transcript": [{"role": "user", "content": task.input}],
        "dispatch_target": None
    })
    return RouteReply(route=state["dispatch_target"], messages=state["transcript"])

@app.post("/a2a/records/tasks", response_model=RecordsReply)
async def tasks_records(task: Task):
    st = await RecordsAgent.ainvoke({
        "dialog": [{"role": "user", "content": task.input}],
        "invoked_tool": None,
        "payload": None
    })
    return RecordsReply(
        tool=st.get("invoked_tool") or "",
        result=st.get("payload") or {},
        messages=st["dialog"]
    )

@app.post("/a2a/assist/tasks", response_model=AssistReply)
async def tasks_assist(task: Task):
    st = await AssistAgent.ainvoke({
        "thread": [{"role": "user", "content": task.input}],
        "last_step": None,
        "ticket_data": None,
        "missing": None
    })
    return AssistReply(
        last_step=st.get("last_step") or "",
        result=st.get("ticket_data") or {},
        missing=st.get("missing") or [],
        messages=st["thread"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
