"""
Functions package for Brain Tumor Classification System
Contains helper modules for risk classification, Arduino communication, QR codes, and email reporting.
"""

from .risk_classification import calculate_risk_level, get_signal_description
from .serial_comm import ArduinoCommunicator, safe_send_to_arduino, get_arduino_instance
from .qr_generator import generate_mobile_upload_qr, generate_qr_from_text, get_local_ip
from .email_sender import EmailReportSender, send_email_report

__all__ = [
    "calculate_risk_level",
    "get_signal_description",
    "ArduinoCommunicator",
    "safe_send_to_arduino",
    "get_arduino_instance",
    "generate_mobile_upload_qr",
    "generate_qr_from_text",
    "get_local_ip",
    "EmailReportSender",
    "send_email_report",
]
