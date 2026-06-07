import smtplib
import ssl
from email.message import EmailMessage
from typing import List, Optional
import mimetypes
import os
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(script_dir, ".env"))

class EmailSender:
    def __init__(
        self,
        smtp_server: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
    ):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def _validate_credentials(self) -> None:
        if not self.username or not self.password:
            raise ValueError(
                "Missing email credentials. Set CB_EMAIL and CB_EMAIL_PWD in .env or environment variables. "
                "For Gmail, use an app password and enable 2FA; normal account passwords will not work."
            )

    def send_email(
        self,
        subject: str,
        body: str,
        to_emails: List[str] | str,
        from_email: Optional[str] = None,
        html: bool = False,
        attachments: Optional[List[str]] = None,
    ) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email or self.username
        msg["To"] = ", ".join(to_emails) if isinstance(to_emails, list) else to_emails
        msg.set_content(body, subtype="html" if html else "plain")

        if attachments:
            for file_path in attachments:
                if not os.path.isfile(file_path):
                    raise FileNotFoundError(f"Attachment not found: {file_path}")

                mime_type, _ = mimetypes.guess_type(file_path)
                mime_type = mime_type or "application/octet-stream"
                maintype, subtype = mime_type.split("/", 1)

                with open(file_path, "rb") as f:
                    file_data = f.read()
                    filename = os.path.basename(file_path)
                    msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=filename)

        self._validate_credentials()
        context = ssl.create_default_context()

        try:
            if self.use_tls:
                with smtplib.SMTP(self.smtp_server, self.port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg)
        except smtplib.SMTPAuthenticationError as auth_err:
            raise RuntimeError(
                "SMTP authentication failed. Check CB_EMAIL and CB_EMAIL_PWD, and use an app password if you are sending through Gmail."
            ) from auth_err
        except smtplib.SMTPException as smtp_err:
            raise RuntimeError(
                f"Failed to send email via {self.smtp_server}:{self.port} - {smtp_err}"
            ) from smtp_err

if __name__ == "__main__":
    email_sender = EmailSender(
        smtp_server="smtp.gmail.com",
        port=587,
        username=os.getenv("CB_EMAIL"),
        password=os.getenv("CB_EMAIL_PWD"),
        use_tls=True,
    )
    email_sender.send_email(
        subject="Test Email",
        body="This is a test email.",
        to_emails="charishmavanukuri3012@gmail.com",
    )
    #in .env file, we have added the email and password for the email account that we will be using to send emails. The password is an app password generated from the email account settings, which is more secure than using the actual account password.
    # here we are specifying the receiver's email address, the subject and body of the email, and then calling the send_email method to send the email.
