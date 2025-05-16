# 🧪 XAlgoNexus – SYSTEM TEST PLAN

> This document provides a full QA and test strategy for validating the XAlgoNexus HFT system end-to-end, including ML filters, execution safety, signal generation, CI/CD, monitoring, and retraining integrity.

---

## 🔍 MODULE COVERAGE

### 📥 Phase 1: Data Ingestion (P0)
- [ ] TimescaleDB insertion works (via `binance_ingestor.py`)
- [ ] Historical replay triggers valid feature flow
- [ ] `data_normalizer` outputs normalized event types

### 🧠 Phase 2: Feature Engineering (P1)
- [ ] All computed features: implied spread, z-score, volatility, imbalance
- [ ] `feature_engineer.py` correctly buffers + computes per-pair signals
- [ ] `test_feature_engineer.py` produces synthetic pass

### 🧠 Phase 3: Signal Generation (P0)
- [ ] `signal_generator.predict_with_confidence()` returns signal + confidence
- [ ] Kalman z-score trends with synthetic pair
- [ ] Confidence threshold veto works
- [ ] Anomaly + cointegration score exported

### 🎯 Phase 4: ML Model Validation (P0)
- [ ] `train_ml_filter_combined.py` executes without failure
- [ ] Generates: `ml_model/triangular_rf_model.pkl`
- [ ] Confidence + Anomaly + Cointegration scores included
- [ ] Model loads in `ml_filter.py`, responds to `.predict_with_confidence()`

### 🔁 Phase 5: Execution Logic (P0)
- [ ] `trade_state_machine` runs leg 1 → leg 2 → leg 3
- [ ] Incomplete cycle triggers `hedge_handler.hedge()`
- [ ] `execution_log.json` records status per cycle
- [ ] `hedge_activations` increments on fallback

### 📈 Phase 6: Monitoring + Prometheus (P0)
- [ ] Metrics emitted: spread, volatility, pnl, z-score, anomaly, cointegration, precision, drift
- [ ] `xalgo_heartbeat` gauge updates every 1s
- [ ] `alert.rules.yml` triggers on:
  - No trades in 10m
  - Drift (pnl_error > 0.003)
  - No heartbeat in 2m
- [ ] `alertmanager.yml` Slack/webhook works

### 📊 Phase 7: Audit Logging (P1)
- [ ] `ShadowAuditLogger` writes JSON to `logs/shadow_audit/YYYY-MM-DD.json`
- [ ] Captures: decision, confidence, actual outcome
- [ ] Handles failure recovery on crash

### 🧬 Phase 8: CI/CD + Auto-Retraining (P0)
- [ ] `.github/workflows/xalgo_autobot.yml` works on:
  - Manual push
  - Weekly `cron`
  - Drift (auto-trigger block enabled)
- [ ] Retrained model committed to Git if changed
- [ ] `README_AUTO.md` regenerates
- [ ] Prometheus endpoint verified in CI

### 🧠 Phase 9: Model Monitoring (P0)
- [ ] `xalgo_model_precision` updated after each trade
- [ ] `xalgo_model_pnl_error` matches actual vs expected
- [ ] Shadow audit logs match expected win rate
- [ ] Alerts trigger when model precision < 0.55

---

## ✅ Priorities Summary

| Phase              | Priority | Status       |
|-------------------|----------|--------------|
| Data Ingestion     | P0       | [ ]          |
| Feature Engineering| P1       | [ ]          |
| Signal Generation  | P0       | [ ]          |
| ML Model Validation| P0       | [ ]          |
| Execution Safety   | P0       | [ ]          |
| Monitoring         | P0       | [ ]          |
| Audit Logging      | P1       | [ ]          |
| CI/CD Pipeline     | P0       | [ ]          |
| Model Monitoring   | P0       | [ ]          |

---

> ☑️ To run all validation tests: `pytest` or CLI suite `xalgo_cli_runner.py test`  
> 🧠 For retraining: `PYTHONPATH=src python src/tools/train_ml_filter_combined.py`