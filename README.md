# HRMS AI Assistant

An AI-powered Human Resource Management System (HRMS) built using Streamlit, Python, MCP (Model Context Protocol), and SQLite. The application combines traditional HR management workflows with conversational AI, allowing users to perform HR operations through both a graphical interface and natural language interactions.

---

## Features

### AI HR Assistant

* Chat-based interface powered by LLMs and MCP tools.
* Supports natural language HR requests.
* Automatically invokes the appropriate HR tool based on user intent.
* Handles multi-step workflows through tool orchestration.

### Employee Management

* View all employees.
* Add new employees.
* Update employee details.
* Fetch employee information.
* Validate unique employee email addresses.

### Leave Management

* View leave balances.
* Apply for leaves using a calendar-based date selector.
* Prevent duplicate leave applications.
* Prevent leave applications for past dates.
* View employee leave history.

### Ticket Management

* Create HR or IT support tickets.
* Track ticket status.
* Update ticket status.
* Filter tickets by employee and status.

### Meeting Management

* Schedule meetings for multiple employees.
* Configure meeting duration and topic.
* Prevent scheduling meetings in the past.
* Cancel scheduled meetings.
* Track meeting status.

### Employee Onboarding Workflow

A dedicated MCP tool automates employee onboarding by:

1. Creating a new employee record.
2. Initializing leave balances.
3. Creating hardware request tickets.
4. Scheduling onboarding meetings.

This enables multiple HR actions to be completed through a single request.

---

## Architecture

### UI Layer

* Streamlit
* Sidebar navigation
* Chat interface
* Data management screens

### AI Layer

* Groq LLM
* MCP (Model Context Protocol)
* Tool orchestration
* Intent routing

### Business Layer

* EmployeeManager
* LeaveManager
* TicketManager
* MeetingManager

### Data Layer

* SQLite Database
* Employee Records
* Leave History
* Tickets
* Meetings

---

## Tech Stack

| Category               | Technologies                 |
| ---------------------- | ---------------------------- |
| Frontend               | Streamlit                    |
| Backend                | Python                       |
| AI/LLM                 | Groq                         |
| Agent Framework        | MCP (Model Context Protocol) |
| Database               | SQLite                       |
| Validation             | Pydantic                     |
| Environment Management | python-dotenv                |

---

## Project Structure

```text
HRMS-Assist/
│
├── app.py
├── server.py
├── emails.py
│
├── HRMS/
│   ├── employee_manager.py
│   ├── leave_manager.py
│   ├── ticket_manager.py
│   ├── meeting_manager.py
│   ├── database.py
│   └── schemas.py
│
├── hrms.db
├── .env
├── requirements.txt
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd HRMS-Assist
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows

```bash
venv\Scripts\activate
```

Mac/Linux

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

---

## Run Application

```bash
streamlit run app.py
```

---

## Sample Queries

### Employee Operations

```text
Add a new employee named John Doe with manager E001 and email john@company.com
```

```text
Get details of employee E005
```

```text
Update email of employee E010 to employee10@company.com
```

### Leave Operations

```text
Apply leave for employee E003 from June 20 to June 22
```

```text
Show leave balance for employee E003
```

### Ticket Operations

```text
Create a hardware request ticket for employee E004
```

```text
Update ticket T0003 status to Closed
```

### Meeting Operations

```text
Schedule an onboarding meeting for employee E007 tomorrow at 10 AM
```

---

## Key Highlights

* Conversational AI integrated with enterprise workflows.
* MCP-based tool orchestration.
* Multi-step employee onboarding automation.
* Real-time data management through Streamlit.
* SQLite-backed persistence layer.
* Modular architecture with separate managers for each HR domain.

---

## Future Enhancements

* Role-Based Access Control (RBAC)
* Email Notifications
* Department Management
* Payroll Integration
* Employee Performance Tracking
* Cloud Database Support
* Multi-user Authentication

---

## Author

**Charishma Vanukuri**

AI-Powered HRMS Assistant built as a hands-on project to explore MCP, LLM Tool Calling, Workflow Automation, and Full-Stack Application Development.
