from datetime import date
from typing import Dict, List
from HRMS.schemas import LeaveApplyRequest
from HRMS.database import get_connection, initialize_db

class LeaveManager:
    def __init__(self):
        initialize_db()
        self.conn = get_connection()

    def _ensure_employee_balance(self, emp_id: str, balance: int = 20) -> None:
        # Allow explicit setting of the balance (replace existing value if present)
        self.conn.execute(
            """
            INSERT OR IGNORE INTO leave_balances(emp_id, balance)
            VALUES (?, ?)
            """,
            (emp_id, balance),
        )
        self.conn.commit()

    def get_leave_balance(self, employee_id: str) -> str:
        row = self.conn.execute(
            """
            SELECT COUNT(*) AS leave_count
            FROM leave_history
            WHERE emp_id = ?
            """,
            (employee_id,)
        ).fetchone()

        taken = row["leave_count"]
        balance = 20 - taken

        return f"{employee_id} has {balance} leave days remaining."

    def apply_leave(self, req: LeaveApplyRequest) -> str:
        employee_id = req.emp_id
        self._ensure_employee_balance(employee_id)
        leave_dates = [d.isoformat() for d in req.leave_dates]
        existing_rows = self.conn.execute(
            """
            SELECT leave_date
            FROM leave_history
            WHERE emp_id = ?
            """,
            (employee_id,)
        ).fetchall()

        existing_dates = {
            row["leave_date"]
            for row in existing_rows
        }
        duplicate_dates = [
            leave_date
            for leave_date in leave_dates
            if leave_date in existing_dates
        ]

        if duplicate_dates:
            raise ValueError(
                "Leave already exists for: "
                + ", ".join(duplicate_dates)
            )
        balance_row = self.conn.execute("SELECT balance FROM leave_balances WHERE emp_id = ?", (employee_id,)).fetchone()
        if not balance_row:
            return "Employee ID not found."
        requested = len(leave_dates)
        available = balance_row["balance"]
        if available < requested:
            return f"Insufficient leave balance: requested {requested}, available {available}."

        request_id_row = self.conn.execute("SELECT MAX(request_id) as max_id FROM leave_history WHERE emp_id = ?", (employee_id,)).fetchone()
        request_id = (request_id_row["max_id"] or 0) + 1
        self.conn.execute(
            "UPDATE leave_balances SET balance = ? WHERE emp_id = ?",
            (available - requested, employee_id),
        )
        for leave_date in leave_dates:
            self.conn.execute(
                "INSERT INTO leave_history(emp_id, leave_date, request_id) VALUES (?, ?, ?)",
                (employee_id, leave_date, request_id),
            )
        self.conn.commit()
        return (
            f"Leave applied for {requested} day(s). Remaining balance: "
            f"{available - requested}"
        )

    def get_leave_history(self, employee_id: str) -> str:
        rows = self.conn.execute(
            "SELECT leave_date FROM leave_history WHERE emp_id = ? ORDER BY leave_date",
            (employee_id,),
        ).fetchall()
        if not rows:
            return f"No leave history found for {employee_id}."
        dates = [date.fromisoformat(row["leave_date"]).strftime("%B %d, %Y") for row in rows]
        return f"Leave history for {employee_id}: {', '.join(dates)}."

    def get_leave_history_records(self, employee_id: str) -> List[str]:
        rows = self.conn.execute(
            "SELECT leave_date FROM leave_history WHERE emp_id = ? ORDER BY leave_date",
            (employee_id,),
        ).fetchall()
        return [date.fromisoformat(row["leave_date"]).strftime("%B %d, %Y") for row in rows]

    def ensure_employee_balance(self, emp_id: str, balance: int = 20) -> None:
        self._ensure_employee_balance(emp_id, balance)

    def add_leave_history(self, emp_id: str, leave_date: date, request_id: int) -> None:
        self._ensure_employee_balance(emp_id)
        self.conn.execute(
            "INSERT INTO leave_history(emp_id, leave_date, request_id) VALUES (?, ?, ?)",
            (emp_id, leave_date.isoformat(), request_id),
        )
        # decrement the available balance when history is added (seeded or manual)
        row = self.conn.execute(
            "SELECT balance FROM leave_balances WHERE emp_id = ?",
            (emp_id,),
        ).fetchone()
        if row:
            new_bal = max(0, row["balance"] - 1)
            self.conn.execute(
                "UPDATE leave_balances SET balance = ? WHERE emp_id = ?",
                (new_bal, emp_id),
            )
        self.conn.commit()

    def list_balances(self):
        rows = self.conn.execute("""
            SELECT
                e.emp_id,
                e.name,
                e.email,
                20 - COUNT(lh.leave_date) AS balance
            FROM employees e
            LEFT JOIN leave_history lh
                ON e.emp_id = lh.emp_id
            GROUP BY e.emp_id, e.name, e.email
            ORDER BY e.emp_id
        """).fetchall()

        return [dict(row) for row in rows]
