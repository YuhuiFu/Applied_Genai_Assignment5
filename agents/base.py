from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal


AgentName = Literal["user", "router", "customer_data", "support"]


@dataclass
class Message:
    sender: AgentName
    receiver: AgentName
    purpose: str
    content: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.sender}->{self.receiver}] ({self.purpose}) {self.content} | {self.payload}"


@dataclass
class ConversationState:
    conversation_id: str
    user_query: str
    inferred_intents: List[str] = field(default_factory=list)
    customer_id: Optional[int] = None
    customer_record: Optional[Dict[str, Any]] = None
    tickets: List[Dict[str, Any]] = field(default_factory=list)
    log: List[str] = field(default_factory=list)

    def add_log(self, text: str) -> None:
        self.log.append(text)
        print(text)


class BaseAgent:
    def __init__(self, name: AgentName):
        self.name = name

    def handle(self, message: Message, state: ConversationState) -> List[Message]:
        raise NotImplementedError
