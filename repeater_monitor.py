#!/usr/bin/env python3
"""
FM Repeater Uptime Monitor
GNU Radio QT GUI application to monitor FM repeater activity and send heartbeats to Uptime Kuma
"""

import sys
import time
import threading
import requests
from PyQt5 import Qt, QtCore, QtWidgets
from gnuradio import gr, qtgui, analog, blocks, filter
from gnuradio.filter import firdes
from gnuradio.fft import window
import osmosdr
import numpy as np


class RepeaterMonitor(gr.top_block, Qt.QWidget):
    """Main application class combining GNU Radio flowgraph and QT GUI"""

    def __init__(self):
        gr.top_block.__init__(self, "Repeater Uptime Monitor")
        Qt.QWidget.__init__(self)

        # Initialize variables
        self.monitoring = False
        self.last_heartbeat_time = 0
        self.activity_detected = False

        # Default values
        self.frequency = 146.52e6  # 146.52 MHz
        self.cooldown_time = 60    # 60 seconds
        self.uptime_kuma_url = "http://localhost:3001/api/push/example"
        self.activity_threshold = -30  # dBFS

        # Setup GUI
        self.setupUi()

        # Setup GNU Radio flowgraph
        self.setup_flowgraph()

        # Setup timer for GUI updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(100)  # Update every 100ms

    def setupUi(self):
        """Setup the QT GUI interface"""
        self.setObjectName("RepeaterMonitor")
        self.resize(800, 600)
        self.setWindowTitle("FM Repeater Uptime Monitor")

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

        main_layout.addWidget(status_group)

        # Frequency sink placeholder (will be replaced after flowgraph setup)
        self.freq_sink_placeholder = QtWidgets.QLabel("Frequency Display (Start monitoring to view)")
        self.freq_sink_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        self.freq_sink_placeholder.setMinimumHeight(300)
        self.freq_sink_placeholder.setStyleSheet("border: 1px solid gray;")
        main_layout.addWidget(self.freq_sink_placeholder)

    def setup_flowgraph(self):
        """Setup the GNU Radio signal processing flowgraph"""
        # Sample rate
        self.samp_rate = samp_rate = 2048000

        # RTL-SDR source
        self.rtlsdr_source = osmosdr.source(args="numchan=1")
        self.rtlsdr_source.set_sample_rate(samp_rate)
        self.rtlsdr_source.set_center_freq(self.frequency)
        self.rtlsdr_source.set_freq_corr(0)
        self.rtlsdr_source.set_dc_offset_mode(0)
        self.rtlsdr_source.set_iq_balance_mode(0)
        self.rtlsdr_source.set_gain_mode(False)
        self.rtlsdr_source.set_gain(20)
        self.rtlsdr_source.set_if_gain(20)
        self.rtlsdr_source.set_bb_gain(20)
        self.rtlsdr_source.set_antenna('')
        self.rtlsdr_source.set_bandwidth(0)

        # Low pass filter for FM channel
        self.low_pass_filter = filter.fir_filter_ccf(
            8,  # Decimation
            firdes.low_pass(
                1,
                samp_rate,
                75000,  # Cutoff freq
                25000,  # Transition width
                window.WIN_HAMMING,
                6.76
            )
        )

        # FM demodulator
        self.fm_demod = analog.wfm_rcv(
            quad_rate=samp_rate//8,
            audio_decimation=4,
        )

        # Convert audio to power level for activity detection
        self.audio_power = blocks.multiply_const_ff(1.0)
        self.power_probe = blocks.probe_signal_f()

        # Convert complex to magnitude for power calculation
        self.complex_to_mag = blocks.complex_to_mag(1)
        self.mag_squared = blocks.multiply_ff(1)

        # Moving average for smoothing
        self.moving_avg = filter.single_pole_iir_filter_ff(0.01)

        # Frequency sink for GUI display
        self.qtgui_freq_sink = qtgui.freq_sink_c(
            1024,  # size
            window.WIN_BLACKMAN_hARRIS,  # wintype
            self.frequency,  # fc
            samp_rate,  # bw
            "Frequency Display",  # name
            1  # number of inputs
        )
        self.qtgui_freq_sink.set_update_time(0.10)
        self.qtgui_freq_sink.set_y_axis(-140, 10)
        self.qtgui_freq_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink.enable_autoscale(False)
        self.qtgui_freq_sink.enable_grid(False)

        # Connect blocks
        self.connect((self.rtlsdr_source, 0), (self.low_pass_filter, 0))
        self.connect((self.low_pass_filter, 0), (self.fm_demod, 0))
        self.connect((self.low_pass_filter, 0), (self.qtgui_freq_sink, 0))

        # Power detection chain for activity monitoring
        self.connect((self.low_pass_filter, 0), (self.complex_to_mag, 0))
        self.connect((self.complex_to_mag, 0), (self.mag_squared, 0))
        self.connect((self.complex_to_mag, 0), (self.mag_squared, 1))  # Square the magnitude
        self.connect((self.mag_squared, 0), (self.moving_avg, 0))
        self.connect((self.moving_avg, 0), (self.power_probe, 0))

    def on_frequency_changed(self, value):
        """Handle frequency change"""
        self.frequency = value * 1e6  # Convert MHz to Hz
        if hasattr(self, 'rtlsdr_source'):
            self.rtlsdr_source.set_center_freq(self.frequency)
            self.qtgui_freq_sink.set_frequency_range(self.frequency, self.rtlsdr_source.get_sample_rate())

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
        try:
            self.start()
            self.monitoring = True
            self.start_stop_button.setText("Stop Monitoring")
            self.status_label.setText("Status: Monitoring")

            # Replace placeholder with actual frequency sink
            layout = self.layout()
            freq_sink_widget = self.qtgui_freq_sink.qwidget()
            layout.replaceWidget(self.freq_sink_placeholder, freq_sink_widget)
            self.freq_sink_placeholder.hide()
            freq_sink_widget.show()

            # Start activity detection thread
            self.detection_thread = threading.Thread(target=self.activity_detection_loop, daemon=True)
            self.detection_thread.start()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to start monitoring: {str(e)}")

    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.monitoring = False
        try:
            if hasattr(self, '_running') and self._running:
                self.stop()
                self.wait()
        except:
            pass
        self.start_stop_button.setText("Start Monitoring")
        self.status_label.setText("Status: Stopped")

    def activity_detection_loop(self):
        """Background thread for activity detection"""
        while self.monitoring:
            try:
                # Get current power level
                power_level = self.power_probe.level()
                power_db = 10 * np.log10(power_level + 1e-10)  # Convert to dB

                # Check if activity detected
                if power_db > self.activity_threshold:
                    if not self.activity_detected:
                        self.activity_detected = True
                        self.send_heartbeat()
                else:
                    self.activity_detected = False

                time.sleep(0.1)  # Check every 100ms

            except Exception as e:
                print(f"Error in activity detection: {e}")
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
    window = RepeaterMonitor()
    window.show()

    # Run the application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()