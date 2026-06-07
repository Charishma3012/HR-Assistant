from typing import Dict, List
from datetime import date, timedelta, datetime
import random
from HRMS.schemas import EmployeeCreate, MeetingCreate, TicketCreate


def seed_services(employee_manager, leave_manager, meeting_manager, ticket_manager):
    existing = employee_manager.list_employees()
    if existing:
        return {
            "employees": len(existing),
            "leave_records": len(leave_manager.list_balances()),
            "meetings": len(meeting_manager.list_all_meetings()),
            "tickets": len(ticket_manager.list_tickets()),
        }

    employees_data = [
        {"emp_id": "E001", "name": "Sarah Johnson", "manager_id": None, "email": "sarah.johnson@atliq.com"},
        {"emp_id": "E002", "name": "Michael Chen", "manager_id": None, "email": "michael.chen@atliq.com"},
        {"emp_id": "E003", "name": "David Wilson", "manager_id": "E001", "email": "david.wilson@atliq.com"},
        {"emp_id": "E004", "name": "Tony Sharma", "manager_id": "E003", "email": "tony.sharma@atliq.com"},
        {"emp_id": "E005", "name": "James Rodriguez", "manager_id": "E003", "email": "james.rodriguez@atliq.com"},
        {"emp_id": "E006", "name": "Emily Kim", "manager_id": "E002", "email": "emily.kim@atliq.com"},
        {"emp_id": "E007", "name": "Carlos Mendez", "manager_id": "E006", "email": "carlos.mendez@atliq.com"},
        {"emp_id": "E008", "name": "Lisa Wong", "manager_id": "E006", "email": "lisa.wong@atliq.com"},
    ]

    for employee in employees_data:
        emp = EmployeeCreate(
            emp_id=employee["emp_id"],
            name=employee["name"],
            manager_id=employee["manager_id"],
            email=employee["email"],
        )
        employee_manager.add_employee(emp)

    current_date = date.today()
    request_id_counter = 1

    for employee in employees_data:
        emp_id = employee["emp_id"]
        leave_balance = random.randint(5, 20)
        leave_manager.ensure_employee_balance(emp_id, leave_balance)

        num_leaves = random.randint(1, 5)
        for _ in range(num_leaves):
            leave_date = current_date - timedelta(days=random.randint(1, 90))
            leave_manager.add_leave_history(emp_id, leave_date, request_id_counter)
            if random.random() > 0.7:
                for j in range(1, random.randint(2, 4)):
                    leave_manager.add_leave_history(emp_id, leave_date + timedelta(days=j), request_id_counter)
            request_id_counter += 1

    meeting_types = ["Team Sync", "Project Review", "Client Meeting", "1:1", "Planning"]
    for employee in employees_data:
        num_meetings = random.randint(2, 4)
        for _ in range(num_meetings):
            meeting_date = current_date + timedelta(days=random.randint(0, 10))
            meeting_hour = random.randint(9, 16)
            meeting_dt = datetime.combine(meeting_date, datetime.min.time()).replace(hour=meeting_hour)
            meeting_manager.schedule_meeting(MeetingCreate(
                emp_ids=[employee["emp_id"]],
                start_dt=meeting_dt,
                duration_minutes=60,
                topic=random.choice(meeting_types),
            ))

    ticket_items = ["Laptop", "Monitor", "Keyboard", "Mouse", "Headset", "Office Chair", "Software License"]
    ticket_reasons = ["New hire setup", "Replacement for broken item", "Upgrade request", "Project requirement", "Ergonomic needs"]
    for _ in range(random.randint(8, 15)):
        employee = random.choice(employees_data)
        ticket_manager.create_ticket(TicketCreate(
            emp_id=employee["emp_id"],
            item=random.choice(ticket_items),
            reason=random.choice(ticket_reasons),
        ))

    return {
        "employees": len(employees_data),
        "leave_records": len(leave_manager.list_balances()),
        "meetings": len(meeting_manager.list_all_meetings()),
        "tickets": len(ticket_manager.list_tickets()),
    }
