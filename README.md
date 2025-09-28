# FM Repeater Uptime Monitor

A GNU Radio QT GUI application that monitors FM repeater activity using RTL-SDR and sends heartbeats to an Uptime Kuma server when activity is detected.

## Features

- **Real-time FM monitoring** using RTL-SDR dongles
- **Activity detection** based on signal strength threshold
- **Uptime Kuma integration** for automated heartbeat notifications
- **Configurable cooldown** to prevent spam heartbeats
- **Live frequency display** showing monitored spectrum
- **Simple GUI** for easy configuration and monitoring

## Requirements

- RTL-SDR compatible USB dongle
- GNU Radio 3.8+ with QT GUI support
- Python 3.6+
- Uptime Kuma server instance

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

1. **Start the application:**
   ```bash
   python3 repeater_monitor.py
   ```

2. **Configure settings:**
   - **Frequency**: Set the FM repeater downlink frequency (MHz)
   - **Cooldown**: Time between heartbeats in seconds (10-600)
   - **Uptime Kuma URL**: Your Uptime Kuma push monitor URL
   - **Activity Threshold**: Signal strength threshold in dBFS (-60 to 0)

3. **Begin monitoring:**
   - Click "Start Monitoring" to begin
   - Watch the frequency display for signal activity
   - Status panel shows current activity and heartbeat information

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

## Technical Details

The application uses:
- **osmosdr** for RTL-SDR interface
- **GNU Radio blocks** for FM demodulation and signal processing
- **PyQt5** for the graphical interface
- **Threading** for non-blocking activity detection
- **HTTP requests** for Uptime Kuma heartbeats
