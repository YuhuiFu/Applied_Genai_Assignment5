from dataclasses import dataclass
from typing import Any, Dict, List
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, TransportProtocol

@dataclass
class CoordinatorState:
    transcript: List[Dict[str, Any]]
    dispatch_target: str | None = None

async def coordinator_node(state: CoordinatorState, rt: Runtime):
    msg = state.transcript[-1]["content"].lower()
    if any(x in msg for x in ["ticket", "support", "issue"]):
        target = "assist_agent"
    else:
        target = "records_agent"

    return {
        "transcript": state.transcript + [
            {"role": "system", "content": f"route={target}"}
        ],
        "dispatch_target": target
    }

graph_builder = StateGraph(CoordinatorState)
graph_builder.add_node("coord", coordinator_node)
graph_builder.add_edge("__start__", "coord")
CoordinatorAgent = graph_builder.compile()

CoordinatorCard = AgentCard(
    name="CoordinatorUnit",
    url="http://localhost:10010",
    description="Routes customer queries to Records or Assist.",
    version="1.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[AgentSkill(
        id="route",
        name="Route Task",
        description="Select appropriate specialist agent.",
        tags=["routing"]
    )]
)
