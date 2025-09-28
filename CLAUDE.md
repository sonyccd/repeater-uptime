# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an FM Repeater Uptime Monitor that uses GNU Radio and RTL-SDR hardware to monitor amateur radio repeater activity and send heartbeats to an Uptime Kuma server when transmissions are detected.

## Development Commands

### Setup and Installation
```bash
# Automated setup with system dependencies and hardware testing
./setup_and_run.sh

# Quick run after initial setup
./run.sh

# Manual hardware testing
python3 test_hardware.py

# Manual dependency installation
pip install -r requirements.txt
```

### GNU Radio Development
```bash
# Build script with automatic change detection
./build.sh

# Force rebuild regardless of timestamps
./build.sh --force

# Manual GNU Radio compilation (if needed)
grcc repeater_monitor.grc

# Run with automatic build detection
./run.sh

# Run the complete monitor application directly
python3 repeater_monitor.py
```

### System Dependencies
```bash
# Install GNU Radio and RTL-SDR drivers (Ubuntu/Debian)
sudo apt install gnuradio gnuradio-dev gr-osmosdr rtl-sdr

# Test RTL-SDR hardware
rtl_test
```

## Architecture

### GNU Radio Companion (GRC) Based Design
The primary application (`uptime_monitor.grc` → `uptime_monitor.py`) is built using GNU Radio Companion, which generates the complete Python application including:

- **Signal Processing Chain**: RTL-SDR source → Low-pass filter → FM demodulator → Power detection
- **Native QT GUI**: All user interface elements created using GNU Radio QT blocks
- **Embedded Python Block**: Custom `uptime_kuma_monitor` class in the GRC flowgraph handles activity detection and HTTP heartbeats

### Key Components

1. **`repeater_monitor.grc`**: Primary GNU Radio Companion flowgraph
   - Contains complete RF processing chain
   - Embedded Python block for Uptime Kuma integration
   - All GUI controls defined as GRC blocks

2. **`repeater_monitor_epy_block_0.py`**: Auto-generated embedded Python block
   - Contains `repeater_uptime_monitor` class
   - Handles activity detection logic and HTTP heartbeat transmission
   - Regenerated automatically when GRC file is compiled

3. **Alternative Implementations**:
   - `simple_monitor.py`: Simulation-only version for testing without hardware
   - `repeater_monitor.py`: Manual QT implementation (has compatibility issues)
   - `integrated_monitor.py`: Hybrid approach (deprecated due to QT integration problems)

### Data Flow
1. RTL-SDR receives RF signals at configured frequency
2. GNU Radio processes FM signals and calculates power levels
3. Embedded Python block monitors power levels against threshold
4. When activity detected, HTTP GET request sent to Uptime Kuma server
5. Cooldown period prevents spam during long transmissions

## Development Guidelines

### Modifying the Application
- **Primary development**: Edit `repeater_monitor.grc` in GNU Radio Companion
- **Automatic building**: Use `./build.sh` or `./run.sh` for automatic change detection
- **Manual regeneration**: Run `grcc repeater_monitor.grc` if needed
- **Do not manually edit**: `repeater_monitor.py` is auto-generated
- **Embedded Python changes**: Modify the Python block source within the GRC file
- **Parameter fixing**: Build scripts automatically fix known GNU Radio generation issues

### GNU Radio Version Compatibility
- Designed for GNU Radio 3.10.9+
- Uses `gnuradio.fft.window` constants (not `firdes.WIN_*`)
- QT GUI blocks use native GNU Radio widgets to avoid integration issues

### Hardware Requirements
- RTL-SDR compatible USB dongle
- User must be in `plugdev` group for device access
- Requires functioning RTL-SDR drivers (`rtl_test` should work)

### Testing Without Hardware
Use `simple_monitor.py` for development and testing without RTL-SDR hardware. It simulates signal activity and demonstrates the Uptime Kuma integration.

## File Organization

- **`*.grc`**: GNU Radio Companion flowgraph files (source files)
- **`*_monitor.py`**: Generated or manual Python applications
- **`*_epy_block_*.py`**: Auto-generated embedded Python blocks
- **`setup_and_run.sh`**: Primary setup script with automatic dependency installation
- **`test_hardware.py`**: Hardware validation script