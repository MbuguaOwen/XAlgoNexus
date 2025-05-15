# logging/shadow_audit_logger.py

import os
import json
import logging
from datetime import datetime
from pathlib import Path

class ShadowAuditLogger:
    def __init__(self, log_dir="logs/shadow_audit", enable_console_log=True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.today_file = self.log_dir / f"{datetime.utcnow().date()}_audit.json"
        self.enable_console_log = enable_console_log

        # Initialize log file with empty array if not exists
        if not self.today_file.exists():
            with open(self.today_file, "w") as f:
                json.dump([], f)

        # Setup console logger if enabled
        if self.enable_console_log:
            self.logger = logging.getLogger("audit_logger")
            if not self.logger.hasHandlers():
                handler = logging.StreamHandler()
                formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)

    def log(self, decision_dict, actual_outcome=None, actual_pnl=None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision_dict.get("decision"),
            "confidence": decision_dict.get("confidence"),
            "zscore": decision_dict.get("zscore"),
            "anomaly": decision_dict.get("anomaly"),
            "cointegration_stability": decision_dict.get("cointegration_stability"),
            "spread": decision_dict.get("spread"),
            "actual_outcome": actual_outcome,
            "actual_pnl": actual_pnl
        }

        # Log to JSON file
        try:
            with open(self.today_file, "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
        except Exception as e:
            print(f"[ShadowAuditLogger] Failed to log entry to JSON: {e}")

        # Log to console if enabled
        if self.enable_console_log:
            try:
                self.logger.info(
                    f"[SHADOW AUDIT] decision={entry['decision']} | "
                    f"confidence={entry['confidence']:.2f} | pnl={entry['actual_pnl']}"
                )
            except Exception as e:
                print(f"[ShadowAuditLogger] Console log error: {e}")
