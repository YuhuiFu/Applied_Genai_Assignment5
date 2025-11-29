from __future__ import annotations

from typing import List

from .base import BaseAgent, Message, ConversationState
from mcp_server.mcp import CustomerDatabaseMCP


class CustomerDataAgent(BaseAgent):
    def __init__(self, mcp: CustomerDatabaseMCP):
        super().__init__("customer_data")
        self.mcp = mcp

    def handle(self, message: Message, state: ConversationState) -> List[Message]:
        state.add_log(f"CustomerDataAgent received: {message.purpose}")
        out: List[Message] = []

        if message.purpose == "get_customer_info":
            cid = message.payload["customer_id"]
            cust = self.mcp.get_customer(cid)
            state.customer_record = cust
            out.append(
                Message(
                    "customer_data",
                    "router",
                    "customer_info_result",
                    "Customer info fetched.",
                    {"customer": cust},
                )
            )

        elif message.purpose == "get_customer_history":
            cid = message.payload["customer_id"]
            history = self.mcp.get_customer_history(cid)
            state.tickets = history
            out.append(
                Message(
                    "customer_data",
                    "router",
                    "customer_history_result",
                    "Customer history fetched.",
                    {"tickets": history},
                )
            )

        elif message.purpose == "list_customers":
            status = message.payload.get("status")
            limit = message.payload.get("limit", 50)
            customers = self.mcp.list_customers(status=status, limit=limit)
            out.append(
                Message(
                    "customer_data",
                    "router",
                    "customers_list_result",
                    "Customer list fetched.",
                    {"customers": customers},
                )
            )

        elif message.purpose == "update_customer":
            cid = message.payload["customer_id"]
            data = message.payload["data"]
            updated = self.mcp.update_customer(cid, data)
            state.customer_record = updated
            out.append(
                Message(
                    "customer_data",
                    "router",
                    "customer_update_result",
                    "Customer updated.",
                    {"customer": updated},
                )
            )

        elif message.purpose == "create_ticket":
            cid = message.payload["customer_id"]
            issue = message.payload["issue"]
            priority = message.payload.get("priority", "medium")
            ticket = self.mcp.create_ticket(cid, issue, priority)
            out.append(
                Message(
                    "customer_data",
                    "router",
                    "ticket_create_result",
                    "Ticket created.",
                    {"ticket": ticket},
                )
            )

        return out
