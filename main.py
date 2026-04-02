#!/usr/bin/env python3
import argparse
import json
import logging
import os
import signal
import sys
import time

from core.discovery import Host
from core.port_scanner import PortScanner
from core.bandwidth import BandwidthMonitor
from alerts.engine import AlertEngine, Alert, ConsoleNotifier, FileNotifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("monitor.log"),
    ]
)
logger = logging.getLogger("netmon")

class NetworkMonitor:
    def __init__(self, subnet, interval=60):
        self.subnet = subnet
        self.interval = interval
        self.running = True
        self.known_macs = set()
        self.port_history = {}

        self.scanner = PortScanner(timeout=0.5, max_workers=100)
        self.bw_monitor = BandwidthMonitor()

        self.alert_engine = AlertEngine()
        self.alert_engine.add_handler(ConsoleNotifier())
        self.alert_engine.add_handler(FileNotifier())

        signal.signal(signal.SIGINT, self._shutdown)

    def run(self):
        logger.info(f"Starting Network Monitor on {self.subnet}")
        cycle = 0
        while self.running:
            cycle += 1
            print(f"\n{'='*50}")
            print(f"  Scan #{cycle} | {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*50}")

            # Bandwidth
            samples, sys_info = self.bw_monitor.poll()
            print(f"  CPU: {sys_info['cpu']}%  "
                  f"RAM: {sys_info['ram']}%  "
                  f"Connections: {sys_info['connections']}")

            # Anomalies
            anomalies = self.bw_monitor.detect_anomalies(samples)
            for a in anomalies:
                self.alert_engine.fire(Alert(
                    alert_type="bandwidth_spike",
                    severity="WARNING",
                    message=f"Spike on {a['interface']}: {a['current_mbps']} MB/s",
                    data=a
                ))

            # Port scan on gateway
            gw = self.subnet.rsplit(".", 1)[0] + ".1"
            print(f"\n  Scanning gateway: {gw}")
            results = self.scanner.scan_host(gw)
            if results:
                for port, state, service in results:
                    print(f"  {gw}:{port} [{service}] {state}")

                # Check for port changes
                prev = self.port_history.get(gw, [])
                curr = [r[0] for r in results]
                opened = set(curr) - set(prev)
                for p in opened:
                    self.alert_engine.fire(Alert(
                        alert_type="port_opened",
                        severity="WARNING",
                        message=f"New open port on {gw}: {p}",
                        data={"ip": gw, "port": p}
                    ))
                self.port_history[gw] = curr
            else:
                print(f"  No open ports found on {gw}")

            logger.info(f"Cycle #{cycle} done. Waiting {self.interval}s...")
            time.sleep(self.interval)

    def _shutdown(self, signum, frame):
        print("\nShutting down...")
        self.running = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network Monitor")
    parser.add_argument("--subnet", default="192.168.1.0/24")
    parser.add_argument("--interval", type=int, default=30)
    args = parser.parse_args()

    monitor = NetworkMonitor(args.subnet, args.interval)
    monitor.run()
