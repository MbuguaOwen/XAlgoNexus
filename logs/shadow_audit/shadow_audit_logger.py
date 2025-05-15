import os
import json
from datetime import datetime
from pathlib import Path

class ShadowAuditLogger:
    def __init__(self, log_dir="logs/shadow_audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.today_file = self.log_dir / f"{datetime.utcnow().date()}_audit.json"
        if not self.today_file.exists():
            with open(self.today_file, "w") as f:
                json.dump([], f)

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
        try:
            with open(self.today_file, "r+") as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[ShadowAuditLogger] Failed to log entry: {e}")