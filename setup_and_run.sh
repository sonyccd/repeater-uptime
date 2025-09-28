#!/bin/bash

# FM Repeater Uptime Monitor - Setup and Run Script
# This script sets up a virtual environment, installs dependencies, tests hardware, and runs the application

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "=== FM Repeater Uptime Monitor Setup ==="
echo "Script directory: $SCRIPT_DIR"
echo

# Function to print colored output
print_status() {
    case $1 in
        "INFO") echo -e "\033[34m[INFO]\033[0m $2" ;;
        "SUCCESS") echo -e "\033[32m[SUCCESS]\033[0m $2" ;;
        "WARNING") echo -e "\033[33m[WARNING]\033[0m $2" ;;
        "ERROR") echo -e "\033[31m[ERROR]\033[0m $2" ;;
    esac
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
print_status "INFO" "Checking system requirements..."

if ! command_exists python3; then
    print_status "ERROR" "Python 3 is not installed. Please install Python 3.6+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
print_status "SUCCESS" "Python version: $PYTHON_VERSION"

if ! command_exists pip3; then
    print_status "ERROR" "pip3 is not installed. Please install pip first."
    exit 1
fi

# Function to install GNU Radio packages
install_gnuradio() {
    print_status "INFO" "Installing GNU Radio and RTL-SDR packages..."

    # Detect OS
    if command_exists apt; then
        print_status "INFO" "Detected Debian/Ubuntu system"
        sudo apt update
        # Install packages, ignore non-critical errors (like xtrx-dkms kernel module failures)
        sudo apt install -y gnuradio gnuradio-dev gr-osmosdr rtl-sdr python3-pip python3-venv || true

        # Add user to plugdev group for RTL-SDR access
        if ! groups | grep -q plugdev; then
            print_status "INFO" "Adding user to plugdev group for RTL-SDR access..."
            sudo usermod -a -G plugdev "$USER"
            print_status "WARNING" "You may need to log out and back in for group changes to take effect"
        fi

    elif command_exists yum; then
        print_status "INFO" "Detected RedHat/CentOS system"
        sudo yum install -y gnuradio gnuradio-devel gr-osmosdr rtl-sdr python3-pip

    elif command_exists dnf; then
        print_status "INFO" "Detected Fedora system"
        sudo dnf install -y gnuradio gnuradio-devel gr-osmosdr rtl-sdr python3-pip

    else
        print_status "ERROR" "Unknown package manager. Please install manually:"
        print_status "INFO" "  GNU Radio, gr-osmosdr, rtl-sdr, python3-pip"
        return 1
    fi
}

# Check for GNU Radio system installation
print_status "INFO" "Checking for GNU Radio installation..."
if ! python3 -c "import gnuradio" 2>/dev/null; then
    print_status "WARNING" "GNU Radio not found in system Python."

    read -p "Would you like to install GNU Radio and dependencies automatically? (Y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_status "INFO" "Please install GNU Radio manually:"
        print_status "INFO" "  Ubuntu/Debian: sudo apt install gnuradio gnuradio-dev gr-osmosdr rtl-sdr"
        print_status "INFO" "  Or use conda: conda install -c conda-forge gnuradio gnuradio-osmosdr"
        exit 1
    fi

    if install_gnuradio; then
        print_status "SUCCESS" "GNU Radio installation completed"

        # Test again after installation
        if ! python3 -c "import gnuradio" 2>/dev/null; then
            print_status "ERROR" "GNU Radio installation failed or requires system restart"
            print_status "INFO" "Try logging out/in or rebooting, then run this script again"
            exit 1
        fi
    else
        print_status "ERROR" "Failed to install GNU Radio"
        exit 1
    fi
else
    print_status "SUCCESS" "GNU Radio found in system Python"
fi

# Check for osmosdr (gr-osmosdr)
if ! python3 -c "import osmosdr" 2>/dev/null; then
    print_status "WARNING" "gr-osmosdr not found"

    if command_exists apt; then
        print_status "INFO" "Installing gr-osmosdr..."
        # Ignore non-critical package errors (like xtrx-dkms)
        sudo apt install -y gr-osmosdr || true
    else
        print_status "ERROR" "Please install gr-osmosdr manually"
        exit 1
    fi

    # Test again
    if ! python3 -c "import osmosdr" 2>/dev/null; then
        print_status "ERROR" "gr-osmosdr installation failed"
        exit 1
    fi
fi

print_status "SUCCESS" "gr-osmosdr found"

# Check for RTL-SDR tools
if command_exists rtl_test; then
    print_status "SUCCESS" "RTL-SDR tools found"
else
    print_status "WARNING" "RTL-SDR tools not found. Install with: sudo apt install rtl-sdr"
fi

# Create virtual environment
print_status "INFO" "Setting up virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR" --system-site-packages
    print_status "SUCCESS" "Virtual environment created at $VENV_DIR"
else
    print_status "INFO" "Virtual environment already exists"
fi

# Activate virtual environment
print_status "INFO" "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
print_status "INFO" "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "INFO" "Installing Python requirements..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -r "$SCRIPT_DIR/requirements.txt"
    print_status "SUCCESS" "Requirements installed successfully"
else
    print_status "ERROR" "requirements.txt not found!"
    exit 1
fi

# Test hardware
print_status "INFO" "Testing hardware and dependencies..."
echo "----------------------------------------"

cd "$SCRIPT_DIR"
if python3 test_hardware.py; then
    print_status "SUCCESS" "Hardware test passed!"
    echo "----------------------------------------"

    # Ask user if they want to start the application
    echo
    read -p "Hardware test successful! Start the FM Repeater Monitor? (Y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_status "INFO" "Setup complete. To run manually:"
        print_status "INFO" "  source $VENV_DIR/bin/activate"
        print_status "INFO" "  python3 repeater_monitor.py"
        exit 0
    fi

    # Check if GRC file is newer than generated Python file
    print_status "INFO" "Checking for GNU Radio flowgraph changes..."
    if [ ! -f "repeater_monitor.py" ] || [ "repeater_monitor.grc" -nt "repeater_monitor.py" ]; then
        print_status "INFO" "Flowgraph changes detected. Regenerating Python code..."
        if command_exists grcc; then
            grcc repeater_monitor.grc
            if [ $? -eq 0 ]; then
                print_status "SUCCESS" "Python code regenerated successfully"

                # Fix the parameter issue in generated code
                if grep -q "activity_threshold=, cooldown_time=, uptime_kuma_url=" repeater_monitor.py; then
                    print_status "INFO" "Fixing parameter passing in generated code..."
                    sed -i 's/activity_threshold=, cooldown_time=, uptime_kuma_url=/activity_threshold=self.activity_threshold, cooldown_time=self.cooldown_time, uptime_kuma_url=self.uptime_kuma_url/' repeater_monitor.py
                    print_status "SUCCESS" "Parameter fix applied"
                fi
            else
                print_status "ERROR" "Failed to regenerate Python code from GRC file"
                exit 1
            fi
        else
            print_status "ERROR" "grcc (GNU Radio Companion compiler) not found"
            print_status "INFO" "Please regenerate manually: grcc repeater_monitor.grc"
            exit 1
        fi
    else
        print_status "SUCCESS" "Generated Python code is up to date"
    fi

    # Start the application
    print_status "INFO" "Starting FM Repeater Monitor..."
    echo "========================================="
    python3 repeater_monitor.py

else
    echo "----------------------------------------"
    print_status "ERROR" "Hardware test failed!"
    print_status "INFO" "Common issues:"
    print_status "INFO" "  1. RTL-SDR dongle not connected"
    print_status "INFO" "  2. GNU Radio not properly installed"
    print_status "INFO" "  3. Missing system dependencies"
    print_status "INFO" ""
    print_status "INFO" "To install system dependencies:"
    print_status "INFO" "  sudo apt update"
    print_status "INFO" "  sudo apt install gnuradio gnuradio-dev gr-osmosdr rtl-sdr"
    print_status "INFO" ""
    print_status "INFO" "To test RTL-SDR hardware:"
    print_status "INFO" "  rtl_test"

    exit 1
fi