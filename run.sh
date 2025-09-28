#!/bin/bash

# Quick run script for FM Repeater Monitor (assumes setup already completed)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Please run setup_and_run.sh first."
    exit 1
fi

# Activate virtual environment and run
echo "Starting FM Repeater Monitor..."
source "$VENV_DIR/bin/activate"
cd "$SCRIPT_DIR"
python3 repeater_monitor.py