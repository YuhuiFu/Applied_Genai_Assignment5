# mcp_server/customer_mcp_server.py

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import sqlite3

from mcp.server.fastmcp import FastMCP

# Import your instructor's DB helper
from database_setup import DatabaseSetup

DB_PATH = Path(__file__).resolve().parent.parent / "support.db"


# ---------- DB bootstrap using the instructor's helper ----------

def ensure_database() -> None:
    """
    Ensure the database file exists, tables are created, and sample data is inserted.
    Uses the DatabaseSetup class from database_setup.py.
    """
    setup = DatabaseSetup(db_path=str(DB_PATH))
    setup.connect()
    setup.create_tables()
    setup.create_triggers()
    setup.insert_sample_data()
    setup.close()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {k: row[k] for k in row.keys()}


# ---------- MCP server + tools ----------

mcp = FastMCP("customer_support_db", json_response=True)


@mcp.tool()
def get_customer(customer_id: int) -> Optional[Dict[str, Any]]:
    """
    get_customer(customer_id) - uses customers.id
    """
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cur.fetchone()
        return row_to_dict(row) if row else None


@mcp.tool()
def list_customers(status: str = "active", limit: int = 20) -> List[Dict[str, Any]]:
    """
    list_customers(status, limit) - uses customers.status
    """
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM customers WHERE status = ? "
            "ORDER BY id LIMIT ?",
            (status, limit),
        )
        return [row_to_dict(r) for r in cur.fetchall()]


@mcp.tool()
def update_customer(customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    update_customer(customer_id, data) - uses customers fields.
    Allowed fields: name, email, phone, status.
    """
    allowed = {"name", "email", "phone", "status"}
    fields = [k for k in data.keys() if k in allowed]

    if not fields:
        return {"ok": False, "error": "No valid fields to update."}

    set_clause = ", ".join(f"{f} = ?" for f in fields)
    params = [data[f] for f in fields]

    with get_connection() as conn:
        conn.execute(
            f"UPDATE customers SET {set_clause}, updated_at = ? WHERE id = ?",
            (*params, datetime.utcnow().isoformat(), customer_id),
        )
        conn.commit()
        cur = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cur.fetchone()
        if row:
            return {"ok": True, "customer": row_to_dict(row)}
        return {"ok": False, "error": "Customer not found."}


@mcp.tool()
def create_ticket(
    customer_id: int,
    issue: str,
    priority: str = "medium",
) -> Dict[str, Any]:
    """
    create_ticket(customer_id, issue, priority) - uses tickets fields
    """
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO tickets (customer_id, issue, status, priority, created_at)
            VALUES (?, ?, 'open', ?, ?)
            """,
            (customer_id, issue, priority, now),
        )
        ticket_id = cur.lastrowid
        conn.commit()
        cur = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()
        return row_to_dict(row)


@mcp.tool()
def get_customer_history(customer_id: int) -> List[Dict[str, Any]]:
    """
    get_customer_history(customer_id) - uses tickets.customer_id
    """
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM tickets WHERE customer_id = ? ORDER BY created_at DESC",
            (customer_id,),
        )
        return [row_to_dict(r) for r in cur.fetchall()]


if __name__ == "__main__":
    # 1) Init DB and sample data
    ensure_database()

    # 2) Start MCP server over SSE HTTP
    #    This exposes /tools/list and /tools/call for MCP Inspector
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8003,
    )
