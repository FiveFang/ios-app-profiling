# iOS Battery Drain Testing Utility

A comprehensive Python utility for testing battery drain on iOS apps using real devices. Features **professional-grade Instruments integration**, **WiFi debugging support**, and **advanced validation systems** for accurate battery consumption measurements.

## ✨ Key Features

- **🔬 Instruments Profiling**: Native Apple Instruments integration for professional energy analysis
- **📡 WiFi Connection Support**: Eliminate charging interference with wireless device connections
- **📱 App-Specific Monitoring**: Target specific iOS apps for focused battery drain analysis
- **⚡ Charging Interference Detection**: Smart detection and handling of USB charging interference
- **🔋 Real Battery Capacity**: Device-specific battery capacity detection (mAh) with percentage conversion
- **📊 Hybrid Monitoring**: Real-time battery tracking + Instruments profiling for comprehensive analysis
- **🎯 Validation Framework**: Cross-validation with confidence levels and benchmark comparisons
- **💾 Advanced Export**: Detailed JSON reports with trace files and energy analysis Drain Testing Utility

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
- iOS device with Developer Trust enabled
- Python 3.7+ with dependencies
- libimobiledevice tools installed

### Installation
```bash
# Clone or download the project
cd ios-battery-tests

# Install Python dependencies
pip install click rich

# Set up system dependencies (libimobiledevice + Instruments)
python setup_dependencies.py
```

### Connection Options

#### USB Connection (Basic Testing)
```bash
# Check USB-connected devices
python instruments_tester.py devices
```

#### WiFi Connection (Recommended for Clean Testing)
```bash
# Enable WiFi debugging on your iOS device:
# Settings → Privacy & Security → Developer → Wireless Debugging → ON
# Connect to same WiFi network as your Mac

# Check WiFi-connected devices
python instruments_tester.py devices
```

### Available Tools

#### 1. **instruments_tester.py** (Professional Grade)
- Instruments profiling integration
- WiFi debugging support  
- Hybrid monitoring with validation
- Energy analysis and trace files

#### 2. **ultimate_battery_tester.py** (Comprehensive)
- Multiple battery detection methods
- Charging compensation algorithms
- Advanced validation framework

#### 3. **simple_tester.py** (Basic Testing)
- Quick battery monitoring
- App-specific testing
- Basic reporting

### Quick Commands

#### List Devices and Apps
```bash
python instruments_tester.py devices
python instruments_tester.py list-apps
```

#### Basic Monitoring
```bash
python instruments_tester.py monitor --duration 5
```

#### App-Specific Test with Instruments
```bash
python instruments_tester.py app-test --app "com.walmart.stores.allspark.beta" --duration 10
```

#### Hybrid Test (Real-time + Instruments)
```bash
python instruments_tester.py hybrid-test --app "com.walmart.stores.allspark.beta" --duration 15
```

#### Validation Test with Confidence Analysis
```bash
python instruments_tester.py validate-test --app "com.walmart.stores.allspark.beta" --duration 10
```

## 📋 Advanced Features

### WiFi Debugging Setup
For the most accurate battery testing without charging interference:

1. **Enable on iOS Device**:
   - Settings → Privacy & Security → Developer → Wireless Debugging → ON
   - Connect device to same WiFi network as your Mac

2. **Test WiFi Connection**:
   ```bash
   # Check for network devices
   idevice_id -n
   
   # Should show your device UDID if WiFi debugging is working
   ```

3. **Run Tests Over WiFi**:
   ```bash
   # All tools automatically detect WiFi vs USB connections
   python instruments_tester.py app-test --app "Fortnite" --duration 10
   ```

### Instruments Integration

#### Supported Templates
- **Activity Monitor**: Comprehensive energy profiling (recommended)
- **CPU Profiler**: App performance analysis 
- **System Trace**: Low-level system monitoring

#### Trace File Analysis
```bash
# Run test with trace export
python instruments_tester.py app-test --app "TikTok" --duration 15

# Trace files saved to: ./Traces/
# JSON reports include parsed energy data
```

### Charging Interference Handling

#### Problem Detection
```bash
# Check battery status and charging state
python instruments_tester.py devices --verbose

# Look for:
# - BatteryIsCharging: true/false
# - FullyCharged: true/false  
# - ExternalConnected: true/false
```

#### Solutions
1. **WiFi Testing**: Use wireless connection to eliminate USB charging
2. **Partial Battery**: Start tests below 100% to allow actual drain
3. **Charging Compensation**: Tools automatically detect and compensate for trickle charging

### Validation Framework

#### Confidence Analysis
```bash
python instruments_tester.py validate-test --app "YouTube" --duration 10
```

Provides:
- **Confidence Level**: HIGH/MEDIUM/LOW based on measurement quality
- **Cross-validation**: Multiple detection methods compared
- **Benchmark Comparison**: Against typical app power consumption patterns
- **Range Analysis**: Expected vs actual consumption validation

#### Energy Conversion
- **mAh to Percentage**: Device-specific battery capacity detection
- **Rate Calculations**: Per-hour consumption rates  
- **Efficiency Metrics**: Energy per minute, per interaction

## � Test Results & Energy Analysis

### Real-time Monitoring
- **Battery Level Tracking**: Percentage with decimal precision
- **Charging State Detection**: USB charging interference warnings
- **App Status Monitoring**: Target app activity and state
- **Device Information**: Hardware details and capacity

### Instruments Profiling Results
```json
{
  "energy_analysis": {
    "consumption_mah": 6.0,
    "consumption_percentage": 0.183,
    "rate_per_hour_mah": 72.0,
    "rate_per_hour_percentage": 2.2,
    "device_capacity_mah": 3274,
    "confidence": "HIGH",
    "method": "instruments_activity_monitor"
  },
  "real_time_readings": [
    {
      "timestamp": "2025-01-09T16:04:42.123456",
      "level": 99.0,
      "charging": false,
      "app_active": true,
      "elapsed_minutes": 0
    }
  ],
  "validation": {
    "confidence_level": "HIGH",
    "cross_validation": true,
    "expected_range_mah": [2.0, 15.0],
    "measured_in_range": true
  }
}
```

### Charging Interference Detection
```json
{
  "charging_analysis": {
    "charging_detected": false,
    "trickle_charge_detected": false,
    "external_connected": false,
    "battery_full": false,
    "interference_level": "NONE"
  }
}
```

### Energy Metrics
- **Consumption (mAh)**: Actual milliamp-hour usage
- **Consumption (%)**: Battery percentage equivalent  
- **Rate per Hour**: Projected hourly consumption
- **Efficiency**: Energy per app interaction/minute
- **Device Capacity**: Hardware battery capacity (mAh)
## 🛠️ Tool Comparison

| Tool | Best For | Key Features |
|------|----------|--------------|
| **instruments_tester.py** | Professional testing | Instruments integration, WiFi support, validation framework |
| **ultimate_battery_tester.py** | Comprehensive analysis | Multiple detection methods, charging compensation |
| **simple_tester.py** | Quick testing | Basic monitoring, easy setup |

### instruments_tester.py Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `devices` | List USB/WiFi devices | `python instruments_tester.py devices` |
| `list-apps` | Show installed apps | `python instruments_tester.py list-apps` |
| `monitor` | Real-time monitoring | `--duration 5` |
| `app-test` | App-specific test | `--app "com.walmart.stores.allspark.beta" --duration 10` |
| `hybrid-test` | Real-time + Instruments | `--app "com.walmart.stores.allspark.beta" --duration 15` |
| `profile` | Pure Instruments profiling | `--app "com.walmart.stores.allspark.beta" --duration 5` |
| `validate-test` | Validation with confidence | `--app "com.walmart.stores.allspark.beta" --duration 10` |
| `compare-test` | Baseline vs app testing | `--app "com.walmart.stores.allspark.beta" --duration 10` |

## 🔧 Troubleshooting

### WiFi Connection Issues
```bash
# Check WiFi debugging status
idevice_id -n

# If empty, enable on iOS device:
# Settings → Privacy & Security → Developer → Wireless Debugging
```

### Charging Interference
```bash
# Check battery status
ideviceinfo -q com.apple.mobile.battery

# Look for:
# BatteryIsCharging: false (should be false for clean testing)
# ExternalConnected: false (use WiFi to avoid)
```

### Instruments Issues
```bash
# Check Instruments availability
xcrun xctrace list devices

# Verify templates
xcrun xctrace list templates

# Check trace directory permissions
ls -la ./Traces/
```

### Common Error Solutions

1. **"No devices found"**
   - USB: Check `idevice_id -l`
   - WiFi: Enable wireless debugging, check `idevice_id -n`

2. **"App not found"**
   - Use exact app name: `python instruments_tester.py list-apps`
   - Try bundle ID instead of display name

3. **"Charging interference detected"**
   - Switch to WiFi connection
   - Start test below 100% battery
   - Use validation framework for compensation

4. **"Instruments profiling failed"**
   - Check Xcode Command Line Tools: `xcode-select --install`
   - Verify device trust and developer mode
   - Try different Instruments template
