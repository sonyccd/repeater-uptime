#!/bin/bash

# Build script for regenerating Python code from GNU Radio Companion flowgraph

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored output
print_status() {
    case $1 in
        "INFO") echo -e "\033[34m[INFO]\033[0m $2" ;;
        "SUCCESS") echo -e "\033[32m[SUCCESS]\033[0m $2" ;;
        "ERROR") echo -e "\033[31m[ERROR]\033[0m $2" ;;
    esac
}

cd "$SCRIPT_DIR"

print_status "INFO" "GNU Radio Companion Build Script"
echo "=================================="

# Check if GRC file exists
if [ ! -f "repeater_monitor.grc" ]; then
    print_status "ERROR" "repeater_monitor.grc not found in current directory"
    exit 1
fi

# Check if grcc is available
if ! command_exists grcc; then
    print_status "ERROR" "grcc (GNU Radio Companion compiler) not found"
    print_status "INFO" "Please install GNU Radio: sudo apt install gnuradio"
    exit 1
fi

# Check if regeneration is needed
if [ -f "repeater_monitor.py" ] && [ "repeater_monitor.py" -nt "repeater_monitor.grc" ]; then
    print_status "INFO" "Python code is already up to date"
    if [ "$1" != "--force" ]; then
        echo "Use --force to regenerate anyway"
        exit 0
    fi
fi

# Generate Python code from GRC
print_status "INFO" "Generating Python code from repeater_monitor.grc..."
grcc repeater_monitor.grc

if [ $? -eq 0 ]; then
    print_status "SUCCESS" "Python code generated successfully"

    # Check and fix parameter issue in generated code
    if grep -q "activity_threshold=, cooldown_time=, uptime_kuma_url=" repeater_monitor.py; then
        print_status "INFO" "Fixing parameter passing in generated code..."
        sed -i 's/activity_threshold=, cooldown_time=, uptime_kuma_url=/activity_threshold=self.activity_threshold, cooldown_time=self.cooldown_time, uptime_kuma_url=self.uptime_kuma_url/' repeater_monitor.py
        print_status "SUCCESS" "Parameter fix applied"
    fi

    print_status "SUCCESS" "Build complete! Run with: python3 repeater_monitor.py"
else
    print_status "ERROR" "Failed to generate Python code"
    print_status "INFO" "Check your GRC file for errors"
    exit 1
fi