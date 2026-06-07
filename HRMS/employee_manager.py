import sqlite3
from typing import List, Dict, Optional
from difflib import get_close_matches
from HRMS.schemas import EmployeeCreate
from HRMS.database import get_connection, initialize_db


class EmployeeManager:
    def __init__(self):
        initialize_db()
        self.conn = get_connection()

    def get_next_emp_id(self) -> str:
        cursor = self.conn.execute(
            "SELECT emp_id FROM employees ORDER BY emp_id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if not row:
            return "E001"
        max_id = int(row["emp_id"][1:])
        return f"E{max_id + 1:03}"

    def add_employee(self, emp: EmployeeCreate) -> None:

        if self.conn.execute(
            "SELECT 1 FROM employees WHERE emp_id = ?", (emp.emp_id,)
        ).fetchone():
            raise ValueError(f"Employee ID '{emp.emp_id}' already exists.")

        if self.conn.execute(
            "SELECT 1 FROM employees WHERE LOWER(email) = LOWER(?)", (emp.email,)
        ).fetchone():
            raise ValueError(f"Email '{emp.email}' already exists.")

        if (
            emp.manager_id
            and not self.conn.execute(
                "SELECT 1 FROM employees WHERE emp_id = ?", (emp.manager_id,)
            ).fetchone()
        ):
            raise ValueError(f"Manager ID '{emp.manager_id}' does not exist.")

        self.conn.execute(
            """
            INSERT INTO employees ( emp_id, name, manager_id, email, hired_date )
            VALUES (?,?, ?,?,date('now'))""",
            (
                emp.emp_id,
                emp.name,
                emp.manager_id,
                emp.email,
            ),
        )

        self.conn.execute(
            """
            INSERT OR IGNORE INTO leave_balances(emp_id,balance)
            VALUES(?, 20)
            """,
            (emp.emp_id,),
        )

        self.conn.commit()

    def get_manager(self, emp_id: str) -> str:
        cursor = self.conn.execute(
            "SELECT manager_id FROM employees WHERE emp_id = ?", (emp_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Employee ID '{emp_id}' not found.")
        mgr_id = row["manager_id"]
        if not mgr_id:
            return "No manager assigned."
        manager_row = self.conn.execute(
            "SELECT name FROM employees WHERE emp_id = ?", (mgr_id,)
        ).fetchone()
        return (
            f"{mgr_id}: {manager_row['name']}"
            if manager_row
            else "Manager record missing."
        )

    def search_employee_by_name(
        self, name_query: str, n: int = 5, cutoff: float = 0.6
    ) -> List[str]:
        rows = self.conn.execute("SELECT emp_id, name FROM employees").fetchall()
        matches = get_close_matches(
            name_query, [row["name"] for row in rows], n=n, cutoff=cutoff
        )
        return [row["emp_id"] for row in rows if row["name"] in matches]

    def get_employee_details(self, emp_id: str) -> Dict[str, Optional[str]]:
        row = self.conn.execute(
            "SELECT emp_id, name, manager_id, email, hired_date FROM employees WHERE emp_id = ?",
            (emp_id,),
        ).fetchone()
        if not row:
            raise ValueError(f"Employee ID '{emp_id}' not found.")
        return dict(row)

    def update_employee(
        self,
        emp_id: str,
        name: Optional[str] = None,
        manager_id: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        if not self.conn.execute(
            "SELECT emp_id FROM employees WHERE emp_id = ?", (emp_id,)
        ).fetchone():
            raise ValueError(f"Employee ID '{emp_id}' not found.")

        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if manager_id is not None:
            if manager_id == "":
                manager_id = None
            elif not self.conn.execute(
                "SELECT emp_id FROM employees WHERE emp_id = ?", (manager_id,)
            ).fetchone():
                raise ValueError(f"Manager ID '{manager_id}' does not exist.")
            updates.append("manager_id = ?")
            params.append(manager_id)

        if email is not None:
            existing_email = self.conn.execute(
                """
                SELECT emp_id
                FROM employees
                WHERE LOWER(email) = LOWER(?)
                """,
                (email,),
            ).fetchone()

            if existing_email and existing_email["emp_id"] != emp_id:
                raise ValueError(f"Email '{email}' already exists.")

            updates.append("email = ?")
            params.append(email)

        if not updates:
            raise ValueError("At least one field must be updated.")

        params.append(emp_id)
        self.conn.execute(
            f"UPDATE employees SET {', '.join(updates)} WHERE emp_id = ?",
            params,
        )
        self.conn.commit()

    def get_direct_reports(self, manager_id: str) -> List[str]:
        if not self.conn.execute(
            "SELECT * FROM employees WHERE emp_id = ?", (manager_id,)
        ).fetchone():
            raise ValueError(f"Manager ID '{manager_id}' not found.")
        rows = self.conn.execute(
            "SELECT emp_id FROM employees WHERE manager_id = ?", (manager_id,)
        ).fetchall()
        return [row["emp_id"] for row in rows]

    def list_employees(self) -> List[Dict[str, str]]:
        rows = self.conn.execute(
            "SELECT emp_id, name, manager_id, email, hired_date FROM employees ORDER BY emp_id"
        ).fetchall()
        return [dict(row) for row in rows]
