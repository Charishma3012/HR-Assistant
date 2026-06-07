from emails import EmailSender
from HRMS import *
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP

# load the env
from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime, timedelta
from utils import seed_services

employee_manager = EmployeeManager()
meeting_manager = MeetingManager()
leave_manager = LeaveManager()
ticket_manager = TicketManager()

seed_services(employee_manager, leave_manager, meeting_manager, ticket_manager)

emailer = EmailSender(
    smtp_server="smtp.gmail.com",
    port=587,
    username=os.getenv("CB_EMAIL"),
    password=os.getenv("CB_EMAIL_PWD"),
    use_tls=True
)

mcp = FastMCP("hr-assist")

@mcp.tool()
def add_employee(emp_name:str, manager_id:str, email:str) -> str:
    """
    Add a new employee to the HRMS system. Employee ID is auto-generated.
    :param emp_name: Employee name
    :param manager_id: Manager ID
    :param email: Employee email
    :return: Confirmation message including the generated employee ID
    """
    generated_id = employee_manager.get_next_emp_id()
    emp = EmployeeCreate(
        emp_id=generated_id,
        name=emp_name,
        manager_id=manager_id,
        email=email
    )
    employee_manager.add_employee(emp)
    return f"Employee {emp_name} added successfully with Employee ID {generated_id}."

@mcp.tool()
def update_employee_details(emp_id: str, name: Optional[str] = None, manager_id: Optional[str] = None, email: Optional[str] = None) -> str:
    """
    Update an existing employee's details.
    :param emp_id: Employee ID to update
    :param name: New full name of the employee
    :param manager_id: New manager ID for the employee
    :param email: New email address of the employee
    :return: Success message
    """
    if name is None and manager_id is None and email is None:
        raise ValueError("At least one of name, manager_id, or email must be provided to update.")

    employee_manager.update_employee(
        emp_id=emp_id,
        name=name,
        manager_id=manager_id,
        email=email,
    )
    return f"Employee {emp_id} updated successfully."

@mcp.tool()
def get_employee_details(name: Optional[str] = None, query: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Get employee details by employee ID or name.
    :param name: Employee name
    :param query: Employee ID (e.g. E001) or name
    :return: Employee details
    """
    query_text = (query or name or "").strip()
    if not query_text:
        raise ValueError("Either query or name must be provided.")

    if query_text.upper().startswith("E"):
        try:
            return employee_manager.get_employee_details(query_text.upper())
        except ValueError:
            pass

    matches = employee_manager.search_employee_by_name(query_text)
    if len(matches) == 0:
        raise ValueError(f"No employees found for {query_text}.")

    emp_id = matches[0]
    return employee_manager.get_employee_details(emp_id)

@mcp.tool()
def send_email(to_emails: List[str], subject: str, body: str, html: bool = False) -> None:
    emailer.send_email(subject, body, to_emails, from_email=emailer.username, html=html)
    return "Email sent successfully."


@mcp.tool()
def create_ticket(emp_id: str, item: str, reason:str) -> str:
    """
    Create a ticket for buying required items for an employee.
    :param emp_id: Employee ID
    :param item: Item requested (Laptop, ID Card, etc.)
    :param reason: Reason for the request
    :return: Confirmation message
    """
    ticket_req = TicketCreate(emp_id=emp_id, item=item, reason=reason)
    return ticket_manager.create_ticket(ticket_req)

@mcp.tool()
def update_ticket_status(ticket_id: str, status: str) -> str:
    """
    Update the status of a ticket.
    :param ticket_id: Ticket ID
    :param status: New status of the ticket
    :return: Confirmation message
    """
    ticket_status_update = TicketStatusUpdate(status=status)
    return ticket_manager.update_ticket_status(ticket_status_update, ticket_id)

@mcp.tool()
def list_tickets(employee_id: str, status: str) -> List[Dict[str, str]]:
    """
    List tickets for an employee with optional status filter.
    :param employee_id: Employee ID
    :param status: Ticket status (optional)
    :return: List of tickets
    """
    return ticket_manager.list_tickets(employee_id=employee_id or None, status=status or None)


@mcp.tool()
def schedule_meeting(employee_ids: List[str], start_datetime: datetime, duration_minutes: int, topic: str) -> str:
    """
    Schedule a meeting for one or more employees.
    :param employee_ids: List of Employee IDs
    :param start_datetime: Date and time the meeting starts
    :param duration_minutes: Meeting duration in minutes
    :param topic: Topic of the meeting
    :return: Confirmation message
    """
    meeting_req = MeetingCreate(
        emp_ids=employee_ids,
        start_dt=start_datetime,
        duration_minutes=duration_minutes,
        topic=topic,
    )
    return meeting_manager.schedule_meeting(meeting_req)


@mcp.tool()
def get_meetings(employee_id: str) -> str:
    """
    Get the list of meetings scheduled for an employee.
    :param employee_id: Employee ID
    :return: List of meetings
    """
    return meeting_manager.get_meetings(employee_id)


@mcp.tool()
def cancel_meeting(meeting_code: str) -> str:
    """
    Cancel a scheduled meeting by meeting code.
    :param meeting_code: Meeting code (e.g. M001)
    :return: Confirmation message
    """
    meeting_req = MeetingCancelRequest(
        meeting_code=meeting_code
    )
    return meeting_manager.cancel_meeting(meeting_req)


@mcp.tool()
def get_employee_leave_balance(emp_id: str) -> str:
    """
    Get the leave balance of an employee.
    :param emp_id: Employee ID
    :return: Leave balance message
    """
    return leave_manager.get_leave_balance(emp_id)

@mcp.tool()
def apply_leave(emp_id: str, leave_dates: list) -> str:
    """
    Apply for leave for an employee.
    :param emp_id: Employee ID
    :param leave_dates: List of leave dates
    :return: Leave application status message
    """
    req = LeaveApplyRequest(emp_id=emp_id, leave_dates=leave_dates)
    return leave_manager.apply_leave(req)


@mcp.tool()
def get_leave_history(emp_id: str) -> str:
    """
    Get the leave history of an employee.
    :param emp_id: Employee ID
    :return: Leave history message
    """
    return leave_manager.get_leave_history(emp_id)


@mcp.tool()
def onboard_employee(emp_name: str, manager_name: str, email: Optional[str] = None) -> str:
    """
    Onboard a new employee with manager assignment, welcome email, equipment tickets, and an intro meeting.
    """
    manager_matches = employee_manager.search_employee_by_name(manager_name)
    if not manager_matches:
        raise ValueError(f"Manager not found for '{manager_name}'.")

    manager_id = manager_matches[0]
    emp_id = employee_manager.get_next_emp_id()
    if not email:
        sanitized_name = emp_name.strip().lower().replace(" ", ".")
        email = f"{sanitized_name}@atliq.com"

    emp = EmployeeCreate(
        emp_id=emp_id,
        name=emp_name,
        manager_id=manager_id,
        email=email,
    )
    employee_manager.add_employee(emp)

    email_subject = f"Welcome to Atlq, {emp_name}!"
    email_body = (
        f"Hi {emp_name},\n\n"
        f"Welcome to Atlq! Your employee ID is {emp_id} and your manager is {manager_name}.\n"
        f"Your login username is {email}.\n\n"
        "Please reach out if you need anything.\n\n"
        "Best,\nAtlq HR Team"
    )
    try:
        emailer.send_email(email_subject, email_body, [email], html=False)
        email_status = "Welcome email sent."
    except Exception as exc:
        email_status = f"Unable to send email: {exc}"

    ticket_manager.create_ticket(TicketCreate(emp_id=emp_id, item="Laptop", reason="New hire setup"))
    ticket_manager.create_ticket(TicketCreate(emp_id=emp_id, item="ID Card", reason="New hire setup"))

    meeting_dt = (datetime.utcnow() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    meeting_manager.schedule_meeting(MeetingCreate(
        emp_ids=[emp_id],
        start_dt=meeting_dt,
        duration_minutes=60,
        topic=f"Intro with {manager_name}",
    ))

    return (
        f"✅ Employee {emp_name} created (ID {emp_id})\n"
        f"✅ {email_status}\n"
        f"✅ Laptop ticket raised\n"
        f"✅ ID Card ticket raised\n"
        f"✅ Intro meeting scheduled for {meeting_dt.isoformat()}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
