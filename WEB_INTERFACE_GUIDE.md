# iOS Battery Testing Web Interface

A comprehensive web-based interface for the iOS Battery Testing Suite, providing team-friendly access to all battery testing and analysis features.

## 🌟 Features

### 📊 Dashboard
- **Real-time Statistics**: Connected devices, active tests, total analyses
- **Recent Activity**: Latest test results and file analyses
- **Device Status**: Live device detection and capability overview
- **Quick Access**: Direct links to all major features

### 🔋 Live Battery Testing
- **Device Selection**: Visual device picker with connection status
- **App Discovery**: Automatic app listing with search functionality
- **Test Configuration**: Duration, test type, and parameter selection
- **Real-time Progress**: Live progress updates with WebSocket connection
- **Instant Results**: Battery consumption percentages and detailed analysis

### 📄 File Analysis
- **Drag & Drop Upload**: Easy .aar file upload with visual feedback
- **Automatic Parsing**: Multiple parsing methods with device profiling parser
- **Energy Estimation**: Percentage calculations with device capacity detection
- **Results Visualization**: Charts and detailed breakdowns
- **History Tracking**: Recent analyses with searchable results

### 📈 Results & Analytics
- **Historical Data**: Complete test history with filtering options
- **Trend Analysis**: Consumption trends over time with interactive charts
- **Test Comparison**: Side-by-side comparison of different tests
- **Export Options**: JSON export for further analysis
- **Performance Metrics**: Average consumption, test distribution

### 📱 Device Management
- **Live Detection**: Real-time device discovery and status updates
- **Connection Types**: WiFi and USB connection support
- **Capability Assessment**: Instruments compatibility checking
- **Setup Guidance**: Step-by-step connection instructions

## 🚀 Quick Start

### 1. Installation
```bash
# Install web dependencies
pip install -r web_requirements.txt

# Start the web interface
./start_web_ui.sh
```

### 2. Access the Interface
Open your browser to:
- **Dashboard**: http://localhost:5000
- **Live Testing**: http://localhost:5000/live-testing
- **File Analysis**: http://localhost:5000/file-analysis
- **Results**: http://localhost:5000/results
- **Device Management**: http://localhost:5000/devices

### 3. Connect iOS Device
- **WiFi (Recommended)**: Enable Wireless Debugging in iOS Settings
- **USB**: Connect via Lightning/USB-C cable with trust enabled

## 📋 User Workflows

### Live Battery Testing Workflow
1. **Connect Device**: WiFi or USB connection
2. **Select Device**: Choose from detected devices
3. **Pick App**: Search and select target application
4. **Configure Test**: Set duration and test type
5. **Monitor Progress**: Real-time updates during test execution
6. **Review Results**: Detailed consumption analysis with percentages

### File Analysis Workflow
1. **Upload File**: Drag and drop .aar file or browse to select
2. **Automatic Analysis**: System parses file with multiple methods
3. **Review Results**: Energy consumption estimates and device info
4. **Compare History**: View alongside previous analyses
5. **Export Data**: Download JSON results for further processing

### Team Collaboration Features
- **Shared Results**: All team members see same historical data
- **Live Updates**: Real-time progress sharing via WebSocket
- **Centralized Storage**: SQLite database for result persistence
- **Export Capabilities**: JSON export for integration with other tools

## 🛠 Technical Architecture

### Backend (Flask)
```
web_ui/app.py:
├── Device API endpoints (/api/devices, /api/apps)
├── Test management (/api/start-test, /api/test-status)
├── File upload & analysis (/api/upload-file)
├── Historical results (/api/historical-results)
├── WebSocket real-time updates
├── SQLite database integration
└── Background test execution
```

### Frontend (HTML5 + JavaScript)
```
web_ui/templates/:
├── dashboard.html      - Main overview with stats and activity
├── live_testing.html   - Interactive test configuration and monitoring
├── file_analysis.html  - Drag-and-drop file upload and results
├── results.html        - Historical analysis with charts
└── devices.html        - Device management and connection guide
```

### Database Schema
```sql
-- Test results from live testing
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY,
    test_id TEXT UNIQUE,
    test_type TEXT,
    device_name TEXT,
    app_bundle_id TEXT,
    duration_minutes INTEGER,
    total_consumption_mah REAL,
    app_consumption_mah REAL,
    total_percentage REAL,
    app_percentage REAL,
    device_capacity_mah INTEGER,
    status TEXT,
    created_at DATETIME,
    results_json TEXT
);

-- File analysis results
CREATE TABLE file_analyses (
    id INTEGER PRIMARY KEY,
    filename TEXT,
    file_size_kb REAL,
    duration_minutes REAL,
    total_consumption_mah REAL,
    app_consumption_mah REAL,
    total_percentage REAL,
    app_percentage REAL,
    device_capacity_mah INTEGER,
    analyzed_at DATETIME,
    results_json TEXT
);
```

## 🐳 Team Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:5000
# Data persists in ./output and ./uploads volumes
```

### Production Deployment
```bash
# Install production WSGI server
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 web_ui.app:app

# Or use provided Docker setup for containerized deployment
```

### Team Setup Recommendations
1. **Shared Mac**: Install on development Mac accessible to team
2. **Network Access**: Ensure port 5000 is accessible to team members
3. **Device Access**: Multiple team members can connect different devices
4. **Results Sharing**: Central database stores all team results
5. **Export Integration**: JSON export for CI/CD pipeline integration

## 🔧 Configuration

### Environment Variables
```bash
# Production settings
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key

# Database location
export DB_PATH=./team_battery_tests.db

# Upload limits
export MAX_CONTENT_LENGTH=104857600  # 100MB
```

### Customization Options
- **Branding**: Update templates with company colors/logos
- **Database**: Switch from SQLite to PostgreSQL/MySQL for larger teams
- **Authentication**: Add user authentication for team access control
- **Integrations**: Connect to Slack/Teams for test notifications
- **CI/CD**: Add API endpoints for automated testing integration

## 📊 API Reference

### Device Management
```bash
GET /api/devices                    # List connected devices
GET /api/apps/{device_id}          # List apps for device
```

### Test Execution
```bash
POST /api/start-test               # Start battery test
GET /api/test-status/{test_id}     # Get test progress
```

### File Analysis
```bash
POST /api/upload-file              # Upload and analyze .aar file
```

### Historical Data
```bash
GET /api/historical-results        # Get all test results and analyses
```

### WebSocket Events
```javascript
// Real-time test progress
socket.on('test_progress', function(data) {
    // data: {test_id, status, progress, message}
});

// Test completion
socket.on('test_complete', function(data) {
    // data: {test_id, status, results, error}
});
```

## 🎯 Benefits for Teams

### For Developers
- **Easy Access**: No command-line knowledge required
- **Visual Feedback**: Real-time progress and results visualization
- **Historical Tracking**: Compare performance over time
- **Quick Analysis**: Drag-and-drop file analysis

### For QA Teams
- **Standardized Testing**: Consistent test procedures across team
- **Result Sharing**: Central repository for all test results
- **Trend Analysis**: Identify performance regressions
- **Export Capabilities**: Integration with testing workflows

### For Team Leaders
- **Overview Dashboard**: Team testing activity at a glance
- **Performance Metrics**: Average consumption and testing statistics
- **Resource Management**: Device usage and testing capacity
- **Progress Tracking**: Real-time visibility into ongoing tests

## 🔍 Troubleshooting

### Common Issues
1. **Device Not Detected**: Check WiFi debugging or USB trust settings
2. **Test Fails to Start**: Ensure device is unlocked and app is installed
3. **File Upload Fails**: Check .aar file size (max 50MB) and format
4. **Real-time Updates Missing**: Verify WebSocket connection (check browser console)

### Debug Mode
```bash
# Enable debug logging
export DEBUG=1
python web_ui/app.py

# Check browser developer tools for JavaScript errors
# Monitor terminal output for backend errors
```

## 🔮 Future Enhancements

### Planned Features
- **User Authentication**: Team member login and role management
- **Advanced Analytics**: Machine learning for consumption prediction
- **Automated Testing**: Scheduled test execution
- **Mobile App**: iOS companion app for remote testing
- **Slack/Teams Integration**: Test result notifications
- **Advanced Filtering**: Search and filter historical results
- **Comparison Tools**: Side-by-side test comparison interface
- **CI/CD Integration**: GitHub Actions and Jenkins plugins

---

*This web interface transforms the iOS Battery Testing Suite into a team-friendly, production-ready solution for professional iOS battery analysis.*
