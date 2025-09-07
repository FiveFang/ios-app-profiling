"""
Battery Monitor for iOS devices.
Monitors battery level, charging status, and power consumption.
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
import psutil
from pymobiledevice3.services.lockdown import LockdownClient
from pymobiledevice3.services.mobile_gestalt import MobileGestaltService


logger = logging.getLogger(__name__)


class BatteryReading:
    """Represents a single battery reading."""
    
    def __init__(self, timestamp: datetime, level: int, is_charging: bool, 
                 voltage: Optional[float] = None, temperature: Optional[float] = None):
        self.timestamp = timestamp
        self.level = level
        self.is_charging = is_charging
        self.voltage = voltage
        self.temperature = temperature
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'is_charging': self.is_charging,
            'voltage': self.voltage,
            'temperature': self.temperature
        }


class BatteryMonitor:
    """Monitors battery status and consumption for iOS devices."""
    
    def __init__(self, udid: str, lockdown_client: LockdownClient):
        self.udid = udid
        self.lockdown = lockdown_client
        self.readings: List[BatteryReading] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable[[BatteryReading], None]] = []
        self.monitor_interval = 10  # seconds
        
    def add_callback(self, callback: Callable[[BatteryReading], None]) -> None:
        """Add a callback function to be called on each battery reading."""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[BatteryReading], None]) -> None:
        """Remove a callback function."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_current_battery_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current battery information.
        
        Returns:
            Dictionary with battery information or None if unavailable
        """
        try:
            # Get battery information from the device
            battery_info = self.lockdown.get_value('com.apple.mobile.battery')
            
            if not battery_info:
                logger.warning(f"No battery info available for device {self.udid}")
                return None
            
            return {
                'level': battery_info.get('BatteryCurrentCapacity', 0),
                'is_charging': battery_info.get('ExternalConnected', False),
                'fully_charged': battery_info.get('FullyCharged', False),
                'gas_gauge_capability': battery_info.get('GasGaugeCapability', False),
                'has_battery': battery_info.get('HasBattery', True),
                'voltage': battery_info.get('Voltage'),
                'amperage': battery_info.get('Amperage'),
                'temperature': battery_info.get('Temperature'),
                'cycle_count': battery_info.get('CycleCount'),
                'design_capacity': battery_info.get('DesignCapacity'),
                'max_capacity': battery_info.get('MaxCapacity'),
            }
            
        except Exception as e:
            logger.error(f"Failed to get battery info for {self.udid}: {e}")
            return None
    
    def start_monitoring(self, interval: int = 10) -> bool:
        """
        Start continuous battery monitoring.
        
        Args:
            interval: Monitoring interval in seconds
            
        Returns:
            True if monitoring started successfully
        """
        if self.monitoring:
            logger.warning(f"Already monitoring device {self.udid}")
            return False
        
        # Test if we can get battery info before starting
        if self.get_current_battery_info() is None:
            logger.error(f"Cannot get battery info for device {self.udid}")
            return False
        
        self.monitor_interval = interval
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"Started battery monitoring for device {self.udid} (interval: {interval}s)")
        return True
    
    def stop_monitoring(self) -> None:
        """Stop battery monitoring."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info(f"Stopped battery monitoring for device {self.udid}")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring:
            try:
                battery_info = self.get_current_battery_info()
                if battery_info:
                    reading = BatteryReading(
                        timestamp=datetime.now(),
                        level=battery_info['level'],
                        is_charging=battery_info['is_charging'],
                        voltage=battery_info.get('voltage'),
                        temperature=battery_info.get('temperature')
                    )
                    
                    self.readings.append(reading)
                    
                    # Call callbacks
                    for callback in self.callbacks:
                        try:
                            callback(reading)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
                
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in battery monitoring loop: {e}")
                time.sleep(self.monitor_interval)
    
    def get_readings(self, since: Optional[datetime] = None) -> List[BatteryReading]:
        """
        Get battery readings.
        
        Args:
            since: Only return readings since this timestamp
            
        Returns:
            List of battery readings
        """
        if since is None:
            return self.readings.copy()
        
        return [r for r in self.readings if r.timestamp >= since]
    
    def get_battery_drain_rate(self, duration_minutes: int = 60) -> Optional[float]:
        """
        Calculate battery drain rate over a specified duration.
        
        Args:
            duration_minutes: Duration to calculate drain rate over
            
        Returns:
            Battery drain rate as percentage per hour, or None if insufficient data
        """
        if len(self.readings) < 2:
            return None
        
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        recent_readings = [r for r in self.readings if r.timestamp >= cutoff_time and not r.is_charging]
        
        if len(recent_readings) < 2:
            return None
        
        # Get first and last readings
        first_reading = recent_readings[0]
        last_reading = recent_readings[-1]
        
        # Calculate drain rate
        time_diff_hours = (last_reading.timestamp - first_reading.timestamp).total_seconds() / 3600
        battery_diff = first_reading.level - last_reading.level
        
        if time_diff_hours == 0:
            return None
        
        return battery_diff / time_diff_hours
    
    def get_charging_sessions(self) -> List[Dict[str, Any]]:
        """
        Get charging sessions from the readings.
        
        Returns:
            List of charging session dictionaries
        """
        sessions = []
        current_session = None
        
        for reading in self.readings:
            if reading.is_charging:
                if current_session is None:
                    # Start new charging session
                    current_session = {
                        'start_time': reading.timestamp,
                        'start_level': reading.level,
                        'end_time': reading.timestamp,
                        'end_level': reading.level,
                        'readings': [reading]
                    }
                else:
                    # Update current session
                    current_session['end_time'] = reading.timestamp
                    current_session['end_level'] = reading.level
                    current_session['readings'].append(reading)
            else:
                if current_session is not None:
                    # End current session
                    duration = (current_session['end_time'] - current_session['start_time']).total_seconds()
                    current_session['duration_seconds'] = duration
                    current_session['charge_gained'] = current_session['end_level'] - current_session['start_level']
                    sessions.append(current_session)
                    current_session = None
        
        # Add final session if still charging
        if current_session is not None:
            duration = (current_session['end_time'] - current_session['start_time']).total_seconds()
            current_session['duration_seconds'] = duration
            current_session['charge_gained'] = current_session['end_level'] - current_session['start_level']
            sessions.append(current_session)
        
        return sessions
    
    def export_data(self, format: str = 'json') -> Dict[str, Any]:
        """
        Export battery monitoring data.
        
        Args:
            format: Export format ('json', 'csv')
            
        Returns:
            Exported data dictionary
        """
        data = {
            'device_udid': self.udid,
            'monitoring_started': self.readings[0].timestamp.isoformat() if self.readings else None,
            'monitoring_ended': self.readings[-1].timestamp.isoformat() if self.readings else None,
            'total_readings': len(self.readings),
            'readings': [reading.to_dict() for reading in self.readings],
            'charging_sessions': self.get_charging_sessions(),
            'current_drain_rate': self.get_battery_drain_rate(60) if not self.readings[-1].is_charging else None
        }
        
        return data
    
    def clear_data(self) -> None:
        """Clear all battery readings."""
        self.readings.clear()
        logger.info(f"Cleared battery data for device {self.udid}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get battery monitoring statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.readings:
            return {'total_readings': 0}
        
        levels = [r.level for r in self.readings]
        charging_readings = [r for r in self.readings if r.is_charging]
        draining_readings = [r for r in self.readings if not r.is_charging]
        
        stats = {
            'total_readings': len(self.readings),
            'monitoring_duration_hours': (self.readings[-1].timestamp - self.readings[0].timestamp).total_seconds() / 3600,
            'min_battery_level': min(levels),
            'max_battery_level': max(levels),
            'average_battery_level': sum(levels) / len(levels),
            'charging_time_percentage': len(charging_readings) / len(self.readings) * 100,
            'draining_time_percentage': len(draining_readings) / len(self.readings) * 100,
            'total_charging_sessions': len(self.get_charging_sessions()),
            'current_drain_rate_per_hour': self.get_battery_drain_rate(60)
        }
        
        return stats
