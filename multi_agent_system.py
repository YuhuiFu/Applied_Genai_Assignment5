from __future__ import annotations

from database import DatabaseSetup
from mcp_server import CustomerDatabaseMCP
from agents import RouterAgent


DB_PATH = "support.db"


def ensure_database(db_path: str = DB_PATH) -> None:
    """
    Uses DatabaseSetup to:
      - connect
      - create tables
      - create triggers
      - insert sample data
      - close connection
    """
    db = DatabaseSetup(db_path=db_path)
    try:
        db.connect()
        db.create_tables()
        db.create_triggers()
        db.insert_sample_data()
    finally:
        db.close()


def main() -> None:
    # Initialize DB & MCP
    ensure_database(DB_PATH)
    mcp = CustomerDatabaseMCP(DB_PATH)
    router = RouterAgent(mcp, default_customer_id=5)

    # ---- Scenario 1: Task Allocation ----
    router.run_query("I need help with my account, customer ID 5")

    # ---- Scenario 2: Negotiation / Escalation ----
    router.run_query("I want to cancel my subscription but I'm having billing issues")

    # ---- Scenario 3: Multi-step Coordination ----
    router.run_query("What's the status of all high-priority tickets for premium customers?")

    # ---- Test Query 1: Simple Query ----
    router.run_query("Get customer information for ID 5")

    # ---- Test Query 2: Coordinated Query ----
    router.run_query("I'm customer 5 and need help upgrading my account")

    # ---- Test Query 3: Complex Query ----
    router.run_query("Show me all active customers who have open tickets")

    # ---- Test Query 4: Escalation ----
    router.run_query("I've been charged twice, please refund immediately!")

    # ---- Test Query 5: Multi-Intent ----
    router.run_query("Update my email to new_email@example.com and show my ticket history")

    mcp.close()


if __name__ == "__main__":
    main()
