"""
QR Code Generator Module
Generates QR codes for mobile-friendly image upload system.
"""

import qrcode
import io
from typing import Tuple
import socket


def get_local_ip() -> str:
    """
    Get local IP address of the machine.

    Returns:
    --------
    str : Local IP address or 'localhost'
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def generate_qr_code(url: str, box_size: int = 10, border: int = 4) -> io.BytesIO:
    """
    Generate QR code image for given URL.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )

        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return img_bytes

    except Exception as e:
        raise Exception(f"Failed to generate QR code: {str(e)}")


def generate_mobile_upload_qr(port: int = 8501) -> Tuple[io.BytesIO, str]:
    """
    Generate QR code for mobile Streamlit upload page.
    """
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{port}"

    qr_image = generate_qr_code(url)

    return qr_image, url


def generate_qr_from_text(text: str) -> io.BytesIO:
    """
    Generate QR code from arbitrary text.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return img_bytes

    except Exception as e:
        raise Exception(f"QR generation failed: {str(e)}")
