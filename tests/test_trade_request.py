import sys
import os

# ✅ Add the absolute path to /src/main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/main")))

from live_controller import app  # ✅ This now works due to sys.path fix
from fastapi.testclient import TestClient

client = TestClient(app)

def test_valid_trade_execution():
    payload = {
        "features": {
            "spread": -0.0021,
            "z_score": -2.9,
            "volume": 0.05,
            "imbalance": 0.4,
            "volatility": 0.0001
        }
    }

    response = client.post("/trade", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] in ["executed", "no_trade"]
    assert "signal" in result


def test_missing_features():
    payload = {}
    response = client.post("/trade", json=payload)
    assert response.status_code == 422


def test_unsupported_decision(monkeypatch):
    def mock_decision(_):
        return {"decision": "HOLD", "side": "NONE"}

    import live_controller
    import controllers.execution_controller
    monkeypatch.setattr(controllers.execution_controller.signal_gen, "generate_signal", mock_decision)

    payload = {
        "features": {
            "spread": 0.003,
            "z_score": 2.5,
            "volume": 0.01,
            "imbalance": 0.5,
            "volatility": 0.0002
        }
    }

    response = client.post("/trade", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "no_trade"


def test_zero_volume():
    payload = {
        "features": {
            "spread": -0.003,
            "z_score": -3.0,
            "volume": 0.0,
            "imbalance": 0.6,
            "volatility": 0.0003
        }
    }

    response = client.post("/trade", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] in ["executed", "no_trade"]
