# /metrics/prometheus_scores.py

from prometheus_client import Gauge

# ------------------------
# Prometheus Gauges
# ------------------------
confidence_score_gauge = Gauge(
    "xalgo_confidence_score", "Model confidence score for trade signal"
)
cointegration_score_gauge = Gauge(
    "xalgo_cointegration_score", "Cointegration stability score for synthetic spread"
)
anomaly_score_gauge = Gauge(
    "xalgo_anomaly_score", "Anomaly detection score for market regime shifts"
)
composite_score_gauge = Gauge(
    "xalgo_composite_score", "Final combined score used for trade filtering"
)

# ------------------------
# Composite Scoring Logic
# ------------------------
def compute_composite_score(confidence: float, cointegration: float, anomaly: float) -> float:
    """
    Compute a composite score by averaging the three input metrics.
    Update this logic to apply different weights if needed.
    """
    return (confidence + cointegration + anomaly) / 3.0

def push_scores_to_prometheus(confidence: float, cointegration: float, anomaly: float) -> float:
    """
    Push individual and composite scores to Prometheus gauges.
    Returns the composite score.
    """
    composite = compute_composite_score(confidence, cointegration, anomaly)

    confidence_score_gauge.set(confidence)
    cointegration_score_gauge.set(cointegration)
    anomaly_score_gauge.set(anomaly)
    composite_score_gauge.set(composite)

    return composite
