"""
Test Runner for iOS battery drain testing.
Manages test scenarios, execution, and data collection.
"""

import logging
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid

from .device_manager import DeviceManager
from .battery_monitor import BatteryMonitor, BatteryReading
from .exceptions import DeviceError, BatteryMonitorError, TestExecutionError


logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TestScenario:
    """Represents a battery drain test scenario."""
    
    def __init__(self, name: str, description: str, duration_minutes: int, 
                 app_bundle_id: Optional[str] = None, actions: Optional[List[Dict]] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.duration_minutes = duration_minutes
        self.app_bundle_id = app_bundle_id
        self.actions = actions or []
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'app_bundle_id': self.app_bundle_id,
            'actions': self.actions,
            'created_at': self.created_at.isoformat()
        }


class TestResult:
    """Represents the result of a battery drain test."""
    
    def __init__(self, scenario: TestScenario, device_udid: str):
        self.id = str(uuid.uuid4())
        self.scenario = scenario
        self.device_udid = device_udid
        self.status = TestStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.battery_readings: List[BatteryReading] = []
        self.initial_battery_level: Optional[int] = None
        self.final_battery_level: Optional[int] = None
        self.total_drain: Optional[int] = None
        self.drain_rate_per_hour: Optional[float] = None
        self.error_message: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'scenario': self.scenario.to_dict(),
            'device_udid': self.device_udid,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'initial_battery_level': self.initial_battery_level,
            'final_battery_level': self.final_battery_level,
            'total_drain': self.total_drain,
            'drain_rate_per_hour': self.drain_rate_per_hour,
            'battery_readings': [reading.to_dict() for reading in self.battery_readings],
            'error_message': self.error_message,
            'metadata': self.metadata
        }


class TestRunner:
    """Manages and executes battery drain tests."""
    
    def __init__(self, device_manager: DeviceManager):
        self.device_manager = device_manager
        self.active_tests: Dict[str, TestResult] = {}
        self.completed_tests: List[TestResult] = []
        self.scenarios: Dict[str, TestScenario] = {}
        self.callbacks: List[Callable[[TestResult], None]] = []
        self._load_default_scenarios()
    
    def add_callback(self, callback: Callable[[TestResult], None]) -> None:
        """Add a callback function to be called on test events."""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[TestResult], None]) -> None:
        """Remove a callback function."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, test_result: TestResult) -> None:
        """Notify all callbacks of test result update."""
        for callback in self.callbacks:
            try:
                callback(test_result)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def _load_default_scenarios(self) -> None:
        """Load default test scenarios."""
        default_scenarios = [
            TestScenario(
                name="Idle Test",
                description="Test battery drain when device is idle with screen off",
                duration_minutes=60,
                actions=[
                    {"type": "screen_off", "delay": 0},
                    {"type": "wait", "duration": 3600}
                ]
            ),
            TestScenario(
                name="Screen On Test",
                description="Test battery drain with screen on at maximum brightness",
                duration_minutes=30,
                actions=[
                    {"type": "screen_on", "delay": 0},
                    {"type": "set_brightness", "level": 100},
                    {"type": "wait", "duration": 1800}
                ]
            ),
            TestScenario(
                name="App Usage Test",
                description="Test battery drain while using a specific application",
                duration_minutes=45,
                app_bundle_id="com.apple.mobilesafari",
                actions=[
                    {"type": "launch_app", "delay": 0},
                    {"type": "interact", "pattern": "browse", "duration": 2700}
                ]
            ),
            TestScenario(
                name="Video Playback Test",
                description="Test battery drain during video playback",
                duration_minutes=120,
                app_bundle_id="com.apple.tv",
                actions=[
                    {"type": "launch_app", "delay": 0},
                    {"type": "play_video", "duration": 7200},
                ]
            ),
            TestScenario(
                name="Gaming Test",
                description="Test battery drain during intensive gaming",
                duration_minutes=90,
                actions=[
                    {"type": "launch_app", "delay": 0},
                    {"type": "simulate_gaming", "intensity": "high", "duration": 5400}
                ]
            )
        ]
        
        for scenario in default_scenarios:
            self.scenarios[scenario.id] = scenario
        
        logger.info(f"Loaded {len(default_scenarios)} default test scenarios")
    
    def add_scenario(self, scenario: TestScenario) -> str:
        """
        Add a custom test scenario.
        
        Args:
            scenario: Test scenario to add
            
        Returns:
            Scenario ID
        """
        self.scenarios[scenario.id] = scenario
        logger.info(f"Added test scenario: {scenario.name}")
        return scenario.id
    
    def get_scenarios(self) -> List[TestScenario]:
        """Get all available test scenarios."""
        return list(self.scenarios.values())
    
    def get_scenario(self, scenario_id: str) -> Optional[TestScenario]:
        """Get a specific test scenario by ID."""
        return self.scenarios.get(scenario_id)
    
    def start_test(self, scenario_id: str, device_udid: str) -> Optional[str]:
        """
        Start a battery drain test.
        
        Args:
            scenario_id: ID of the test scenario
            device_udid: Target device UDID
            
        Returns:
            Test result ID if started successfully, None otherwise
        """
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            logger.error(f"Scenario {scenario_id} not found")
            return None
        
        if not self.device_manager.is_device_connected(device_udid):
            logger.error(f"Device {device_udid} not connected")
            return None
        
        # Check if device is already being tested
        for test_id, test_result in self.active_tests.items():
            if test_result.device_udid == device_udid:
                logger.error(f"Device {device_udid} is already running test {test_id}")
                return None
        
        # Create test result
        test_result = TestResult(scenario, device_udid)
        test_result.status = TestStatus.RUNNING
        test_result.started_at = datetime.now()
        
        self.active_tests[test_result.id] = test_result
        
        # Start test in background thread
        test_thread = threading.Thread(
            target=self._execute_test,
            args=(test_result,),
            daemon=True
        )
        test_thread.start()
        
        logger.info(f"Started test {test_result.id} for scenario '{scenario.name}' on device {device_udid}")
        return test_result.id
    
    def stop_test(self, test_id: str) -> bool:
        """
        Stop a running test.
        
        Args:
            test_id: Test result ID
            
        Returns:
            True if stopped successfully
        """
        test_result = self.active_tests.get(test_id)
        if not test_result:
            logger.error(f"Test {test_id} not found")
            return False
        
        if test_result.status != TestStatus.RUNNING:
            logger.warning(f"Test {test_id} is not running")
            return False
        
        test_result.status = TestStatus.CANCELLED
        test_result.completed_at = datetime.now()
        
        # Move to completed tests
        self.completed_tests.append(test_result)
        del self.active_tests[test_id]
        
        logger.info(f"Cancelled test {test_id}")
        self._notify_callbacks(test_result)
        return True
    
    def get_test_result(self, test_id: str) -> Optional[TestResult]:
        """Get a test result by ID."""
        # Check active tests first
        if test_id in self.active_tests:
            return self.active_tests[test_id]
        
        # Check completed tests
        for test_result in self.completed_tests:
            if test_result.id == test_id:
                return test_result
        
        return None
    
    def get_active_tests(self) -> List[TestResult]:
        """Get all currently running tests."""
        return list(self.active_tests.values())
    
    def get_completed_tests(self) -> List[TestResult]:
        """Get all completed tests."""
        return self.completed_tests.copy()
    
    def _execute_test(self, test_result: TestResult) -> None:
        """Execute a battery drain test."""
        scenario = test_result.scenario
        device_udid = test_result.device_udid
        
        try:
            # Get device lockdown client
            lockdown = self.device_manager.lockdown_clients.get(device_udid)
            if not lockdown:
                raise DeviceError(f"Cannot get lockdown client for device {device_udid}")
            
            # Initialize battery monitor
            battery_monitor = BatteryMonitor(device_udid, lockdown)
            
            # Setup and start monitoring
            self._setup_battery_monitoring(battery_monitor, test_result)
            
            # Execute test actions
            self._execute_actions(scenario.actions, device_udid, test_result)
            
            # Wait for test duration
            duration_seconds = scenario.duration_minutes * 60
            start_time = time.time()
            
            while (time.time() - start_time) < duration_seconds:
                if test_result.status == TestStatus.CANCELLED:
                    break
                time.sleep(10)  # Check every 10 seconds
            
            # Stop battery monitoring
            battery_monitor.stop_monitoring()
            
            # Get final battery level
            final_info = battery_monitor.get_current_battery_info()
            if final_info:
                test_result.final_battery_level = final_info['level']
                test_result.metadata['final_battery_info'] = final_info
                
                # Calculate drain metrics
                if test_result.initial_battery_level and test_result.final_battery_level:
                    test_result.total_drain = test_result.initial_battery_level - test_result.final_battery_level
                    
                    actual_duration_hours = (time.time() - start_time) / 3600
                    if actual_duration_hours > 0:
                        test_result.drain_rate_per_hour = test_result.total_drain / actual_duration_hours
            
            # Mark test as completed
            if test_result.status == TestStatus.RUNNING:
                test_result.status = TestStatus.COMPLETED
            
            test_result.completed_at = datetime.now()
            
            # Get battery statistics
            test_result.metadata['battery_stats'] = battery_monitor.get_statistics()
            test_result.metadata['charging_sessions'] = battery_monitor.get_charging_sessions()
            
        except Exception as e:
            logger.error(f"Test {test_result.id} failed: {e}")
            test_result.status = TestStatus.FAILED
            test_result.error_message = str(e)
            test_result.completed_at = datetime.now()
        
        finally:
            # Move test to completed
            if test_result.id in self.active_tests:
                del self.active_tests[test_result.id]
            self.completed_tests.append(test_result)
            
            # Notify callbacks
            self._notify_callbacks(test_result)
            
            logger.info(f"Test {test_result.id} completed with status: {test_result.status.value}")
    
    def _setup_battery_monitoring(self, battery_monitor: BatteryMonitor, test_result: TestResult) -> None:
        """Setup battery monitoring for a test."""
        # Get initial battery level
        initial_info = battery_monitor.get_current_battery_info()
        if not initial_info:
            raise BatteryMonitorError("Cannot get initial battery information")
        
        test_result.initial_battery_level = initial_info['level']
        test_result.metadata['initial_battery_info'] = initial_info
        
        # Start battery monitoring
        if not battery_monitor.start_monitoring(interval=30):  # 30-second intervals
            raise BatteryMonitorError("Failed to start battery monitoring")
        
        # Store readings callback
        def store_reading(reading: BatteryReading) -> None:
            test_result.battery_readings.append(reading)
        
        battery_monitor.add_callback(store_reading)
    
    def _execute_actions(self, actions: List[Dict], device_udid: str, test_result: TestResult) -> None:
        """Execute test actions on the device."""
        for action in actions:
            if test_result.status == TestStatus.CANCELLED:
                break
                
            self._execute_single_action(action, device_udid, test_result)
    
    def _execute_single_action(self, action: Dict, device_udid: str, test_result: TestResult) -> None:
        """Execute a single action on the device."""
        action_type = action.get('type')
        delay = action.get('delay', 0)
        
        if delay > 0:
            time.sleep(delay)
        
        try:
            if action_type == 'launch_app':
                self._handle_app_action(action, device_udid, test_result, launch=True)
            elif action_type == 'kill_app':
                self._handle_app_action(action, device_udid, test_result, launch=False)
            elif action_type == 'wait':
                duration = action.get('duration', 60)
                time.sleep(duration)
            elif action_type in ['screen_on', 'screen_off', 'set_brightness', 
                               'interact', 'play_video', 'simulate_gaming']:
                logger.warning(f"Action '{action_type}' not implemented yet")
        except Exception as e:
            logger.error(f"Failed to execute action {action_type}: {e}")
    
    def _handle_app_action(self, action: Dict, device_udid: str, test_result: TestResult, launch: bool) -> None:
        """Handle app launch/kill actions."""
        bundle_id = action.get('bundle_id') or test_result.scenario.app_bundle_id
        if bundle_id:
            if launch:
                self.device_manager.launch_app(device_udid, bundle_id)
            else:
                self.device_manager.kill_app(device_udid, bundle_id)
    
    def export_test_results(self, test_ids: Optional[List[str]] = None, 
                          format: str = 'json') -> Dict[str, Any]:
        """
        Export test results.
        
        Args:
            test_ids: Specific test IDs to export, or None for all
            format: Export format
            
        Returns:
            Exported data
        """
        if test_ids:
            results = []
            for test_id in test_ids:
                result = self.get_test_result(test_id)
                if result:
                    results.append(result.to_dict())
        else:
            # Export all tests
            results = []
            results.extend([test.to_dict() for test in self.active_tests.values()])
            results.extend([test.to_dict() for test in self.completed_tests])
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_tests': len(results),
            'format': format,
            'test_results': results
        }
        
        return export_data
    
    def clear_completed_tests(self) -> None:
        """Clear all completed test results."""
        count = len(self.completed_tests)
        self.completed_tests.clear()
        logger.info(f"Cleared {count} completed test results")
