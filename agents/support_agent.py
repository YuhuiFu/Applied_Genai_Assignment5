from __future__ import annotations

from typing import List, Tuple, Dict, Any

from .base import BaseAgent, Message, ConversationState
from mcp_server.mcp import CustomerDatabaseMCP


class SupportAgent(BaseAgent):
    def __init__(self, mcp: CustomerDatabaseMCP):
        super().__init__("support")
        self.mcp = mcp

    def handle(self, message: Message, state: ConversationState) -> List[Message]:
        state.add_log(f"SupportAgent received: {message.purpose}")
        out: List[Message] = []

        # Simple support for customer info / upgrade
        if message.purpose == "handle_support_request":
            customer = message.payload.get("customer") or state.customer_record or {}
            intent = message.payload.get("intent", "general")

            if intent == "get_customer_info":
                reply = (
                    f"Customer {customer.get('id')} is {customer.get('name')} "
                    f"({customer.get('email')}). Status: {customer.get('status')}."
                )
            elif intent == "upgrade_account":
                reply = (
                    "I can help you upgrade your account. "
                    "For this demo, assume your plan is upgraded to premium "
                    "and a confirmation email has been sent."
                )
            else:
                reply = "General support reply (demo)."

            out.append(
                Message("support", "router", "support_reply", reply, {"reply": reply})
            )

        # Negotiation for cancel + billing (Scenario 2)
        elif message.purpose == "negotiate_cancel_billing":
            comment = "I can handle cancel + billing, but I need billing context (tickets) first."
            out.append(
                Message(
                    "support",
                    "router",
                    "support_needs_billing_context",
                    comment,
                    {},
                )
            )

        # After billing context (Scenario 2)
        elif message.purpose == "handle_billing_and_cancel":
            cid = state.customer_id or message.payload.get("customer_id", 5)
            ticket = self.mcp.create_ticket(
                cid,
                "Billing issue: double charge & cancellation request",
                "high",
            )
            reply = (
                f"I've created a high-priority billing ticket #{ticket['id']} "
                "and initiated your cancellation. Our team will review your "
                "billing history and process your refund as quickly as possible."
            )
            out.append(
                Message(
                    "support",
                    "router",
                    "support_reply",
                    reply,
                    {"reply": reply, "ticket": ticket},
                )
            )

        # Gather open tickets for customers (complex query)
        elif message.purpose == "gather_open_tickets":
            customers = message.payload["customers"]
            open_tickets: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
            for c in customers:
                hist = self.mcp.get_customer_history(c["id"])
                for t in hist:
                    if t["status"] == "open":
                        open_tickets.append((c, t))
            out.append(
                Message(
                    "support",
                    "router",
                    "open_tickets_result",
                    "Open tickets gathered.",
                    {"open_tickets": open_tickets},
                )
            )

        # Gather high-priority tickets for customers (Scenario 3)
        elif message.purpose == "gather_high_priority_tickets":
            customers = message.payload["customers"]
            hp_tickets: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
            for c in customers:
                hist = self.mcp.get_customer_history(c["id"])
                for t in hist:
                    if t["priority"] == "high":
                        hp_tickets.append((c, t))
            out.append(
                Message(
                    "support",
                    "router",
                    "high_priority_tickets_result",
                    "High priority tickets gathered.",
                    {"high_priority_tickets": hp_tickets},
                )
            )

        # Escalation-only billing issue (Escalation test query)
        elif message.purpose == "handle_billing_escalation":
            cid = state.customer_id or 5
            ticket = self.mcp.create_ticket(
                cid,
                "Urgent billing issue: charged twice, refund requested",
                "high",
            )
            reply = (
                f"I've created a high-priority ticket #{ticket['id']} "
                "for your billing issue. Our billing team will review and "
                "process your refund as soon as possible."
            )
            out.append(
                Message(
                    "support",
                    "router",
                    "support_reply",
                    reply,
                    {"reply": reply, "ticket": ticket},
                )
            )

        return out
