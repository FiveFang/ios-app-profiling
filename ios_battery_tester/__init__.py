"""
iOS Battery Drain Testing Utility

A comprehensive tool for testing battery consumption of iOS applications
on real devices with both CLI and web interfaces.
"""

__version__ = "1.0.0"
__author__ = "iOS Battery Tester"
__email__ = "test@example.com"

from .core.device_manager import DeviceManager
from .core.battery_monitor import BatteryMonitor
from .core.test_runner import TestRunner

__all__ = ["DeviceManager", "BatteryMonitor", "TestRunner"]
