import socket
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)

SERVICE_MAP = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
    6379: "Redis", 8080: "HTTP-Alt", 27017: "MongoDB",
}

TOP_PORTS = [21, 22, 23, 25, 53, 80, 443, 445,
             3306, 3389, 5432, 6379, 8080, 27017]

class PortScanner:
    def __init__(self, timeout=0.5, max_workers=100):
        self.timeout = timeout
        self.max_workers = max_workers

    def scan_host(self, ip, ports=None):
        ports = ports or TOP_PORTS
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(self._tcp_connect, ip, p): p for p in ports}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        return sorted(results, key=lambda r: r[0])

    def _tcp_connect(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            if sock.connect_ex((ip, port)) == 0:
                service = SERVICE_MAP.get(port, "unknown")
                return (port, "open", service)
        except Exception:
            pass
        finally:
            sock.close()
        return None
