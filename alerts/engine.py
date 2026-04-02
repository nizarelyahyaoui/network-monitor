import json
import logging
import sqlite3
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Alert:
    alert_type: str
    severity: str
    message: str
    data: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
        }

class AlertEngine:
    def __init__(self, db_path="alerts.db"):
        self.db_path = db_path
        self._handlers = []
        self._init_db()

    def add_handler(self, handler):
        self._handlers.append(handler)

    def fire(self, alert):
        self._save(alert)
        for h in self._handlers:
            try:
                h(alert)
            except Exception as e:
                logger.error(f"Handler error: {e}")

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT, severity TEXT,
                    message TEXT, data TEXT, timestamp REAL
                )
            """)

    def _save(self, alert):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO alerts (alert_type, severity, message, data, timestamp) "
                "VALUES (?, ?, ?, ?, ?)",
                (alert.alert_type, alert.severity,
                 alert.message, json.dumps(alert.data), alert.timestamp)
            )

    def get_recent(self, limit=20):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return rows

class ConsoleNotifier:
    COLORS = {"INFO": "\033[94m", "WARNING": "\033[93m", "CRITICAL": "\033[91m"}
    RESET = "\033[0m"

    def __call__(self, alert):
        color = self.COLORS.get(alert.severity, "")
        ts = time.strftime("%H:%M:%S", time.localtime(alert.timestamp))
        print(f"{color}[{ts}] [{alert.severity}] {alert.message}{self.RESET}")

class FileNotifier:
    def __init__(self, path="alerts.jsonl"):
        self.path = path

    def __call__(self, alert):
        with open(self.path, "a") as f:
            f.write(json.dumps(alert.to_dict()) + "\n")
