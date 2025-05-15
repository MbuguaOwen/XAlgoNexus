import json
from datetime import datetime
from pathlib import Path

class ExecutionLogger:
    def __init__(self, log_dir="logs/execution"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.today_file = self.log_dir / f"{datetime.utcnow().date()}_executions.json"
        if not self.today_file.exists():
            with open(self.today_file, "w") as f:
                json.dump([], f)

    def log(self, data: dict):
        data["timestamp"] = datetime.utcnow().isoformat()
        try:
            with open(self.today_file, "r+") as f:
                logs = json.load(f)
                logs.append(data)
                f.seek(0)
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"[ExecutionLogger] Failed to log trade: {e}")