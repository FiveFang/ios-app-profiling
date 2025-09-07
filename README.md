# iOS Battery Drain Testing Utility

A comprehensive Python utility for testing battery drain on iOS apps using real devices. The utility provides both command-line and web-based interfaces for monitoring battery consumption with support for **app-specific testing** and **charging control guidance**.

## ✨ Key Features

- **� App-Specific Monitoring**: Target specific iOS apps for focused battery drain analysis
- **🔋 Charging Control**: Guided instructions for proper charging control during tests  
- **📊 Real-time Monitoring**: Live battery level tracking with drain rate calculations
- **🔍 Device Discovery**: Automatic iOS device detection and connection management
- **📈 Advanced Analytics**: Trend analysis and comprehensive reporting
- **💾 Data Export**: Test results exported in JSON format with rich metadata
- **🎯 Multiple Test Modes**: Quick monitoring, comprehensive testing, and app-focused analysis

## 🚀 Quick Start

### Prerequisites
- macOS with Xcode Command Line Tools installed
- iOS device connected via USB with developer trust enabled
- Python 3.7+ with `click` and `rich` libraries

### Installation
```bash
# Clone or download the project
cd ios-battery-tests

# Install Python dependencies
pip install click rich

# Set up system dependencies (libimobiledevice)
python setup_dependencies.py
```

### Basic Usage

#### 1. List Connected Devices
```bash
python simple_tester.py devices
```

#### 2. List Installed Apps
```bash
python simple_tester.py apps
```

#### 3. Quick Battery Monitoring (5 minutes)
```bash
python simple_tester.py monitor --duration 5
```

#### 4. App-Specific Battery Test (30 minutes)
```bash
python simple_tester.py app_test --app "YouTube" --duration 30
```

#### 5. Comprehensive Battery Test with Custom Settings
```bash
python simple_tester.py test --app "Instagram" --duration 60 --interval 30
```

## 📋 Available Commands

| Command | Description | Key Options |
|---------|-------------|-------------|
| `devices` | List connected iOS devices | - |
| `apps` | Show all installed apps | - |
| `monitor` | Real-time battery monitoring | `--app`, `--duration` |
| `test` | Standard battery drain test | `--app`, `--duration`, `--interval` |
| `app_test` | Comprehensive app-focused test | `--app` (required), `--duration` |

### Command Options

- `--udid`: Target specific device by UDID (partial match supported)
- `--app, -a`: App name or bundle ID to monitor (e.g., "YouTube", "com.google.ios.youtube")
- `--duration, -d`: Test duration in minutes (default varies by command)
- `--interval, -i`: Reading interval in seconds (default: 30-60s)
- `--no-charging-check`: Skip charging control instructions
- `--no-charging-check`: Skip charging control instructions

## 🔋 Charging Control for Accurate Testing

For precise battery drain measurements, the utility provides comprehensive charging control instructions:

### Before Testing:
1. **🔌 Keep USB connected** for device communication
2. **⚙️ Disable "Optimized Battery Charging"** in Settings → Battery → Battery Health
3. **🔋 Charge to desired starting level** (90-95% recommended)
4. **🚫 Unplug USB cable** to stop charging before starting test

### During Testing:
- **📱 Keep target app active** and in use
- **🚫 Do not reconnect USB** cable
- **⚡ Monitor real-time progress** via the utility

### After Testing:
- **🔌 Reconnect USB** to resume charging
- **⚙️ Re-enable charging optimizations** if desired

## 📊 Test Results & Analytics

### Standard Metrics
- **Initial/Final Battery Levels**: Start and end percentages
- **Total Drain**: Battery consumed during test period  
- **Drain Rate**: Percentage per hour consumption rate
- **Charging Detection**: Warnings if charging occurred during test

### Advanced Analytics (app_test command)
- **Trend Analysis**: Early vs. late period drain comparison
- **App Metadata**: Version, bundle ID, and display name
- **Device Information**: iOS version, model, and device name
- **Test Conditions**: Duration, intervals, and initial charging state

### Sample Output
```json
{
  "readings": [
    {
      "timestamp": "2025-09-05T16:45:00.000000",
      "level": 95,
      "charging": false,
      "elapsed_minutes": 0,
      "monitored_app": {
        "bundle_id": "com.google.ios.youtube", 
        "display_name": "YouTube"
      }
    }
  ],
  "initial_level": 95,
  "final_level": 85,
  "total_drain": 10,
  "drain_rate_per_hour": 20.0,
  "app_monitored": {...},
  "charging_detected": false
}
```
```

### Python Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/ios-battery-tests.git
cd ios-battery-tests

# Install dependencies
pip install -e .

# Or install in development mode
pip install -e ."[dev]"
```

## Usage

### Command Line Interface

#### List Connected Devices
```bash
ios-battery-test devices
```

#### Monitor Battery Level
```bash
ios-battery-test monitor --udid <device_udid> --duration 60 --interval 30
```

#### List Available Test Scenarios
```bash
ios-battery-test scenarios
```

#### Run a Battery Drain Test
```bash
ios-battery-test test --udid <device_udid> --scenario "Idle Test" --wait --output results.json
```

#### View Test Results
```bash
ios-battery-test results --test-id <test_id>
```

#### List Installed Apps
```bash
ios-battery-test apps --udid <device_udid>
```

### Web Interface

#### Start the Web Server
```bash
# Development server
python -m ios_battery_tester.web.app

# Or using the entry point (if installed)
ios-battery-web
```

#### Access the Dashboard
Open your browser and navigate to `http://localhost:5000`

The web interface provides:
- **Dashboard**: Overview of connected devices and test statistics
- **Devices**: Device discovery and management
- **Tests**: Start new tests and monitor active ones
- **Results**: View and analyze test results with interactive charts

## Test Scenarios

### Built-in Scenarios

1. **Idle Test** (60 minutes)
   - Device idle with screen off
   - Measures baseline battery drain

2. **Screen On Test** (30 minutes)
   - Screen on at maximum brightness
   - Tests display power consumption

3. **App Usage Test** (45 minutes)
   - Specific app interaction simulation
   - Measures app-specific battery usage

4. **Video Playback Test** (120 minutes)
   - Continuous video playback
   - Tests media consumption impact

5. **Gaming Test** (90 minutes)
   - Intensive gaming simulation
   - High-performance battery testing

### Custom Scenarios

You can create custom test scenarios by extending the `TestScenario` class or using the web interface.

## API Reference

The web interface exposes a REST API:

### Endpoints

- `GET /api/devices` - List connected devices
- `GET /api/devices/{udid}` - Get device details
- `GET /api/devices/{udid}/apps` - Get installed apps
- `GET /api/scenarios` - List test scenarios
- `POST /api/tests` - Start a new test
- `GET /api/tests` - List all tests
- `GET /api/tests/{test_id}` - Get test details
- `DELETE /api/tests/{test_id}` - Stop a running test
- `GET /api/tests/export` - Export test results

### WebSocket Events

Real-time updates via Socket.IO:
- `test_update` - Test status changes
- `device_status` - Device connection status
- `battery_reading` - Real-time battery data

## Configuration

### Environment Variables

```bash
# Web server configuration
FLASK_ENV=development
FLASK_PORT=5000
FLASK_HOST=0.0.0.0

# Battery monitoring
BATTERY_MONITOR_INTERVAL=30  # seconds
TEST_DATA_RETENTION_DAYS=30
```

## Development

### Project Structure
```
ios_battery_tester/
├── __init__.py
├── cli.py                 # Command line interface
├── core/
│   ├── __init__.py
│   ├── device_manager.py  # iOS device management
│   ├── battery_monitor.py # Battery monitoring
│   ├── test_runner.py     # Test execution
│   └── exceptions.py      # Custom exceptions
└── web/
    ├── __init__.py
    ├── app.py            # Flask web application
    └── templates/
        └── index.html    # Web interface
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black ios_battery_tester/

# Sort imports
isort ios_battery_tester/

# Lint
flake8 ios_battery_tester/

# Type checking
mypy ios_battery_tester/
```

## Troubleshooting

### Common Issues

1. **Device Not Found**
   - Ensure device is connected via USB
   - Trust the computer on your iOS device
   - Check if `idevice_id -l` shows your device

2. **Permission Denied**
   - Make sure you have proper permissions for device access
   - Try running with `sudo` if necessary (not recommended)

3. **Battery Information Unavailable**
   - Some battery metrics may not be available on all devices
   - Ensure device is not in low power mode during testing

4. **Web Interface Not Loading**
   - Check if port 5000 is available
   - Try accessing via `127.0.0.1:5000` instead of `localhost:5000`

### Logging

Enable verbose logging for debugging:

```bash
ios-battery-test --verbose <command>
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [pymobiledevice3](https://github.com/doronz88/pymobiledevice3) for iOS device communication
- [libimobiledevice](https://libimobiledevice.org/) for low-level iOS protocols
- Flask and Socket.IO for the web interface
- Chart.js for data visualization

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information

## Roadmap

- [ ] Support for wireless device connections
- [ ] Advanced test scenario scripting
- [ ] Machine learning-based battery prediction
- [ ] Integration with CI/CD pipelines
- [ ] Support for Android devices
- [ ] Cloud-based test execution
