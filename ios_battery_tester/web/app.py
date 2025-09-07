"""
Flask web application for iOS Battery Drain Testing.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

from ..core.device_manager import DeviceManager
from ..core.test_runner import TestRunner, TestResult
from ..core.battery_monitor import BatteryReading


logger = logging.getLogger(__name__)


def create_app(config: Dict[str, Any] = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # Configuration
    app.config['SECRET_KEY'] = config.get('secret_key', 'dev-secret-key') if config else 'dev-secret-key'
    app.config['DEBUG'] = config.get('debug', True) if config else True
    
    # Enable CORS
    CORS(app)
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize managers
    device_manager = DeviceManager()
    test_runner = TestRunner(device_manager)
    
    # Store in app context
    app.device_manager = device_manager
    app.test_runner = test_runner
    app.socketio = socketio
    
    # Setup routes and handlers
    _setup_routes(app, device_manager, test_runner)
    _setup_socketio_handlers(socketio, device_manager, test_runner)
    
    return app


def _setup_routes(app: Flask, device_manager: DeviceManager, test_runner: TestRunner) -> None:
    """Setup Flask routes."""
    
    @app.route('/')
    def index() -> str:
        return render_template('index.html')
    
    @app.route('/api/devices')
    def get_devices() -> Dict[str, Any]:
        try:
            devices = device_manager.discover_devices()
            return jsonify({'success': True, 'devices': devices})
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/devices/<udid>')
    def get_device_info(udid: str) -> Dict[str, Any]:
        try:
            device_info = device_manager.get_device_info(udid)
            if device_info:
                return jsonify({'success': True, 'device': device_info})
            else:
                return jsonify({'success': False, 'error': 'Device not found'}), 404
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/devices/<udid>/apps')
    def get_device_apps(udid: str) -> Dict[str, Any]:
        try:
            apps = device_manager.get_installed_apps(udid)
            return jsonify({'success': True, 'apps': apps})
        except Exception as e:
            logger.error(f"Error getting device apps: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/scenarios')
    def get_scenarios() -> Dict[str, Any]:
        try:
            scenarios = test_runner.get_scenarios()
            scenario_data = [scenario.to_dict() for scenario in scenarios]
            return jsonify({'success': True, 'scenarios': scenario_data})
        except Exception as e:
            logger.error(f"Error getting scenarios: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Test management routes
    _setup_test_routes(app, test_runner)


def _setup_test_routes(app: Flask, test_runner: TestRunner) -> None:
    """Setup test-related routes."""
    
    @app.route('/api/tests', methods=['POST'])
    def start_test() -> Dict[str, Any]:
        return _handle_start_test(test_runner)
    
    @app.route('/api/tests/<test_id>', methods=['DELETE'])
    def stop_test(test_id: str) -> Dict[str, Any]:
        return _handle_stop_test(test_runner, test_id)
    
    @app.route('/api/tests/<test_id>')
    def get_test_result(test_id: str) -> Dict[str, Any]:
        return _handle_get_test_result(test_runner, test_id)
    
    @app.route('/api/tests')
    def get_tests() -> Dict[str, Any]:
        return _handle_get_tests(test_runner)
    
    @app.route('/api/tests/export')
    def export_tests() -> Dict[str, Any]:
        return _handle_export_tests(test_runner)


def _handle_start_test(test_runner: TestRunner) -> Dict[str, Any]:
    """Handle test start request."""
    try:
        data = request.get_json()
        scenario_id = data.get('scenario_id')
        device_udid = data.get('device_udid')
        
        if not scenario_id or not device_udid:
            return jsonify({'success': False, 'error': 'Missing scenario_id or device_udid'}), 400
        
        test_id = test_runner.start_test(scenario_id, device_udid)
        if test_id:
            return jsonify({'success': True, 'test_id': test_id})
        else:
            return jsonify({'success': False, 'error': 'Failed to start test'}), 500
    except Exception as e:
        logger.error(f"Error starting test: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def _handle_stop_test(test_runner: TestRunner, test_id: str) -> Dict[str, Any]:
    """Handle test stop request."""
    try:
        success = test_runner.stop_test(test_id)
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error stopping test: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def _handle_get_test_result(test_runner: TestRunner, test_id: str) -> Dict[str, Any]:
    """Handle get test result request."""
    try:
        test_result = test_runner.get_test_result(test_id)
        if test_result:
            return jsonify({'success': True, 'test': test_result.to_dict()})
        else:
            return jsonify({'success': False, 'error': 'Test not found'}), 404
    except Exception as e:
        logger.error(f"Error getting test result: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def _handle_get_tests(test_runner: TestRunner) -> Dict[str, Any]:
    """Handle get all tests request."""
    try:
        active_tests = test_runner.get_active_tests()
        completed_tests = test_runner.get_completed_tests()
        
        all_tests = []
        all_tests.extend([test.to_dict() for test in active_tests])
        all_tests.extend([test.to_dict() for test in completed_tests[-20:]])
        
        return jsonify({'success': True, 'tests': all_tests})
    except Exception as e:
        logger.error(f"Error getting tests: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def _handle_export_tests(test_runner: TestRunner) -> Dict[str, Any]:
    """Handle export tests request."""
    try:
        test_ids = request.args.get('test_ids')
        if test_ids:
            test_ids = test_ids.split(',')
        
        export_data = test_runner.export_test_results(test_ids)
        return jsonify({'success': True, 'data': export_data})
    except Exception as e:
        logger.error(f"Error exporting tests: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def _setup_socketio_handlers(socketio: SocketIO, device_manager: DeviceManager, test_runner: TestRunner) -> None:
    """Setup SocketIO event handlers."""
    
    # Add callback for test updates
    def test_update_callback(test_result: TestResult) -> None:
        socketio.emit('test_update', {
            'test_id': test_result.id,
            'status': test_result.status.value,
            'data': test_result.to_dict()
        })
    
    test_runner.add_callback(test_update_callback)
    
    @socketio.on('connect')
    def handle_connect() -> None:
        logger.info(f"Client connected: {request.sid}")
        emit('connected', {'status': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect() -> None:
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('join_test')
    def handle_join_test(data: Dict[str, Any]) -> None:
        test_id = data.get('test_id')
        if test_id:
            join_room(f"test_{test_id}")
            logger.info(f"Client {request.sid} joined test {test_id}")
    
    @socketio.on('leave_test')
    def handle_leave_test(data: Dict[str, Any]) -> None:
        test_id = data.get('test_id')
        if test_id:
            leave_room(f"test_{test_id}")
            logger.info(f"Client {request.sid} left test {test_id}")
    
    @socketio.on('get_device_status')
    def handle_get_device_status(data: Dict[str, Any]) -> None:
        udid = data.get('udid')
        if udid and device_manager.is_device_connected(udid):
            device_info = device_manager.get_device_info(udid)
            emit('device_status', {
                'udid': udid,
                'status': 'connected',
                'info': device_info
            })
        else:
            emit('device_status', {
                'udid': udid,
                'status': 'disconnected'
            })


def run_dev_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = True) -> None:
    """Run the development server."""
    app = create_app({'debug': debug})
    app.socketio.run(app, host=host, port=port, debug=debug)
