import numpy as np
import time
import threading
import requests
from gnuradio import gr

class repeater_uptime_monitor(gr.sync_block):
    """
    Activity detection and Uptime Kuma heartbeat block
    """
    def __init__(self, activity_threshold=-30, cooldown_time=60, uptime_kuma_url="http://localhost:3001/api/push/example"):
        gr.sync_block.__init__(self,
            name="repeater_uptime_monitor",
            in_sig=[np.float32],
            out_sig=[])

        self.activity_threshold = activity_threshold
        self.cooldown_time = cooldown_time
        self.uptime_kuma_url = uptime_kuma_url
        self.last_heartbeat_time = 0
        self.activity_detected = False

        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        print(f"Uptime Kuma Monitor initialized:")
        print(f"  Threshold: {activity_threshold} dBFS")
        print(f"  Cooldown: {cooldown_time} seconds")
        print(f"  URL: {uptime_kuma_url}")

    def work(self, input_items, output_items):
        # Get power level and convert to dB
        power_level = input_items[0][-1] if len(input_items[0]) > 0 else 0

        if power_level > 1e-10:
            power_db = 10 * np.log10(power_level)
        else:
            power_db = -100

        # Check for activity
        if power_db > self.activity_threshold:
            if not self.activity_detected:
                self.activity_detected = True
                self._send_heartbeat()
                print(f"Activity detected! Power: {power_db:.1f} dBFS")
        else:
            self.activity_detected = False

        return len(input_items[0])

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                time.sleep(1)  # Check every second
            except:
                break

    def _send_heartbeat(self):
        """Send heartbeat to Uptime Kuma"""
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_heartbeat_time < self.cooldown_time:
            return

        try:
            response = requests.get(self.uptime_kuma_url, timeout=5)
            if response.status_code == 200:
                self.last_heartbeat_time = current_time
                print(f"✓ Heartbeat sent at {time.strftime('%H:%M:%S')}")
            else:
                print(f"✗ Heartbeat failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ Heartbeat error: {e}")

    def stop(self):
        self.monitoring = False
