"""
Custom exceptions for iOS Battery Tester.
"""


class BatteryTesterError(Exception):
    """Base exception for battery tester."""
    pass


class DeviceError(BatteryTesterError):
    """Device-related errors."""
    pass


class BatteryMonitorError(BatteryTesterError):
    """Battery monitoring errors."""
    pass


class TestExecutionError(BatteryTesterError):
    """Test execution errors."""
    pass


class ConfigurationError(BatteryTesterError):
    """Configuration-related errors."""
    pass
