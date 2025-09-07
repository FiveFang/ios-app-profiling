#!/usr/bin/env python3
"""
Test script to verify iOS Battery Tester project structure and basic functionality.
This can run without external dependencies for initial validation.
"""

import os
import sys
import importlib.util
from pathlib import Path


def test_file_structure():
    """Test that all required files exist."""
    print("🧪 Testing project structure...")
    
    required_files = [
        "pyproject.toml",
        "requirements.txt", 
        "README.md",
        "ios_battery_tester/__init__.py",
        "ios_battery_tester/cli.py",
        "ios_battery_tester/core/__init__.py",
        "ios_battery_tester/core/device_manager.py",
        "ios_battery_tester/core/battery_monitor.py",
        "ios_battery_tester/core/test_runner.py",
        "ios_battery_tester/core/exceptions.py",
        "ios_battery_tester/web/__init__.py",
        "ios_battery_tester/web/app.py",
        "ios_battery_tester/web/templates/index.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True


def test_python_syntax():
    """Test Python files for syntax errors."""
    print("\n🧪 Testing Python syntax...")
    
    python_files = [
        "ios_battery_tester/__init__.py",
        "ios_battery_tester/core/__init__.py", 
        "ios_battery_tester/core/exceptions.py",
        "setup_dependencies.py"
    ]
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
    
    if syntax_errors:
        print("❌ Syntax errors found:")
        for error in syntax_errors:
            print(f"   {error}")
        return False
    
    print("✅ All Python files have valid syntax")
    return True


def test_project_metadata():
    """Test project metadata files."""
    print("\n🧪 Testing project metadata...")
    
    try:
        # Test pyproject.toml
        with open("pyproject.toml", 'r') as f:
            content = f.read()
            if 'name = "ios-battery-tester"' not in content:
                print("❌ pyproject.toml missing project name")
                return False
        
        # Test README.md
        with open("README.md", 'r') as f:
            content = f.read()
            if "# iOS Battery Drain Testing Utility" not in content:
                print("❌ README.md missing title")
                return False
    
    except Exception as e:
        print(f"❌ Error reading metadata files: {e}")
        return False
    
    print("✅ Project metadata files valid")
    return True


def test_entry_points():
    """Test that entry points are properly defined."""
    print("\n🧪 Testing entry points...")
    
    try:
        with open("pyproject.toml", 'r') as f:
            content = f.read()
            if 'ios-battery-test = "ios_battery_tester.cli:main"' not in content:
                print("❌ CLI entry point not found in pyproject.toml")
                return False
    
    except Exception as e:
        print(f"❌ Error checking entry points: {e}")
        return False
    
    print("✅ Entry points properly defined")
    return True


def main():
    """Run all tests."""
    print("🔋 iOS Battery Tester - Project Validation")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_python_syntax,
        test_project_metadata,
        test_entry_points
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Project validation successful!")
        print("\n📋 Next steps:")
        print("1. Run: python setup_dependencies.py")
        print("2. Activate venv: source venv/bin/activate") 
        print("3. Install dependencies: pip install -e .")
        print("4. Test CLI: ios-battery-test --help")
        return True
    else:
        print(f"\n❌ {total - passed} tests failed. Please fix issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
