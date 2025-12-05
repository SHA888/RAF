"""
RAF Experiments Module.

Provides empirical validation experiments for the three acceleration loops.
"""

from .error_mitigation import ErrorMitigationExperiment
from .metrics_collector import ExperimentalMetricsCollector

__all__ = [
    "ErrorMitigationExperiment",
    "ExperimentalMetricsCollector",
]
