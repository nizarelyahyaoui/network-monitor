import socket
import subprocess
import ipaddress
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Optional
import time

logger = logging.getLogger(__name__)

@dataclass
class Host:
    ip: str
    mac: Optional[str] = None
    hostname: Optional[str] = None
    latency_ms: Optional[float] = None
    is_alive: bool = False
    open_ports: List[int] = field(default_factory=list)
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "ip": self.ip, "mac": self.mac,
            "hostname": self.hostname, "latency_ms": self.latency_ms,
            "is_alive": self.is_alive, "open_ports": self.open_ports,
            "first_seen": self.first_seen, "last_seen": self.last_seen,
        }
