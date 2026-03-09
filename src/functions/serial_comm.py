"""
Arduino Serial Communication Module
Handles safe serial communication with Arduino board.
Supports robot control signals with automatic error handling.
"""

import serial
import time
from typing import Tuple, Optional


class ArduinoCommunicator:
    """
    Manages serial communication with Arduino.
    Safely handles connection failures without crashing the application.
    """

    def __init__(self, port: str = "COM3", baudrate: int = 9600, timeout: float = 2.0):
        """
        Initialize Arduino communicator.

        Parameters:
        -----------
        port : str
            Serial port (default: COM3 for Windows, /dev/ttyUSB0 for Linux)
        baudrate : int
            Communication speed (default: 9600)
        timeout : float
            Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
        self.is_connected = False

    def connect(self) -> Tuple[bool, str]:
        """
        Attempt to connect to Arduino.

        Returns:
        --------
        Tuple[bool, str] : (success, message)
        """
        try:
            self.connection = serial.Serial(
                port=self.port, baudrate=self.baudrate, timeout=self.timeout
            )
            time.sleep(2)  # Wait for Arduino to initialize
            self.is_connected = True
            return True, f"✅ Connected to Arduino on {self.port}"
        except serial.SerialException as e:
            self.is_connected = False
            return False, f"❌ Cannot connect to Arduino: {str(e)}"
        except Exception as e:
            self.is_connected = False
            return False, f"❌ Connection error: {str(e)}"

    def send_signal(self, signal: str) -> Tuple[bool, str]:
        """
        Send control signal to Arduino.

        Parameters:
        -----------
        signal : str
            Single character signal: 'R' (Red/High), 'Y' (Yellow/Moderate),
                                     'G' (Green/Healthy), 'B' (Blue/Low Confidence)

        Returns:
        --------
        Tuple[bool, str] : (success, message)
        """
        if not self.is_connected:
            return False, "❌ Arduino not connected. Please check connection."

        if signal not in ["R", "Y", "G", "B"]:
            return False, f"❌ Invalid signal: {signal}. Use R, Y, G, or B."

        try:
            if self.connection and self.connection.is_open:
                self.connection.write(signal.encode())
                time.sleep(0.5)  # Brief delay for Arduino to process
                return True, f"✅ Signal '{signal}' sent successfully"
            else:
                self.is_connected = False
                return False, "❌ Serial connection lost."
        except serial.SerialException as e:
            self.is_connected = False
            return False, f"❌ Send failed: {str(e)}"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"

    def disconnect(self) -> bool:
        """Close serial connection."""
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
            self.is_connected = False
            return True
        except Exception:
            return False

    def get_available_ports(self) -> list:
        """
        Get list of available serial ports.

        Returns:
        --------
        list : Available COM ports
        """
        try:
            import platform

            if platform.system() == "Windows":
                import serial.tools.list_ports

                ports = [port.device for port in serial.tools.list_ports.comports()]
            else:
                import glob

                ports = glob.glob("/dev/tty*")
            return ports if ports else []
        except Exception:
            return []


# Global communicator instance
_arduino = None


def get_arduino_instance(port: str = "COM3") -> ArduinoCommunicator:
    """Get or create Arduino communicator instance."""
    global _arduino
    if _arduino is None:
        _arduino = ArduinoCommunicator(port=port)
    return _arduino


def safe_send_to_arduino(signal: str, port: str = "COM3") -> Tuple[bool, str]:
    """
    Safely send signal to Arduino with automatic connection handling.

    Parameters:
    -----------
    signal : str
        Control signal (R, Y, G, B)
    port : str
        Serial port

    Returns:
    --------
    Tuple[bool, str] : (success, message)
    """
    try:
        arduino = get_arduino_instance(port)

        # Try to connect if not already connected
        if not arduino.is_connected:
            success, msg = arduino.connect()
            if not success:
                return False, msg

        # Send the signal
        return arduino.send_signal(signal)

    except Exception as e:
        return False, f"❌ Unexpected error: {str(e)}"
