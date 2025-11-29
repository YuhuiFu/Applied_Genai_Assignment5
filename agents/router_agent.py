from __future__ import annotations

from typing import List, Optional

from .base import BaseAgent, Message, ConversationState
from .customer_data_agent import CustomerDataAgent
from .support_agent import SupportAgent
from mcp_server.mcp import CustomerDatabaseMCP


class RouterAgent(BaseAgent):
    """
    Orchestrates all flows and runs all assignment scenarios.
    """

    def __init__(self, mcp: CustomerDatabaseMCP, default_customer_id: int = 5):
        super().__init__("router")
        self.mcp = mcp
        self.data_agent = CustomerDataAgent(mcp)
        self.support_agent = SupportAgent(mcp)
        self.default_customer_id = default_customer_id

    def infer_intents(self, text: str) -> List[str]:
        lower = text.lower()
        intents: List[str] = []

        if "get customer information" in lower or "get customer info" in lower or "information for id" in lower:
            intents.append("get_customer_info")
        if "upgrade" in lower:
            intents.append("upgrade_account")
        if "cancel" in lower and "subscription" in lower:
            intents.append("cancel_subscription")
        if "billing" in lower or "charged twice" in lower or "refund" in lower:
            intents.append("billing_issue")
        if "active customers" in lower and "open tickets" in lower:
            intents.append("active_with_open_tickets")
        if "high-priority" in lower and "premium customers" in lower:
            intents.append("high_priority_premium_tickets")
        if "update my email" in lower:
            intents.append("update_email")
        if "ticket history" in lower:
            intents.append("ticket_history")

        return intents

    def extract_customer_id(self, text: str) -> Optional[int]:
        tokens = text.replace(",", " ").split()
        for i, t in enumerate(tokens):
            if t.upper() == "ID" and i + 1 < len(tokens):
                try:
                    return int(tokens[i + 1])
                except ValueError:
                    pass
        return None

    def extract_email(self, text: str) -> Optional[str]:
        for tok in text.replace(",", " ").split():
            if "@" in tok:
                return tok
        return None

    def handle(self, message: Message, state: ConversationState) -> List[Message]:
        state.add_log(f"Router received: {message.purpose} from {message.sender}")
        out: List[Message] = []
        intents = state.inferred_intents

        # 1) Entry: user query
        if message.sender == "user":
            intents = self.infer_intents(message.content)
            state.inferred_intents = intents
            cid = self.extract_customer_id(message.content) or self.default_customer_id
            state.customer_id = cid

            # Routing by scenario / test query
            if "get_customer_info" in intents and len(intents) == 1:
                # Simple Query
                out.append(
                    Message(
                        "router",
                        "customer_data",
                        "get_customer_info",
                        "Fetch customer info",
                        {"customer_id": cid},
                    )
                )
            elif "upgrade_account" in intents:
                # Coordinated Query
                out.append(
                    Message(
                        "router",
                        "customer_data",
                        "get_customer_info",
                        "Fetch customer info before upgrade",
                        {"customer_id": cid},
                    )
                )
            elif "cancel_subscription" in intents and "billing_issue" in intents:
                # Scenario 2: Negotiation
                out.append(
                    Message(
                        "router",
                        "support",
                        "negotiate_cancel_billing",
                        "Can you handle cancel + billing?",
                        {},
                    )
                )
            elif "billing_issue" in intents and "cancel_subscription" not in intents:
                # Escalation-only
                out.append(
                    Message(
                        "router",
                        "support",
                        "handle_billing_escalation",
                        "Urgent billing escalation",
                        {},
                    )
                )
            elif "active_with_open_tickets" in intents:
                # Complex Query
                out.append(
                    Message(
                        "router",
                        "customer_data",
                        "list_customers",
                        "List active customers",
                        {"status": "active", "limit": 100},
                    )
                )
            elif "high_priority_premium_tickets" in intents:
                # Scenario 3: multi-step
                out.append(
                    Message(
                        "router",
                        "customer_data",
                        "list_customers",
                        "List active customers",
                        {"status": "active", "limit": 100},
                    )
                )
            elif "update_email" in intents and "ticket_history" in intents:
                # Multi-intent: update email + history
                new_email = self.extract_email(message.content)
                out.append(
                    Message(
                        "router",
                        "customer_data",
                        "update_customer",
                        "Update email",
                        {"customer_id": cid, "data": {"email": new_email}},
                    )
                )
            else:
                # Fallback: get info
                out.append(
                    Message(
                        "router",
                        "customer_data",
                        "get_customer_info",
                        "Default fetch",
                        {"customer_id": cid},
                    )
                )

        # 2) Responses from CustomerDataAgent
        elif message.sender == "customer_data":
            if message.purpose == "customer_info_result":
                cust = message.payload["customer"]
                if not cust:
                    out.append(
                        Message(
                            "router",
                            "user",
                            "final_response",
                            "Sorry, we could not find your customer record.",
                            {},
                        )
                    )
                else:
                    if "upgrade_account" in intents:
                        out.append(
                            Message(
                                "router",
                                "support",
                                "handle_support_request",
                                "Please upgrade this account.",
                                {"customer": cust, "intent": "upgrade_account"},
                            )
                        )
                    else:
                        out.append(
                            Message(
                                "router",
                                "support",
                                "handle_support_request",
                                "Provide customer info.",
                                {"customer": cust, "intent": "get_customer_info"},
                            )
                        )

            elif message.purpose == "customers_list_result":
                customers = message.payload["customers"]
                if "active_with_open_tickets" in intents:
                    out.append(
                        Message(
                            "router",
                            "support",
                            "gather_open_tickets",
                            "Gather open tickets for these customers.",
                            {"customers": customers},
                        )
                    )
                elif "high_priority_premium_tickets" in intents:
                    out.append(
                        Message(
                            "router",
                            "support",
                            "gather_high_priority_tickets",
                            "Gather high priority tickets for these customers.",
                            {"customers": customers},
                        )
                    )

            elif message.purpose == "customer_history_result":
                if "cancel_subscription" in intents and "billing_issue" in intents:
                    out.append(
                        Message(
                            "router",
                            "support",
                            "handle_billing_and_cancel",
                            "Use history for billing+cancel.",
                            {"tickets": message.payload["tickets"]},
                        )
                    )
                elif "update_email" in intents and "ticket_history" in intents:
                    cust = state.customer_record
                    tickets = message.payload["tickets"]
                    lines = [f"Your email has been updated to: {cust.get('email')}."]
                    if not tickets:
                        lines.append("You currently have no tickets in your history.")
                    else:
                        lines.append("Here is your ticket history:")
                        for t in tickets:
                            lines.append(
                                f"- Ticket {t['id']}: '{t['issue']}' "
                                f"(status={t['status']}, priority={t['priority']})"
                            )
                    text = "\n".join(lines)
                    out.append(
                        Message("router", "user", "final_response", text, {})
                    )

            elif message.purpose == "customer_update_result":
                cid = state.customer_id
                state.customer_record = message.payload["customer"]
                out.append(
                    Message(
                        "router",
                        "customer_data",
                        "get_customer_history",
                        "Get history after email update.",
                        {"customer_id": cid},
                    )
                )

        # 3) Responses from SupportAgent
        elif message.sender == "support":
            if message.purpose == "support_reply":
                reply = message.payload["reply"]
                out.append(
                    Message("router", "user", "final_response", reply, {})
                )

            elif message.purpose == "support_needs_billing_context":
                cid = state.customer_id or self.default_customer_id
                out.append(
                    Message(
                        "router",
                        "customer_data",
                        "get_customer_history",
                        "Get billing history",
                        {"customer_id": cid},
                    )
                )

            elif message.purpose in ("open_tickets_result", "high_priority_tickets_result"):
                if message.purpose == "open_tickets_result":
                    open_tickets = message.payload["open_tickets"]
                    if not open_tickets:
                        text = "There are no active customers with open tickets."
                    else:
                        lines = []
                        for c, t in open_tickets:
                            lines.append(
                                f"Customer {c['id']} ({c['name']}): ticket {t['id']} "
                                f"'{t['issue']}' status={t['status']} priority={t['priority']}"
                            )
                        text = "Active customers with open tickets:\n" + "\n".join(lines)
                else:
                    hp_tickets = message.payload["high_priority_tickets"]
                    if not hp_tickets:
                        text = (
                            "There are no high-priority tickets for premium customers "
                            "(in this demo, we treat all active customers as premium)."
                        )
                    else:
                        lines = []
                        for c, t in hp_tickets:
                            lines.append(
                                f"Customer {c['id']} ({c['name']}): ticket {t['id']} "
                                f"'{t['issue']}' status={t['status']} priority={t['priority']}"
                            )
                        text = "High-priority tickets for premium customers:\n" + "\n".join(lines)

                out.append(
                    Message("router", "user", "final_response", text, {})
                )

        return out

    def run_query(self, query: str) -> ConversationState:
        state = ConversationState("conv", query)
        state.add_log(f"\n=== USER QUERY: {query} ===")
        queue: List[Message] = [Message("user", "router", "user_query", query, {})]

        for _ in range(30):
            if not queue:
                break
            msg = queue.pop(0)

            if msg.receiver == "router":
                queue += self.handle(msg, state)
            elif msg.receiver == "customer_data":
                queue += self.data_agent.handle(msg, state)
            elif msg.receiver == "support":
                queue += self.support_agent.handle(msg, state)
            elif msg.receiver == "user":
                state.add_log(f"\nFINAL RESPONSE: {msg.content}\n")
                break

        return state
