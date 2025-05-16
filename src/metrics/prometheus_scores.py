# /metrics/prometheus_scores.py

from prometheus_client import Gauge

# ------------------------
# Prometheus Gauges
# ------------------------
confidence_score_gauge = Gauge(
    "mlfilter_confidence_score", "Confidence score from ML model"
)
cointegration_score_gauge = Gauge(
    "mlfilter_cointegration_score", "Triangle cointegration stability"
)
anomaly_score_gauge = Gauge(
    "mlfilter_anomaly_score", "Anomaly score from Isolation Forest"
)
composite_score_gauge = Gauge(
    "mlfilter_composite_score", "Final composite signal score"
)

# ------------------------
# Composite Scoring Logic
# ------------------------
def compute_composite_score(confidence: float, cointegration: float, anomaly: float) -> float:
    """
    Compute a composite score using weighted average of input metrics.
    Default weights: confidence (40%), cointegration (40%), inverse anomaly (20%).
    You may update weights based on performance benchmarks.
    """
    return 0.4 * confidence + 0.4 * cointegration + 0.2 * (1.0 - anomaly)

def push_scores_to_prometheus(confidence: float, cointegration: float, anomaly: float) -> float:
    """
    Push individual and composite scores to Prometheus.
    Returns the composite score.
    """
    composite = compute_composite_score(confidence, cointegration, anomaly)

    confidence_score_gauge.set(confidence)
    cointegration_score_gauge.set(cointegration)
    anomaly_score_gauge.set(anomaly)
    composite_score_gauge.set(composite)

    return composite
