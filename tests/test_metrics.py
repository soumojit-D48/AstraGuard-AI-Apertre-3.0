"""
Comprehensive tests for Prometheus Metrics module.

Tests cover:
- Metric creation and registration
- Counter, Gauge, Histogram operations
- Registry management
- Metric collection and formatting
"""

import pytest
import time
from prometheus_client import CollectorRegistry

# Import the metrics module
from core.metrics import (
    REGISTRY,
    # Circuit Breaker Metrics
    CIRCUIT_STATE,
    CIRCUIT_FAILURES_TOTAL,
    CIRCUIT_SUCCESSES_TOTAL,
    CIRCUIT_TRIPS_TOTAL,
    CIRCUIT_RECOVERIES_TOTAL,
    CIRCUIT_OPEN_DURATION_SECONDS,
    CIRCUIT_FAILURE_RATIO,
    # Anomaly Detection Metrics
    ANOMALY_DETECTIONS_TOTAL,
    ANOMALY_DETECTION_LATENCY,
    ANOMALY_MODEL_LOAD_ERRORS_TOTAL,
    ANOMALY_MODEL_FALLBACK_ACTIVATIONS,
    # System Health Metrics
    COMPONENT_HEALTH_STATUS,
    COMPONENT_ERROR_COUNT,
    COMPONENT_WARNING_COUNT,
    # Memory Store Metrics
    MEMORY_STORE_SIZE_BYTES,
    MEMORY_STORE_ENTRIES,
    MEMORY_STORE_RETRIEVALS,
    MEMORY_STORE_PRUNINGS,
    # Mission Phase Metrics
    MISSION_PHASE,
    ANOMALIES_BY_TYPE,
    # Recovery Metrics
    RECOVERY_ACTIONS_TOTAL,
    # Utility functions
    get_metrics_text,
    get_metrics_content_type
)


class TestCircuitBreakerMetrics:
    """Test circuit breaker metric operations"""

    def setup_method(self):
        # Reset metrics via private API or by re-registering? 
        # Standard way is to unregister, but we can't easily re-import.
        # So we just test values relative to current state or try to reset.
        # For simplicity in this env, we relies on get_sample_value.
        pass

    def test_circuit_state_gauge(self):
        """Test circuit state gauge metric"""
        # Test setting different states
        CIRCUIT_STATE.labels(circuit_name="test_circuit").set(0)  # CLOSED
        assert REGISTRY.get_sample_value('astraguard_circuit_state', labels={'circuit_name': 'test_circuit'}) == 0
        
        CIRCUIT_STATE.labels(circuit_name="test_circuit").set(1)  # OPEN
        assert REGISTRY.get_sample_value('astraguard_circuit_state', labels={'circuit_name': 'test_circuit'}) == 1
        
        CIRCUIT_STATE.labels(circuit_name="test_circuit").set(2)  # HALF_OPEN
        assert REGISTRY.get_sample_value('astraguard_circuit_state', labels={'circuit_name': 'test_circuit'}) == 2

    def test_circuit_failures_counter(self):
        """Test circuit failures counter"""
        before = REGISTRY.get_sample_value('astraguard_circuit_failures_total', labels={'circuit_name': 'test_circuit'}) or 0
        
        # Increment counter
        CIRCUIT_FAILURES_TOTAL.labels(circuit_name="test_circuit").inc()
        CIRCUIT_FAILURES_TOTAL.labels(circuit_name="test_circuit").inc(2)

        after = REGISTRY.get_sample_value('astraguard_circuit_failures_total', labels={'circuit_name': 'test_circuit'})
        assert after == before + 3

    def test_circuit_successes_counter(self):
        """Test circuit successes counter"""
        before = REGISTRY.get_sample_value('astraguard_circuit_successes_total', labels={'circuit_name': 'test_circuit'}) or 0
        CIRCUIT_SUCCESSES_TOTAL.labels(circuit_name="test_circuit").inc(5)
        after = REGISTRY.get_sample_value('astraguard_circuit_successes_total', labels={'circuit_name': 'test_circuit'})
        assert after == before + 5

    def test_circuit_trips_counter(self):
        """Test circuit trips counter"""
        before = REGISTRY.get_sample_value('astraguard_circuit_trips_total', labels={'circuit_name': 'test_circuit'}) or 0
        CIRCUIT_TRIPS_TOTAL.labels(circuit_name="test_circuit").inc()
        after = REGISTRY.get_sample_value('astraguard_circuit_trips_total', labels={'circuit_name': 'test_circuit'})
        assert after == before + 1

    def test_circuit_recoveries_counter(self):
        """Test circuit recoveries counter"""
        before = REGISTRY.get_sample_value('astraguard_circuit_recoveries_total', labels={'circuit_name': 'test_circuit'}) or 0
        CIRCUIT_RECOVERIES_TOTAL.labels(circuit_name="test_circuit").inc(3)
        after = REGISTRY.get_sample_value('astraguard_circuit_recoveries_total', labels={'circuit_name': 'test_circuit'})
        assert after == before + 3

    def test_circuit_open_duration_gauge(self):
        """Test circuit open duration gauge"""
        CIRCUIT_OPEN_DURATION_SECONDS.labels(circuit_name="test_circuit").set(45.5)
        val = REGISTRY.get_sample_value('astraguard_circuit_open_duration_seconds', labels={'circuit_name': 'test_circuit'})
        assert val == 45.5

    def test_circuit_failure_ratio_gauge(self):
        """Test circuit failure ratio gauge"""
        CIRCUIT_FAILURE_RATIO.labels(circuit_name="test_circuit").set(0.15)
        val = REGISTRY.get_sample_value('astraguard_circuit_failure_ratio', labels={'circuit_name': 'test_circuit'})
        assert val == 0.15


class TestAnomalyDetectionMetrics:
    """Test anomaly detection metric operations"""

    def test_anomaly_detections_counter(self):
        """Test anomaly detections counter"""
        before_model = REGISTRY.get_sample_value('astraguard_anomaly_detections_total', labels={'detector_type': 'model'}) or 0
        before_heuristic = REGISTRY.get_sample_value('astraguard_anomaly_detections_total', labels={'detector_type': 'heuristic'}) or 0

        ANOMALY_DETECTIONS_TOTAL.labels(detector_type="model").inc()
        ANOMALY_DETECTIONS_TOTAL.labels(detector_type="heuristic").inc(2)

        after_model = REGISTRY.get_sample_value('astraguard_anomaly_detections_total', labels={'detector_type': 'model'})
        after_heuristic = REGISTRY.get_sample_value('astraguard_anomaly_detections_total', labels={'detector_type': 'heuristic'})

        assert after_model == before_model + 1
        assert after_heuristic == before_heuristic + 2

    def test_anomaly_detection_latency_histogram(self):
        """Test anomaly detection latency histogram"""
        # Observe some latency values
        ANOMALY_DETECTION_LATENCY.labels(detector_type="model").observe(0.5)
        
        # For histograms, we check _sum or _count
        sum_val = REGISTRY.get_sample_value('astraguard_anomaly_detection_latency_seconds_sum', labels={'detector_type': 'model'})
        count_val = REGISTRY.get_sample_value('astraguard_anomaly_detection_latency_seconds_count', labels={'detector_type': 'model'})
        
        assert sum_val > 0
        assert count_val > 0

    def test_anomaly_model_load_errors_counter(self):
        """Test model load errors counter"""
        before = REGISTRY.get_sample_value('astraguard_anomaly_model_load_errors_total') or 0
        ANOMALY_MODEL_LOAD_ERRORS_TOTAL.inc()
        ANOMALY_MODEL_LOAD_ERRORS_TOTAL.inc(2)
        after = REGISTRY.get_sample_value('astraguard_anomaly_model_load_errors_total')
        assert after == before + 3

    def test_anomaly_model_fallback_activations(self):
        """Test model fallback activations counter"""
        before = REGISTRY.get_sample_value('astraguard_anomaly_model_fallback_activations_total') or 0
        ANOMALY_MODEL_FALLBACK_ACTIVATIONS.inc()
        after = REGISTRY.get_sample_value('astraguard_anomaly_model_fallback_activations_total')
        assert after == before + 1


class TestMetricsUtilities:
    """Test utility functions"""

    def test_get_metrics_text(self):
        """Test getting metrics as text format"""
        # Add some test data
        CIRCUIT_STATE.labels(circuit_name="test").set(0)
        
        # Get metrics text
        metrics_text = get_metrics_text()

        # Verify it's a string
        assert isinstance(metrics_text, str)
        assert len(metrics_text) > 0
        assert "astraguard_circuit_state" in metrics_text