#!/bin/bash

# FM Repeater Monitor - Executable Builder
# Creates standalone executables using PyInstaller

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if GNU Radio is available
if ! command -v grcc &> /dev/null && ! command -v gnuradio-companion &> /dev/null; then
    print_error "GNU Radio is not installed (neither grcc nor gnuradio-companion found)"
    print_error "Please install GNU Radio 3.10+ before building"
    exit 1
fi

print_status "Building FM Repeater Monitor executable..."

# Step 1: Generate Python from GRC
print_status "Generating Python code from GRC flowgraph..."
if [ ! -f "repeater_monitor.py" ] || [ "repeater_monitor.grc" -nt "repeater_monitor.py" ]; then
    if command -v grcc &> /dev/null; then
        print_status "Using grcc to generate Python code..."
        grcc repeater_monitor.grc
    else
        print_status "Using gnuradio-companion to generate Python code..."
        gnuradio-companion --generate repeater_monitor.grc
    fi

    # Apply parameter fixes
    print_status "Applying parameter fixes to generated code..."
    sed -i.bak 's/activity_threshold=activity_threshold/activity_threshold=self.activity_threshold/g' repeater_monitor.py
    sed -i.bak 's/cooldown_time=cooldown_time/cooldown_time=self.cooldown_time/g' repeater_monitor.py
    sed -i.bak 's/uptime_kuma_url=uptime_kuma_url/uptime_kuma_url=self.uptime_kuma_url/g' repeater_monitor.py

    print_success "Python code generated and fixed successfully"
else
    print_status "Python code is up to date"
fi

# Step 2: Set up virtual environment and install dependencies
VENV_DIR="build_venv"

if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    print_status "Using existing virtual environment..."
fi

print_status "Activating virtual environment and installing dependencies..."
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Step 3: Test Python module
print_status "Testing Python module import..."
if python -c "import repeater_monitor; print('Module loads successfully')" 2>/dev/null; then
    print_success "Python module imports successfully"
else
    print_error "Python module failed to import"
    exit 1
fi

# Step 4: Create PyInstaller spec file
print_status "Creating PyInstaller specification file..."
cat > repeater_monitor.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['repeater_monitor.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('repeater_monitor_epy_block_0.py', '.'),
    ],
    hiddenimports=[
        'gnuradio',
        'gnuradio.gr',
        'gnuradio.blocks',
        'gnuradio.analog',
        'gnuradio.digital',
        'gnuradio.filter',
        'gnuradio.fft',
        'gnuradio.qtgui',
        'osmosdr',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'numpy',
        'requests',
        'threading',
        'time',
        'sys',
        'os',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='fm-repeater-monitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Step 5: Build executable
print_status "Building executable with PyInstaller..."
pyinstaller repeater_monitor.spec --clean --noconfirm

if [ -f "dist/fm-repeater-monitor" ] || [ -f "dist/fm-repeater-monitor.exe" ]; then
    print_success "Executable built successfully!"

    # Get platform info
    PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)

    # Normalize architecture
    case $ARCH in
        x86_64) ARCH="x64" ;;
        aarch64|arm64) ARCH="arm64" ;;
    esac

    # Rename executable with platform info
    if [ -f "dist/fm-repeater-monitor.exe" ]; then
        mv "dist/fm-repeater-monitor.exe" "dist/fm-repeater-monitor-${PLATFORM}-${ARCH}.exe"
        print_success "Executable: dist/fm-repeater-monitor-${PLATFORM}-${ARCH}.exe"
    else
        mv "dist/fm-repeater-monitor" "dist/fm-repeater-monitor-${PLATFORM}-${ARCH}"
        chmod +x "dist/fm-repeater-monitor-${PLATFORM}-${ARCH}"
        print_success "Executable: dist/fm-repeater-monitor-${PLATFORM}-${ARCH}"
    fi

    # Show file size
    if [ -f "dist/fm-repeater-monitor-${PLATFORM}-${ARCH}" ]; then
        SIZE=$(du -h "dist/fm-repeater-monitor-${PLATFORM}-${ARCH}" | cut -f1)
        print_status "Executable size: $SIZE"
    elif [ -f "dist/fm-repeater-monitor-${PLATFORM}-${ARCH}.exe" ]; then
        SIZE=$(du -h "dist/fm-repeater-monitor-${PLATFORM}-${ARCH}.exe" | cut -f1)
        print_status "Executable size: $SIZE"
    fi

    print_success "Build completed successfully!"
    print_status "To test the executable, make sure you have an RTL-SDR connected and run:"
    if [ -f "dist/fm-repeater-monitor-${PLATFORM}-${ARCH}.exe" ]; then
        print_status "  ./dist/fm-repeater-monitor-${PLATFORM}-${ARCH}.exe"
    else
        print_status "  ./dist/fm-repeater-monitor-${PLATFORM}-${ARCH}"
    fi

else
    print_error "Executable build failed!"
    exit 1
fi

# Cleanup
print_status "Cleaning up temporary files..."
rm -f *.bak
rm -f repeater_monitor.spec

# Deactivate virtual environment
deactivate

print_success "Build process completed!"
print_status "Virtual environment preserved at: $VENV_DIR"
print_status "To clean up: rm -rf $VENV_DIR"