"""
RAF Experiments Module.

Provides empirical validation experiments for the three acceleration loops.
"""

from .ansatz_design import AnsatzDesignExperiment, HardwareHeterogeneityStudy, NeuralSurrogate
from .bottleneck_validation import (
    BottleneckEffect,
    BottleneckScenario,
    BottleneckType,
    BottleneckValidationExperiment,
    ValidationResult,
)
from .control_optimization import (
    ControlOptimizationExperiment,
    ControlOptimizationMetrics,
    GateOptimizer,
    NoiseAwareCompiler,
    OptimizationResult,
    OptimizationStrategy,
)
from .cross_loop_validation import (
    CrossLoopEffect,
    CrossLoopValidationExperiment,
    IntegratedExperimentResult,
)
from .error_mitigation import ErrorMitigationExperiment
from .metrics_collector import ExperimentalMetricsCollector

__all__ = [
    "ErrorMitigationExperiment",
    "AnsatzDesignExperiment",
    "HardwareHeterogeneityStudy",
    "NeuralSurrogate",
    "ExperimentalMetricsCollector",
    "ControlOptimizationExperiment",
    "NoiseAwareCompiler",
    "GateOptimizer",
    "OptimizationResult",
    "OptimizationStrategy",
    "ControlOptimizationMetrics",
    "CrossLoopValidationExperiment",
    "CrossLoopEffect",
    "IntegratedExperimentResult",
    "BottleneckValidationExperiment",
    "BottleneckScenario",
    "BottleneckType",
    "BottleneckEffect",
    "ValidationResult",
]
