#!/usr/bin/env python3
"""
Simplified FM Repeater Uptime Monitor
GNU Radio QT GUI application to monitor FM repeater activity and send heartbeats to Uptime Kuma
"""

import sys
import time
import threading
import requests
from PyQt5 import Qt, QtCore, QtWidgets
import numpy as np


class SimpleRepeaterMonitor(QtWidgets.QWidget):
    """Simplified version without GNU Radio integration for testing"""

    def __init__(self):
        super().__init__()

        # Initialize variables
        self.monitoring = False
        self.last_heartbeat_time = 0
        self.activity_detected = False

        # Default values
        self.frequency = 146.52  # MHz
        self.cooldown_time = 60  # seconds
        self.uptime_kuma_url = "http://localhost:3001/api/push/example"
        self.activity_threshold = -30  # dBFS

        # Setup GUI
        self.setupUi()

        # Setup timer for GUI updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(100)  # Update every 100ms

    def setupUi(self):
        """Setup the QT GUI interface"""
        self.setObjectName("SimpleRepeaterMonitor")
        self.resize(600, 400)
        self.setWindowTitle("FM Repeater Uptime Monitor (Simple Version)")

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)

        # Control panel
        control_group = QtWidgets.QGroupBox("Control Panel")
        control_layout = QtWidgets.QGridLayout(control_group)

        # Frequency input
        control_layout.addWidget(QtWidgets.QLabel("Frequency (MHz):"), 0, 0)
        self.freq_spinbox = QtWidgets.QDoubleSpinBox()
        self.freq_spinbox.setRange(80.0, 1000.0)
        self.freq_spinbox.setValue(146.52)
        self.freq_spinbox.setDecimals(3)
        self.freq_spinbox.setSuffix(" MHz")
        self.freq_spinbox.valueChanged.connect(self.on_frequency_changed)
        control_layout.addWidget(self.freq_spinbox, 0, 1)

        # Cooldown time
        control_layout.addWidget(QtWidgets.QLabel("Cooldown (seconds):"), 1, 0)
        self.cooldown_spinbox = QtWidgets.QSpinBox()
        self.cooldown_spinbox.setRange(10, 600)
        self.cooldown_spinbox.setValue(60)
        self.cooldown_spinbox.valueChanged.connect(self.on_cooldown_changed)
        control_layout.addWidget(self.cooldown_spinbox, 1, 1)

        # Uptime Kuma URL
        control_layout.addWidget(QtWidgets.QLabel("Uptime Kuma URL:"), 2, 0)
        self.url_lineedit = QtWidgets.QLineEdit()
        self.url_lineedit.setText(self.uptime_kuma_url)
        self.url_lineedit.textChanged.connect(self.on_url_changed)
        control_layout.addWidget(self.url_lineedit, 2, 1)

        # Activity threshold
        control_layout.addWidget(QtWidgets.QLabel("Activity Threshold (dBFS):"), 3, 0)
        self.threshold_spinbox = QtWidgets.QSpinBox()
        self.threshold_spinbox.setRange(-60, 0)
        self.threshold_spinbox.setValue(-30)
        self.threshold_spinbox.valueChanged.connect(self.on_threshold_changed)
        control_layout.addWidget(self.threshold_spinbox, 3, 1)

        # Start/Stop button
        self.start_stop_button = QtWidgets.QPushButton("Start Monitoring")
        self.start_stop_button.clicked.connect(self.toggle_monitoring)
        control_layout.addWidget(self.start_stop_button, 4, 0, 1, 2)

        main_layout.addWidget(control_group)

        # Status panel
        status_group = QtWidgets.QGroupBox("Status")
        status_layout = QtWidgets.QVBoxLayout(status_group)

        self.status_label = QtWidgets.QLabel("Status: Stopped")
        status_layout.addWidget(self.status_label)

        self.activity_label = QtWidgets.QLabel("Activity: None")
        status_layout.addWidget(self.activity_label)

        self.last_heartbeat_label = QtWidgets.QLabel("Last Heartbeat: Never")
        status_layout.addWidget(self.last_heartbeat_label)

        self.signal_level_label = QtWidgets.QLabel("Signal Level: -- dBFS")
        status_layout.addWidget(self.signal_level_label)

        main_layout.addWidget(status_group)

        # Instructions
        instructions = QtWidgets.QLabel("""
<b>Instructions:</b><br>
1. Set your repeater frequency<br>
2. Enter your Uptime Kuma push monitor URL<br>
3. Click 'Start Monitoring' to begin<br>
<br>
<i>Note: This is a simplified test version. The full version with RTL-SDR<br>
integration requires additional GNU Radio fixes.</i>
        """)
        instructions.setAlignment(QtCore.Qt.AlignTop)
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)

        # Test heartbeat button
        self.test_button = QtWidgets.QPushButton("Test Heartbeat")
        self.test_button.clicked.connect(self.send_test_heartbeat)
        main_layout.addWidget(self.test_button)

    def on_frequency_changed(self, value):
        """Handle frequency change"""
        self.frequency = value

    def on_cooldown_changed(self, value):
        """Handle cooldown time change"""
        self.cooldown_time = value

    def on_url_changed(self, text):
        """Handle Uptime Kuma URL change"""
        self.uptime_kuma_url = text

    def on_threshold_changed(self, value):
        """Handle activity threshold change"""
        self.activity_threshold = value

    def toggle_monitoring(self):
        """Start or stop monitoring"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        """Start the monitoring process"""
        self.monitoring = True
        self.start_stop_button.setText("Stop Monitoring")
        self.status_label.setText("Status: Monitoring (Simulated)")

        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()

    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.monitoring = False
        self.start_stop_button.setText("Start Monitoring")
        self.status_label.setText("Status: Stopped")

    def simulation_loop(self):
        """Simulate activity detection for testing"""
        while self.monitoring:
            try:
                # Simulate random signal levels
                noise_floor = -45
                signal_level = noise_floor + np.random.normal(0, 5)

                # Occasionally simulate activity
                if np.random.random() < 0.05:  # 5% chance per check
                    signal_level = -15 + np.random.normal(0, 3)
                    if not self.activity_detected:
                        self.activity_detected = True
                        self.send_heartbeat()
                else:
                    self.activity_detected = False

                # Update signal level for display
                self.current_signal_level = signal_level

                time.sleep(0.5)  # Check every 500ms

            except Exception as e:
                print(f"Error in simulation: {e}")
                time.sleep(1)

    def send_heartbeat(self):
        """Send heartbeat to Uptime Kuma server"""
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_heartbeat_time < self.cooldown_time:
            return

        try:
            response = requests.get(self.uptime_kuma_url, timeout=5)
            if response.status_code == 200:
                self.last_heartbeat_time = current_time
                print(f"Heartbeat sent successfully at {time.strftime('%H:%M:%S')}")
            else:
                print(f"Heartbeat failed with status: {response.status_code}")

        except Exception as e:
            print(f"Error sending heartbeat: {e}")

    def send_test_heartbeat(self):
        """Send a test heartbeat manually"""
        self.last_heartbeat_time = 0  # Reset cooldown for testing
        self.send_heartbeat()

    def update_gui(self):
        """Update GUI elements"""
        if self.monitoring:
            # Update activity status
            if self.activity_detected:
                self.activity_label.setText("Activity: DETECTED")
                self.activity_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.activity_label.setText("Activity: None")
                self.activity_label.setStyleSheet("color: black;")

            # Update signal level
            if hasattr(self, 'current_signal_level'):
                self.signal_level_label.setText(f"Signal Level: {self.current_signal_level:.1f} dBFS")

            # Update last heartbeat time
            if self.last_heartbeat_time > 0:
                heartbeat_time = time.strftime('%H:%M:%S', time.localtime(self.last_heartbeat_time))
                self.last_heartbeat_label.setText(f"Last Heartbeat: {heartbeat_time}")

    def closeEvent(self, event):
        """Handle application close"""
        self.stop_monitoring()
        event.accept()


def main():
    """Main application entry point"""
    app = QtWidgets.QApplication(sys.argv)

    # Create and show the main window
    window = SimpleRepeaterMonitor()
    window.show()

    # Run the application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()