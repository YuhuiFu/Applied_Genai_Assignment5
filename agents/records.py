from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
import re
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, TransportProtocol
from mcp_server.mcp_core import get_customer, get_customer_history

@dataclass
class RecordsState:
    dialog: List[Dict[str, Any]]
    invoked_tool: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

def extract_id(text):
    m = re.search(r"customer\s+id\s+(\d+)", text.lower())
    if m:
        return int(m.group(1))
    return None

async def records_node(state: RecordsState, rt: Runtime):
    last = state.dialog[-1]["content"]
    cid = extract_id(last)
    if cid is None:
        return {
            "dialog": state.dialog + [{"role": "agent", "content": "Missing customer id."}]
        }

    if "history" in last.lower():
        result = await get_customer_history(None, cid)
        return {
            "dialog": state.dialog + [{"role": "agent", "content": "History retrieved"}],
            "invoked_tool": "get_customer_history",
            "payload": result
        }

    result = await get_customer(None, cid)
    return {
        "dialog": state.dialog + [{"role": "agent", "content": "Profile retrieved"}],
        "invoked_tool": "get_customer",
        "payload": result
    }

gb = StateGraph(RecordsState)
gb.add_node("records", records_node)
gb.add_edge("__start__", "records")
RecordsAgent = gb.compile()

RecordsCard = AgentCard(
    name="RecordsUnit",
    url="http://localhost:10011",
    description="Fetches customer profiles and history via MCP.",
    version="1.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[AgentSkill(
        id="lookup",
        name="Lookup Customer",
        description="Retrieve customer data via MCP."
    )]
)
