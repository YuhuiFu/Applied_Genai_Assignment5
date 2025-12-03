import sqlite3
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP, Context

DB_PATH = "support.db"
mcp = FastMCP("support-db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class PatchCustomer(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None

@mcp.tool()
async def get_customer(ctx: Context, customer_id: int):
    with get_conn() as c:
        row = c.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
        if not row:
            return {"found": False}
        return {"found": True, "customer": dict(row)}

@mcp.tool()
async def list_customers(ctx: Context, status: str = "active", limit: int = 10):
    with get_conn() as c:
        rows = c.execute(
            "SELECT * FROM customers WHERE status=? ORDER BY created_at DESC LIMIT ?",
            (status, limit)
        ).fetchall()
        return {"status": status, "customers": [dict(r) for r in rows]}

@mcp.tool()
async def update_customer(ctx: Context, customer_id: int, data: PatchCustomer):
    updates = []
    vals = []
    for k, v in data.dict(exclude_none=True).items():
        updates.append(f"{k}=?")
        vals.append(v)
    if not updates:
        return {"updated": False, "reason": "no fields"}
    vals.append(customer_id)
    with get_conn() as c:
        cur = c.execute(f"UPDATE customers SET {','.join(updates)} WHERE id=?", vals)
        c.commit()
        if cur.rowcount == 0:
            return {"updated": False, "reason": "not found"}
        row = c.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
        return {"updated": True, "customer": dict(row)}

@mcp.tool()
async def create_ticket(ctx: Context, customer_id: int, issue: str, priority: str = "medium"):
    if priority not in ("low", "medium", "high"):
        return {"created": False, "reason": "invalid priority"}
    with get_conn() as c:
        row = c.execute("SELECT id FROM customers WHERE id=?", (customer_id,)).fetchone()
        if not row:
            return {"created": False, "reason": "customer missing"}
        cur = c.execute(
            "INSERT INTO tickets (customer_id, issue, status, priority) VALUES (?, ?, 'open', ?)",
            (customer_id, issue, priority)
        )
        c.commit()
        tid = cur.lastrowid
        t = c.execute("SELECT * FROM tickets WHERE id=?", (tid,)).fetchone()
        return {"created": True, "ticket": dict(t)}

@mcp.tool()
async def get_customer_history(ctx: Context, customer_id: int):
    with get_conn() as c:
        cust = c.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
        if not cust:
            return {"found": False}
        tickets = c.execute(
            "SELECT * FROM tickets WHERE customer_id=? ORDER BY created_at DESC",
            (customer_id,)
        ).fetchall()
        return {
            "found": True,
            "customer": dict(cust),
            "tickets": [dict(t) for t in tickets]
        }

if __name__ == "__main__":
    mcp.run()
