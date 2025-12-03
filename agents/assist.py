from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
import re
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, TransportProtocol
from mcp_server.mcp_core import create_ticket

@dataclass
class AssistState:
    thread: List[Dict[str, Any]]
    last_step: Optional[str] = None
    ticket_data: Optional[Dict[str, Any]] = None
    missing: Optional[List[str]] = None

def extract_id(txt):
    m = re.search(r"customer\s+id\s+(\d+)", txt.lower())
    return int(m.group(1)) if m else None

def extract_priority(txt):
    txt = txt.lower()
    for p in ["low", "medium", "high"]:
        if p in txt:
            return p
    return None

def extract_issue(txt):
    m = re.search(r"(?:about|regarding)\s+(.+)", txt, flags=re.I)
    return m.group(1) if m else None

async def assist_node(state: AssistState, rt: Runtime):
    txt = state.thread[-1]["content"]
    cid = extract_id(txt)
    priority = extract_priority(txt)
    issue = extract_issue(txt)

    missing = []
    if cid is None: missing.append("customer_id")
    if issue is None: missing.append("issue")
    if priority is None: missing.append("priority")

    if missing:
        msg = "Need more info:\n" + "\n".join(f"- {m}" for m in missing)
        return {
            "thread": state.thread + [{"role": "agent", "content": msg}],
            "missing": missing
        }

    result = await create_ticket(None, cid, issue, priority)
    return {
        "thread": state.thread + [{"role": "agent", "content": "Ticket created."}],
        "last_step": "create_ticket",
        "ticket_data": result,
        "missing": []
    }

gb = StateGraph(AssistState)
gb.add_node("assist", assist_node)
gb.add_edge("__start__", "assist")
AssistAgent = gb.compile()

AssistCard = AgentCard(
    name="AssistUnit",
    url="http://localhost:10012",
    description="Creates tickets & handles negotiation of missing fields.",
    version="1.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[AgentSkill(
        id="ticket",
        name="Create Ticket",
        description="Open support tickets via MCP."
    )]
)
