#!/bin/bash
# Bash wrapper script to run all services
# This is a convenience script for users who prefer shell scripts

echo "Starting Task App..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    exit 1
fi

# Use python3 if available, otherwise use python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if requirements are installed
if ! $PYTHON_CMD -c "import uvicorn" &> /dev/null; then
    echo "⚠️  Dependencies not installed. Installing..."
    $PYTHON_CMD -m pip install -r requirements.txt
    echo ""
fi

# Run the Python script
exec $PYTHON_CMD run.py
