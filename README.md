# XAlgoNexus: BTC/ETH/USDT High-Frequency Arbitrage System

## Overview

XAlgoNexus is a real-time, high-frequency trading (HFT) system designed to capture triangular arbitrage opportunities across BTC, ETH, and USDT pairs on crypto exchanges like Binance. The system integrates classical statistical arbitrage logic with adaptive machine learning filters to optimize precision, profitability, and robustness.

## Features

* Binance WebSocket integration for real-time trade data
* Triangular arbitrage detection across BTC/USDT, ETH/USDT, and ETH/BTC
* Real-time spread and volatility metrics
* ML-based signal filtering using RandomForest classifiers
* Cointegration and anomaly scoring with statistical models
* Execution logic with smart order sequencing
* Real-time Prometheus metrics exposed for Grafana dashboards
* TimescaleDB (PostgreSQL) backend for time-series trade and feature storage
* Modular CLI for training, logging, testing, and running live

## System Architecture

```
Exchange WebSocket API --> Data Normalizer --> Feature Engineering -->
ML Filter + Cointegration + Anomaly Detector --> Strategy Logic -->
Execution Engine --> Risk Controller --> Metrics + DB Logging
```

## Technology Stack

* Python 3.10+
* FastAPI for async REST server
* Scikit-learn, PyTorch (ML inference)
* TimescaleDB/PostgreSQL
* Prometheus + Grafana for metrics
* Docker + Docker Compose (local dev)
* GitHub Actions for PR testing

## Directory Structure

```
.
├── crypto_feature_framework/
├── infra/
│   ├── monitoring/
│   └── docker-compose.yml
├── ml_model/
├── src/
│   ├── controllers/
│   ├── core/
│   ├── data_pipeline/
│   ├── execution_layer/
│   ├── feature_engineering/
│   ├── filters/
│   ├── main/
│   ├── messaging/
│   ├── metrics/
│   ├── risk_manager/
│   ├── scoring/
│   ├── signal_core/
│   ├── strategy_core/
│   └── tools/
├── logs/
├── xalgo_cli_runner.py
├── requirements.txt
└── README.md
```

## Quickstart

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/XAlgoNexus.git
cd XAlgoNexus
```

### 2. Setup Python Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Create a `.env` file in the root:

```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=11230428018
POSTGRES_DB=xalgo_trading_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 4. Launch Database & Metrics

```bash
docker-compose up -d timescaledb
```

### 5. Run Live System

```bash
python src/main/live_controller.py
```

### 6. Train ML Model

```bash
python src/tools/train_ml_filter.py
```

## Unified CLI (xalgo\_cli\_runner.py)

```bash
# Launch live pipeline
python xalgo_cli_runner.py run

# Retrain ML model
python xalgo_cli_runner.py train

# Show trade and signal logs
python xalgo_cli_runner.py logs

# Run tests
python xalgo_cli_runner.py test

# Clean unused files and bytecode
python xalgo_cli_runner.py clean
```

Alias it:

```bash
alias xalgo="python xalgo_cli_runner.py"
xalgo run
```

## Prometheus Metrics

Exposed via `/metrics` on port `9100`:

* `xalgo_latest_spread`
* `xalgo_latest_volatility`
* `xalgo_latest_imbalance`
* `xalgo_daily_pnl`
* `xalgo_confidence_score`
* `xalgo_cointegration_score`
* `xalgo_anomaly_score`
* `xalgo_composite_score`
* `mlfilter_total_predictions`
* `mlfilter_correct_predictions`

## Pull Requests & Auto-Merge

* Generate a patch: `git diff > patch.diff`
* Apply: `git apply patch.diff`
* Auto-merge via GitHub UI or CI/CD bot

## Clean Code Utilities

```bash
# Bytecode, pycache, empty __init__.py
find . -type f \( -name "*.pyc" -o -name "*~" \) -delete
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "__init__.py" -size 0 -delete

# Lint unused imports
autoflake --remove-all-unused-imports --recursive --ignore-init-module-imports --check .
```

Run via:

```bash
python xalgo_cli_runner.py clean
```

## Monitoring & Logs

* View Grafana dashboard via `infra/monitoring/prometheus.yml`
* Trade logs: `/logs/trade_log.csv`
* Signal logs: `/logs/signal_log.csv`
* Signal plots: `/logs/signal_analysis.png`

## Contact

* Team: [core@xalgonexus.com](mailto:core@xalgonexus.com)
* Ops: [ops@xalgonexus.com](mailto:ops@xalgonexus.com)

## License

(c) 2025 XAlgoNexus. All rights reserved.

---

Let the code trade while you sleep. ⚡
