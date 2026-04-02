import time
import logging
from collections import deque
from typing import List, Optional
import psutil

logger = logging.getLogger(__name__)

class BandwidthMonitor:
    def __init__(self, interfaces=None, history_size=60, anomaly_multiplier=3.0):
        self.interfaces = interfaces
        self.history_size = history_size
        self.anomaly_multiplier = anomaly_multiplier
        self._prev = {}
        self._history = {}
        self._last_poll = time.time()

    def poll(self):
        now = time.time()
        dt = now - self._last_poll
        self._last_poll = now
        counters = psutil.net_io_counters(pernic=True)
        samples = []

        for iface, stats in counters.items():
            if self.interfaces and iface not in self.interfaces:
                continue
            if iface in self._prev and dt > 0:
                prev = self._prev[iface]
                sample = {
                    "interface": iface,
                    "recv_bps": (stats.bytes_recv - prev.bytes_recv) / dt,
                    "send_bps": (stats.bytes_sent - prev.bytes_sent) / dt,
                }
                samples.append(sample)
                if iface not in self._history:
                    self._history[iface] = deque(maxlen=self.history_size)
                self._history[iface].append(sample)
            self._prev[iface] = stats

        sys_info = {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "connections": len(psutil.net_connections(kind="inet")),
        }
        return samples, sys_info

    def detect_anomalies(self, samples):
        anomalies = []
        for s in samples:
            hist = self._history.get(s["interface"])
            if not hist or len(hist) < 5:
                continue
            avg_recv = sum(x["recv_bps"] for x in hist) / len(hist)
            if avg_recv > 0 and s["recv_bps"] > avg_recv * self.anomaly_multiplier:
                anomalies.append({
                    "type": "bandwidth_spike",
                    "interface": s["interface"],
                    "current_mbps": round(s["recv_bps"] / 1e6, 2),
                    "baseline_mbps": round(avg_recv / 1e6, 2),
                })
        return anomalies
