from typing import List, Dict, Optional
from datetime import datetime
from HRMS.schemas import TicketCreate, TicketStatusUpdate
from HRMS.database import get_connection, initialize_db


class TicketManager:
    def __init__(self):
        initialize_db()
        self.conn = get_connection()

    def _next_ticket_id(self) -> str:
        row = self.conn.execute("SELECT ticket_id FROM tickets ORDER BY ticket_id DESC LIMIT 1").fetchone()
        if not row:
            return "T0001"
        last_id = int(row["ticket_id"][1:])
        return f"T{last_id + 1:04d}"

    def create_ticket(self, req: TicketCreate) -> str:
        ticket_id = self._next_ticket_id()
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            "INSERT INTO tickets(ticket_id, emp_id, item, reason, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (ticket_id, req.emp_id, req.item, req.reason, "Open", now, now),
        )
        self.conn.commit()
        return f"Ticket {ticket_id} created for {req.emp_id}."

    def update_ticket_status(self, req: TicketStatusUpdate, ticket_id: str) -> str:
        cursor = self.conn.execute(
            "UPDATE tickets SET status = ?, updated_at = ? WHERE ticket_id = ?",
            (req.status, datetime.utcnow().isoformat(), ticket_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Ticket '{ticket_id}' not found.")
        self.conn.commit()
        return f"Ticket {ticket_id} status updated to {req.status}."

    def list_tickets(
        self,
        employee_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        query = "SELECT ticket_id, emp_id, item, reason, status, created_at, updated_at FROM tickets"
        params = []
        conditions = []
        if employee_id:
            conditions.append("emp_id = ?")
            params.append(employee_id)
        if status:
            conditions.append("LOWER(status) = LOWER(?)")
            params.append(status)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
