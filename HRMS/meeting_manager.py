from typing import List, Dict
from datetime import datetime, timedelta
from HRMS.schemas import MeetingCreate, MeetingCancelRequest
from HRMS.database import get_connection, initialize_db


class MeetingManager:
    def __init__(self):
        initialize_db()
        self.conn = get_connection()

    def _format_meeting_code(self, sequence: int) -> str:
        return f"M{sequence:03d}"

    def _parse_meeting_code(self, meeting_code: str) -> str:
        meeting_code = meeting_code.strip().upper()
        if not meeting_code.startswith("M"):
            meeting_code = f"M{meeting_code}"
        return meeting_code

    def _get_next_meeting_code(self) -> str:
        rows = self.conn.execute(
            "SELECT meeting_code FROM meetings WHERE meeting_code IS NOT NULL"
        ).fetchall()
        max_number = 0
        for row in rows:
            code = row["meeting_code"]
            if not code:
                continue
            numeric = code.lstrip("M")
            if numeric.isdigit():
                max_number = max(max_number, int(numeric))
        return self._format_meeting_code(max_number + 1)

    def _overlaps(self, start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
        return start_a < end_b and start_b < end_a

    def _validate_overlap(self, emp_id: str, start_dt: datetime, end_dt: datetime) -> None:
        rows = self.conn.execute(
            "SELECT meeting_code, start_dt, duration_minutes FROM meetings WHERE emp_id = ? AND status = 'Scheduled'",
            (emp_id,),
        ).fetchall()
        for row in rows:
            existing_start = datetime.fromisoformat(row["start_dt"])
            existing_end = existing_start + timedelta(minutes=row["duration_minutes"])
            if self._overlaps(start_dt, end_dt, existing_start, existing_end):
                raise ValueError(
                    f"Conflict: {emp_id} already has {row['meeting_code']} from {existing_start.strftime('%Y-%m-%d %H:%M')} to {existing_end.strftime('%H:%M')}.")

    def schedule_meeting(self, req: MeetingCreate) -> str:
        if req.start_dt < datetime.now():
            raise ValueError("Cannot schedule a meeting in the past.")
        if not req.emp_ids:
            raise ValueError("Select at least one employee for the meeting.")
        if req.duration_minutes <= 0:
            raise ValueError("Duration must be a positive number of minutes.")

        meeting_code = self._get_next_meeting_code()
        end_dt = req.start_dt + timedelta(minutes=req.duration_minutes)

        for emp_id in req.emp_ids:
            self._validate_overlap(emp_id, req.start_dt, end_dt)

        self.conn.executemany(
            "INSERT INTO meetings(meeting_code, emp_id, meeting_dt, start_dt, duration_minutes, topic, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    meeting_code,
                    emp_id,
                    req.start_dt.isoformat(),
                    req.start_dt.isoformat(),
                    req.duration_minutes,
                    req.topic,
                    "Scheduled",
                )
                for emp_id in req.emp_ids
            ],
        )
        self.conn.commit()

        attendees = ", ".join(req.emp_ids)
        return (
            f"Meeting {meeting_code} scheduled for {attendees} on {req.start_dt.date().isoformat()} "
            f"from {req.start_dt.strftime('%H:%M')} to {end_dt.strftime('%H:%M')} about '{req.topic}'."
        )

    def get_meetings(self, employee_id: str) -> List[Dict[str, str]]:
        rows = self.conn.execute(
            "SELECT meeting_code, start_dt, duration_minutes, topic, status "
            "FROM meetings WHERE emp_id = ? ORDER BY start_dt",
            (employee_id,),
        ).fetchall()

        meetings = []
        for row in rows:
            start_dt = datetime.fromisoformat(row["start_dt"])
            end_dt = start_dt + timedelta(minutes=row["duration_minutes"])
            meetings.append(
                {
                    "meeting_code": row["meeting_code"],
                    "date": start_dt.date().isoformat(),
                    "start_time": start_dt.strftime("%H:%M"),
                    "end_time": end_dt.strftime("%H:%M"),
                    "topic": row["topic"],
                    "status": row["status"],
                }
            )
        return meetings

    def list_all_meetings(self) -> List[Dict[str, str]]:
        rows = self.conn.execute(
            "SELECT meeting_code, GROUP_CONCAT(emp_id, ', ') AS employee_ids, start_dt, duration_minutes, topic, status "
            "FROM meetings "
            "GROUP BY meeting_code, start_dt, duration_minutes, topic, status "
            "ORDER BY start_dt"
        ).fetchall()

        meetings = []
        for row in rows:
            start_dt = datetime.fromisoformat(row["start_dt"])
            end_dt = start_dt + timedelta(minutes=row["duration_minutes"])
            meetings.append(
                {
                    "meeting_code": row["meeting_code"],
                    "employee_ids": row["employee_ids"],
                    "date": start_dt.date().isoformat(),
                    "start_time": start_dt.strftime("%H:%M"),
                    "end_time": end_dt.strftime("%H:%M"),
                    "duration_minutes": row["duration_minutes"],
                    "topic": row["topic"],
                    "status": row["status"],
                }
            )
        return meetings

    def cancel_meeting(self, req: MeetingCancelRequest) -> str:
        return self.cancel_meeting_by_id(req.meeting_code)

    def cancel_meeting_by_id(self, meeting_code: str) -> str:
        meeting_code = self._parse_meeting_code(meeting_code)
        cursor = self.conn.execute(
            "UPDATE meetings SET status = 'Cancelled' WHERE meeting_code = ? AND status != 'Cancelled'",
            (meeting_code,),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Meeting {meeting_code} not found or already cancelled.")
        self.conn.commit()
        return f"Meeting {meeting_code} canceled successfully."
