# FM Repeater Uptime Monitor

A GNU Radio QT GUI application that monitors FM repeater activity using RTL-SDR and sends heartbeats to an Uptime Kuma server when activity is detected.

![GNU Radio Application](https://img.shields.io/badge/GNU%20Radio-3.10+-blue?logo=gnuradio)
![RTL-SDR](https://img.shields.io/badge/RTL--SDR-Compatible-green)
![Python](https://img.shields.io/badge/Python-3.6+-blue?logo=python)
![License](https://img.shields.io/badge/License-GPL--3.0-red)

## Features

- 📡 **Real-time FM monitoring** using RTL-SDR dongles
- 🎯 **Intelligent activity detection** based on configurable signal strength threshold
- 📊 **Live spectrum display** with real-time frequency visualization
- 🔄 **Uptime Kuma integration** for automated heartbeat notifications
- ⏱️ **Smart cooldown management** to prevent spam during long conversations
- 🎛️ **Professional GUI** built with native GNU Radio QT blocks
- 🔧 **Easy configuration** with real-time parameter adjustment

## Requirements

- **RTL-SDR compatible USB dongle** (RTL2832U based)
- **GNU Radio 3.10+** with QT GUI support
- **Python 3.6+**
- **Uptime Kuma server** instance
- **Linux/Windows/macOS** (tested on Ubuntu 24.04)

## Quick Start

**Automated setup and run:**
```bash
./setup_and_run.sh
```

This script will:
1. Create a virtual environment
2. Install all dependencies
3. Test your RTL-SDR hardware
4. Start the application if tests pass

**Quick run (after initial setup):**
```bash
./run.sh
```

## Manual Installation

1. Install GNU Radio and RTL-SDR drivers:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install gnuradio gnuradio-dev gr-osmosdr rtl-sdr

   # Or use conda/mamba
   conda install -c conda-forge gnuradio gnuradio-osmosdr
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Connect your RTL-SDR dongle and verify it's detected:
   ```bash
   rtl_test
   ```

## Usage

### Main Application
```bash
# Run the GNU Radio-based monitor (recommended)
python3 repeater_monitor.py

# Alternative: Test version without hardware
python3 simple_monitor.py
```

### Configuration
The application provides real-time GUI controls for:

- **📻 Frequency (Hz)**: Set the FM repeater downlink frequency
- **⚡ RF Gain**: Adjust RTL-SDR gain (0-50)
- **🎚️ Activity Threshold (dB)**: Signal strength threshold (-60 to 0 dBFS)
- **⏲️ Cooldown Time**: Seconds between heartbeats (10-600)
- **🌐 Uptime Kuma URL**: Your push monitor endpoint

### Monitoring
- **📈 Live spectrum display** shows real-time frequency domain
- **📊 Signal strength meter** displays current power levels
- **🟢 Activity detection** triggers automatic heartbeats
- **📝 Console output** shows heartbeat status and errors

## Uptime Kuma Setup

1. Create a new **Push** monitor in Uptime Kuma
2. Copy the generated push URL (e.g., `http://your-server:3001/api/push/abc123`)
3. Paste the URL into the application's "Uptime Kuma URL" field
4. The monitor will receive heartbeats when repeater activity is detected

## Configuration Tips

- **Frequency**: Use the repeater's output (downlink) frequency
- **Threshold**: Start with -30 dBFS and adjust based on noise floor
- **Cooldown**: Set to prevent multiple heartbeats during long conversations
- **Gain**: Adjust RTL-SDR gain if signals are too weak/strong (modify source code)

## Troubleshooting

- **No RTL-SDR detected**: Check USB connection and driver installation
- **GNU Radio errors**: Verify GNU Radio and gr-osmosdr installation
- **No frequency display**: Check QT GUI components are installed
- **Heartbeat failures**: Verify Uptime Kuma URL and network connectivity

## Architecture

### GNU Radio Companion Design
The application is built using **GNU Radio Companion (GRC)** which provides:
- 🏗️ **Visual flowgraph design** with drag-and-drop blocks
- 🔄 **Automatic Python generation** from `uptime_monitor.grc`
- 🎛️ **Native QT GUI integration** without widget compatibility issues
- 🐍 **Embedded Python blocks** for custom Uptime Kuma functionality

### Signal Processing Chain
```
RTL-SDR → Low-Pass Filter → FM Demodulator → Power Detection → Activity Monitor
   ↓              ↓               ↓              ↓              ↓
2.048 MHz     256 kHz        Audio          dBFS Level    HTTP Heartbeat
```

### Key Components
- **`repeater_monitor.grc`**: Primary GNU Radio Companion flowgraph
- **`repeater_monitor.py`**: Auto-generated Python application
- **`repeater_monitor_epy_block_0.py`**: Embedded Python for Uptime Kuma integration
- **`setup_and_run.sh`**: Automated dependency installation and hardware testing

### Technical Stack
- **🔧 GNU Radio 3.10+** for RF signal processing
- **📡 gr-osmosdr** for RTL-SDR hardware interface
- **🖥️ PyQt5** via GNU Radio QT GUI blocks
- **🌐 HTTP requests** for Uptime Kuma heartbeat API
- **⚡ Threading** for non-blocking activity detection

## Development

### Modifying the Application
1. **Edit the flowgraph**: Open `repeater_monitor.grc` in GNU Radio Companion
2. **Build and run**: Use any of these methods:
   ```bash
   # Automatic build and run (detects changes)
   ./run.sh

   # Manual build only
   ./build.sh

   # Force rebuild
   ./build.sh --force

   # Manual GNU Radio compilation
   grcc repeater_monitor.grc
   ```
3. **Test changes**: The scripts automatically regenerate Python code when the GRC file is modified

> ⚠️ **Important**: Never manually edit `repeater_monitor.py` - it's auto-generated!

### Build System Features
- **🔍 Change Detection**: Scripts automatically detect when GRC file is newer than Python
- **🔧 Auto-Regeneration**: Automatically runs `grcc` when changes are detected
- **🛠️ Parameter Fixing**: Automatically fixes known GNU Radio generation issues
- **⚡ Smart Caching**: Only rebuilds when necessary (unless forced)

### File Structure
```
├── repeater_monitor.grc            # 📝 Main GRC flowgraph (edit this)
├── repeater_monitor.py             # 🤖 Generated application (don't edit)
├── repeater_monitor_epy_block_0.py # 🐍 Generated embedded Python block
├── setup_and_run.sh               # 🚀 Automated setup and launch script
├── run.sh                          # ⚡ Quick launch with auto-build
├── build.sh                        # 🔨 Build script for development
├── test_hardware.py               # 🔧 RTL-SDR hardware validation
├── simple_monitor.py              # 🧪 Test version without hardware
├── requirements.txt               # 📦 Python dependencies
├── README.md                       # 📖 Project documentation
└── CLAUDE.md                       # 🤖 Claude Code guidance
```
