<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created.

- [x] Clarify Project Requirements
	Python-based iOS battery drain testing utility with web interface and CLI tool

- [x] Scaffold the Project
	Created complete project structure with CLI and web interfaces, core modules, and comprehensive documentation

- [x] Customize the Project
	Implemented full feature set including device management, battery monitoring, test execution, CLI and web interfaces

- [x] Install Required Extensions
	No VS Code extensions needed for this Python project

- [x] Compile the Project
	Project structure verified, syntax checks passed. Dependencies require network access to install (pymobiledevice3, flask, etc.)

- [x] Create and Run Task
	Not applicable - Python project uses standard pip installation and command-line execution

- [x] Launch the Project
	Project ready to launch - requires dependency installation first. Created setup scripts and validation tools.

- [x] Ensure Documentation is Complete
	README.md created with comprehensive documentation, project structure validated, all files properly documented

## Project: iOS Battery Drain Testing Utility

This project provides both a standalone command-line utility and a web-based interface for testing battery drain on iOS apps using real devices. The utility communicates with iOS devices via libimobiledevice and provides comprehensive battery monitoring and automated testing scenarios.

### Key Features Implemented:
- **Device Management**: Automatic iOS device discovery and connection management
- **Battery Monitoring**: Real-time battery level tracking with drain rate calculations  
- **Test Scenarios**: Pre-built and custom test scenarios for different use cases
- **Dual Interfaces**: Both CLI and web-based interfaces for different user preferences
- **Data Export**: Test results can be exported in JSON format for analysis
- **Real-time Updates**: Web interface uses WebSocket for live test monitoring

### Project Structure:
- `ios_battery_tester/core/` - Core functionality (device management, battery monitoring, test execution)
- `ios_battery_tester/cli.py` - Command-line interface
- `ios_battery_tester/web/` - Flask web application with real-time dashboard
- `setup_dependencies.py` - System dependency installer for macOS
- `test_project.py` - Project validation script
