#!/bin/bash

# Quick run script for FM Repeater Monitor (assumes setup already completed)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Please run setup_and_run.sh first."
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
cd "$SCRIPT_DIR"

# Check if GRC file is newer than generated Python file
echo "Checking for GNU Radio flowgraph changes..."
if [ ! -f "repeater_monitor.py" ] || [ "repeater_monitor.grc" -nt "repeater_monitor.py" ]; then
    echo "Flowgraph changes detected. Regenerating Python code..."
    if command_exists grcc; then
        grcc repeater_monitor.grc
        if [ $? -eq 0 ]; then
            echo "✓ Python code regenerated successfully"

            # Fix the parameter issue in generated code
            if grep -q "activity_threshold=, cooldown_time=, uptime_kuma_url=" repeater_monitor.py; then
                echo "Fixing parameter passing in generated code..."
                sed -i 's/activity_threshold=, cooldown_time=, uptime_kuma_url=/activity_threshold=self.activity_threshold, cooldown_time=self.cooldown_time, uptime_kuma_url=self.uptime_kuma_url/' repeater_monitor.py
                echo "✓ Parameter fix applied"
            fi
        else
            echo "✗ Failed to regenerate Python code from GRC file"
            exit 1
        fi
    else
        echo "✗ grcc (GNU Radio Companion compiler) not found"
        echo "Please regenerate manually: grcc repeater_monitor.grc"
        exit 1
    fi
else
    echo "✓ Generated Python code is up to date"
fi

# Start the application
echo "Starting FM Repeater Monitor..."
python3 repeater_monitor.py