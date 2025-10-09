#!/bin/bash

# iOS Battery Testing Web Interface Startup Script

echo "🚀 Starting iOS Battery Testing Web Interface..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo "   pip install -r web_requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install web dependencies if needed
pip install -q -r web_requirements.txt

# Check if main tools are available
if [ ! -f "instruments_tester.py" ]; then
    echo "❌ instruments_tester.py not found in current directory"
    exit 1
fi

if [ ! -f "device_profiling_parser.py" ]; then
    echo "❌ device_profiling_parser.py not found in current directory"
    exit 1
fi

# Start the web interface
echo "📱 Starting web server..."
echo ""
echo "🌐 Web Interface URLs:"
echo "   Dashboard:     http://localhost:5000"
echo "   Live Testing:  http://localhost:5000/live-testing"
echo "   File Analysis: http://localhost:5000/file-analysis"
echo "   Results:       http://localhost:5000/results"
echo "   Device Mgmt:   http://localhost:5000/devices"
echo ""
echo "🔋 Ready for iOS battery testing!"
echo ""

cd web_ui && python app.py
