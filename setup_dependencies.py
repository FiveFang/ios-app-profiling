#!/usr/bin/env python3
"""
Setup script to install system dependencies for iOS Battery Tester.
Run this script to install required system dependencies on macOS.
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"📦 {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr}")
        return False


def check_homebrew():
    """Check if Homebrew is installed."""
    try:
        subprocess.run(["brew", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Homebrew not found. Please install Homebrew first:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False


def main():
    print("🔋 iOS Battery Tester - Dependency Installer")
    print("=" * 50)
    
    if not check_homebrew():
        sys.exit(1)
    
    # Install system dependencies
    dependencies = [
        ("brew install libimobiledevice", "Installing libimobiledevice"),
        ("brew install ideviceinstaller", "Installing ideviceinstaller"),
        ("brew install usbmuxd", "Installing usbmuxd"),
    ]
    
    failed_deps = []
    for cmd, desc in dependencies:
        if not run_command(cmd, desc):
            failed_deps.append(desc)
    
    if failed_deps:
        print(f"\n❌ {len(failed_deps)} dependencies failed to install:")
        for dep in failed_deps:
            print(f"   - {dep}")
        print("\nPlease install these manually and try again.")
        sys.exit(1)
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        run_command("python3 -m venv venv", "Creating Python virtual environment")
    
    print("\n✅ System dependencies installed successfully!")
    print("\nNext steps:")
    print("1. Activate virtual environment: source venv/bin/activate")
    print("2. Install Python dependencies: pip install -e .")
    print("3. Connect your iOS device via USB")
    print("4. Trust this computer on your device")
    print("5. Run: ios-battery-test devices")
    
    print("\n📖 For more information, see README.md")


if __name__ == "__main__":
    main()
