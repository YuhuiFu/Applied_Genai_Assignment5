from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional


class CustomerDatabaseMCP:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        return {k: row[k] for k in row.keys()}

    # ---------- MCP tools ----------

    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def list_customers(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        if status:
            cur.execute("SELECT * FROM customers WHERE status = ? LIMIT ?", (status, limit))
        else:
            cur.execute("SELECT * FROM customers LIMIT ?", (limit,))
        rows = cur.fetchall()
        return [self._row_to_dict(r) for r in rows]

    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not data:
            return self.get_customer(customer_id)

        allowed = {"name", "email", "phone", "status"}
        fields = [f for f in data if f in allowed]
        if not fields:
            return self.get_customer(customer_id)

        set_clause = ", ".join([f"{f} = ?" for f in fields] + ["updated_at = ?"])
        values = [data[f] for f in fields] + [datetime.utcnow().isoformat()]

        cur = self.conn.cursor()
        cur.execute(
            f"UPDATE customers SET {set_clause} WHERE id = ?",
            (*values, customer_id),
        )
        self.conn.commit()
        return self.get_customer(customer_id)

    def create_ticket(self, customer_id: int, issue: str, priority: str = "medium") -> Dict[str, Any]:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO tickets (customer_id, issue, status, priority, created_at)
            VALUES (?, ?, 'open', ?, ?)
            """,
            (customer_id, issue, priority, datetime.utcnow().isoformat()),
        )
        self.conn.commit()

        ticket_id = cur.lastrowid
        cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()
        return self._row_to_dict(row)

    def get_customer_history(self, customer_id: int) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM tickets WHERE customer_id = ? ORDER BY created_at DESC, id DESC",
            (customer_id,),
        )
        rows = cur.fetchall()
        return [self._row_to_dict(r) for r in rows]

    def close(self) -> None:
        self.conn.close()
