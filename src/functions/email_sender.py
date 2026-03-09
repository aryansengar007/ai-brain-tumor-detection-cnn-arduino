"""
Email Report Sending Module
Securely sends PDF reports via SMTP.
Credentials must be provided via environment variables.
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from typing import Tuple


class EmailReportSender:
    """Handles secure email transmission of medical reports."""

    def __init__(
        self,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        sender_email: str = None,
        sender_password: str = None,
    ):
        """
        Initialize email sender with credentials from environment variables.

        Environment variables required:
        - EMAIL_ADDRESS: Sender email address
        - EMAIL_PASSWORD: Sender email password or app password

        For Gmail: Use App Password (not regular password)
        See: https://support.google.com/accounts/answer/185833
        """

        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

        # Get credentials from environment variables
        self.sender_email = sender_email or os.getenv("EMAIL_ADDRESS", "")
        self.sender_password = sender_password or os.getenv("EMAIL_PASSWORD", "")

        # Check if credentials are configured
        self.is_configured = bool(self.sender_email and self.sender_password)

    def validate_configuration(self) -> Tuple[bool, str]:
        """Validate that email credentials are configured."""
        if not self.is_configured:
            return (
                False,
                "Email credentials not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.",
            )
        if not self.sender_email:
            return (
                False,
                "Sender email missing. Set EMAIL_ADDRESS environment variable.",
            )
        if not self.sender_password:
            return (
                False,
                "Sender password missing. Set EMAIL_PASSWORD environment variable.",
            )
        if "@" not in self.sender_email:
            return False, "Invalid sender email format."
        return True, "Email configuration valid"

    def send_report(
        self,
        recipient_email: str,
        patient_name: str,
        pdf_bytes: bytes,
        filename: str = "Brain_Tumor_Report.pdf",
    ) -> Tuple[bool, str]:
        """
        Send medical report via email.

        Parameters:
        -----------
        recipient_email : str
            Recipient email address
        patient_name : str
            Patient identifier/name
        pdf_bytes : bytes
            PDF file content as bytes
        filename : str
            PDF filename

        Returns:
        --------
        Tuple[bool, str] : (success, message)
        """

        # Validate configuration first
        is_valid, config_msg = self.validate_configuration()
        if not is_valid:
            return False, config_msg

        if not recipient_email or "@" not in recipient_email:
            return False, "Invalid recipient email address"

        if not pdf_bytes or len(pdf_bytes) == 0:
            return False, "PDF content is empty"

        try:

            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            msg["Date"] = formatdate(localtime=True)
            msg["Subject"] = f"Brain Tumor Classification Report - {patient_name}"

            body = f"""
Dear {patient_name},

Your Brain Tumor Classification analysis has been completed.

Please find the detailed report attached to this email.

This report includes:
- Classification result (Healthy/Tumor)
- Confidence score
- Risk level assessment
- Detailed analysis and visualizations

IMPORTANT: This report is for informational purposes only and should be reviewed by a qualified medical professional.

Best regards,
Brain Tumor Classification System
"""

            msg.attach(MIMEText(body, "plain"))

            attachment = MIMEBase("application", "octet-stream")
            attachment.set_payload(pdf_bytes)
            encoders.encode_base64(attachment)

            attachment.add_header(
                "Content-Disposition", "attachment", filename=filename
            )

            msg.attach(attachment)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            return True, f"Report sent successfully to {recipient_email}"

        except smtplib.SMTPAuthenticationError:
            return (
                False,
                "Email authentication failed. Check EMAIL_ADDRESS and EMAIL_PASSWORD.",
            )
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"


def send_email_report(
    recipient_email: str,
    pdf_bytes: bytes,
    patient_name: str = "Patient",
) -> Tuple[bool, str]:

    sender = EmailReportSender()
    return sender.send_report(recipient_email, patient_name, pdf_bytes)
