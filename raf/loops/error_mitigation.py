"""
Error Mitigation Loop implementation.

This loop operates at the output/application level:

ML-QEM → Cleaner Outputs → Larger QML Experiments → More Training Data → Improved ML-QEM

The loop accelerates because data quantity and quality compound. Better error
mitigation increases the effective "quantum volume" accessible for computation,
which increases both the diversity and reliability of training data for
next-generation mitigation models.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

from raf.core.loop import AccelerationLoop, LoopLevel, LoopState
from raf.core.metrics import (
    AccelerationMetric,
    BottleneckIndicator,
    BottleneckSeverity,
    ProgressMetric,
)


@dataclass
class ErrorMitigationState:
    """
    State specific to the Error Mitigation Loop.
    
    Attributes:
        mitigation_accuracy: Current accuracy of ML-QEM models (0-1)
        output_fidelity: Fidelity of mitigated quantum outputs (0-1)
        experiment_scale: Scale of QML experiments (qubits × depth)
        training_data_volume: Amount of training data (samples)
        calibration_cost: Cost of generating calibration data (relative)
    """
    mitigation_accuracy: float = 0.5
    output_fidelity: float = 0.5
    experiment_scale: float = 10.0  # qubits × depth
    training_data_volume: float = 1000.0
    calibration_cost: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mitigation_accuracy": self.mitigation_accuracy,
            "output_fidelity": self.output_fidelity,
            "experiment_scale": self.experiment_scale,
            "training_data_volume": self.training_data_volume,
            "calibration_cost": self.calibration_cost,
        }


class ErrorMitigationLoop(AccelerationLoop):
    """
    Error Mitigation Loop - Operating at the output/application level.
    
    This loop captures the feedback cycle where:
    1. ML-based error mitigation (ML-QEM) produces cleaner quantum outputs
    2. Cleaner outputs enable larger-scale QML experiments
    3. Larger experiments generate more training data
    4. More training data improves ML-QEM models
    5. Improved mitigation enables yet larger experiments
    
    Bottlenecks:
    - Calibration data acquisition cost
    - Generalization limits across devices/drift conditions
    - Diminishing returns as mitigation approaches fundamental limits
    
    Example:
        >>> loop = ErrorMitigationLoop()
        >>> loop.set_mitigation_accuracy(0.7)
        >>> loop.set_experiment_scale(50)
        >>> state = loop.iterate()
        >>> print(state.acceleration_rate)
    """
    
    # Loop stage definitions
    STAGES = [
        "ml_qem",              # ML-based error mitigation
        "cleaner_outputs",     # Improved quantum outputs
        "larger_experiments",  # Larger-scale QML experiments
        "more_training_data",  # Increased training data
        "improved_models",     # Better ML-QEM models
    ]
    
    # Bottleneck type definitions
    BOTTLENECK_TYPES = [
        "calibration_cost",      # Cost of generating ground-truth labels
        "generalization",        # Transfer across devices/conditions
        "diminishing_returns",   # Approaching fundamental limits
        "data_quality",          # Quality vs quantity tradeoff
    ]
    
    def __init__(
        self,
        name: str = "error_mitigation",
        initial_accuracy: float = 0.5,
        initial_scale: float = 10.0,
    ):
        """
        Initialize the Error Mitigation Loop.
        
        Args:
            name: Identifier for this loop instance
            initial_accuracy: Starting mitigation accuracy (0-1)
            initial_scale: Starting experiment scale (qubits × depth)
        """
        super().__init__(
            name=name,
            level=LoopLevel.APPLICATION,
            description="ML-based error mitigation feedback loop at the application level",
        )
        
        self.em_state = ErrorMitigationState(
            mitigation_accuracy=initial_accuracy,
            experiment_scale=initial_scale,
        )
        
        # Initialize progress metrics
        self.metrics.progress["mitigation_accuracy"] = ProgressMetric(
            domain="mitigation_accuracy",
            current_value=initial_accuracy,
            target_value=0.99,
            direction="higher",
        )
        self.metrics.progress["experiment_scale"] = ProgressMetric(
            domain="experiment_scale",
            current_value=initial_scale,
            target_value=1000.0,  # Target: 1000 qubit-depth product
            unit="qubit-depth",
            direction="higher",
        )
    
    @property
    def stages(self) -> List[str]:
        return self.STAGES
    
    @property
    def bottleneck_types(self) -> List[str]:
        return self.BOTTLENECK_TYPES
    
    def set_mitigation_accuracy(self, accuracy: float):
        """Set the current mitigation accuracy."""
        self.em_state.mitigation_accuracy = np.clip(accuracy, 0.0, 1.0)
        self.metrics.progress["mitigation_accuracy"].record(accuracy)
    
    def set_output_fidelity(self, fidelity: float):
        """Set the current output fidelity."""
        self.em_state.output_fidelity = np.clip(fidelity, 0.0, 1.0)
    
    def set_experiment_scale(self, scale: float):
        """Set the current experiment scale."""
        self.em_state.experiment_scale = max(1.0, scale)
        self.metrics.progress["experiment_scale"].record(scale)
    
    def set_training_data_volume(self, volume: float):
        """Set the current training data volume."""
        self.em_state.training_data_volume = max(0.0, volume)
    
    def set_calibration_cost(self, cost: float):
        """Set the current calibration cost."""
        self.em_state.calibration_cost = max(0.1, cost)
    
    def compute_acceleration(self) -> AccelerationMetric:
        """
        Compute the current acceleration rate.
        
        Acceleration is computed based on:
        - Improvement in mitigation accuracy
        - Growth in experiment scale
        - Growth in training data volume
        - Reduction in calibration cost
        """
        # Get historical values if available
        accuracy_history = self.metrics.progress["mitigation_accuracy"].history
        scale_history = self.metrics.progress["experiment_scale"].history
        
        # Compute acceleration components
        accuracy_factor = 1.0
        if len(accuracy_history) >= 2:
            prev_acc = accuracy_history[-2][1]
            curr_acc = self.em_state.mitigation_accuracy
            if prev_acc > 0:
                accuracy_factor = curr_acc / prev_acc
        
        scale_factor = 1.0
        if len(scale_history) >= 2:
            prev_scale = scale_history[-2][1]
            curr_scale = self.em_state.experiment_scale
            if prev_scale > 0:
                scale_factor = curr_scale / prev_scale
        
        # Data flywheel effect: more data → better models → more accessible experiments
        data_factor = np.log1p(self.em_state.training_data_volume) / 10.0
        
        # Cost efficiency factor
        cost_factor = 1.0 / self.em_state.calibration_cost
        
        # Combined acceleration (geometric mean of factors)
        acceleration = (accuracy_factor * scale_factor * (1 + data_factor) * cost_factor) ** 0.25
        
        return AccelerationMetric(
            name=f"{self.name}_acceleration",
            value=acceleration,
            baseline=1.0,
            iteration=self.state.iteration,
            metadata={
                "accuracy_factor": accuracy_factor,
                "scale_factor": scale_factor,
                "data_factor": data_factor,
                "cost_factor": cost_factor,
            },
        )
    
    def identify_bottlenecks(self) -> List[BottleneckIndicator]:
        """
        Identify current bottlenecks in the loop.
        
        Checks for:
        1. High calibration data acquisition cost
        2. Poor generalization (accuracy vs scale mismatch)
        3. Diminishing returns (high accuracy but slow improvement)
        4. Data quality issues
        """
        bottlenecks = []
        
        # Bottleneck 1: Calibration cost
        if self.em_state.calibration_cost > 2.0:
            severity = BottleneckSeverity.HIGH if self.em_state.calibration_cost > 5.0 else BottleneckSeverity.MEDIUM
            bottlenecks.append(BottleneckIndicator(
                name="high_calibration_cost",
                description="Generating ground-truth labels for ML-QEM training is expensive",
                severity=severity,
                loop_name=self.name,
                constraint_type="data",
                current_value=self.em_state.calibration_cost,
                threshold=2.0,
                addressability_score=0.6,
                recommended_actions=[
                    "Develop efficient classical simulation methods for calibration",
                    "Use transfer learning to reduce calibration data requirements",
                    "Implement active learning to select most informative calibration points",
                ],
            ))
        
        # Bottleneck 2: Generalization limits
        # If accuracy is high but scale is low, generalization may be limiting
        accuracy_scale_ratio = self.em_state.mitigation_accuracy / (self.em_state.experiment_scale / 100)
        if accuracy_scale_ratio > 2.0 and self.em_state.experiment_scale < 100:
            bottlenecks.append(BottleneckIndicator(
                name="generalization_limit",
                description="ML-QEM models may not generalize to larger scales or different conditions",
                severity=BottleneckSeverity.MEDIUM,
                loop_name=self.name,
                constraint_type="model",
                current_value=accuracy_scale_ratio,
                threshold=2.0,
                addressability_score=0.5,
                recommended_actions=[
                    "Train on diverse noise instances and device configurations",
                    "Develop physics-informed ML architectures",
                    "Implement domain adaptation techniques",
                ],
            ))
        
        # Bottleneck 3: Diminishing returns
        accuracy_trend = self.metrics.progress["mitigation_accuracy"].trend
        if self.em_state.mitigation_accuracy > 0.9 and accuracy_trend is not None and accuracy_trend < 0.01:
            bottlenecks.append(BottleneckIndicator(
                name="diminishing_returns",
                description="Approaching fundamental limits of error mitigation",
                severity=BottleneckSeverity.LOW,
                loop_name=self.name,
                constraint_type="knowledge",
                current_value=self.em_state.mitigation_accuracy,
                threshold=0.9,
                addressability_score=0.3,
                recommended_actions=[
                    "Shift focus to error correction rather than mitigation",
                    "Explore hybrid mitigation-correction approaches",
                    "Accept current accuracy and optimize for efficiency",
                ],
            ))
        
        # Bottleneck 4: Data quality
        data_quality_estimate = min(1.0, self.em_state.output_fidelity * 1.2)
        if data_quality_estimate < 0.6:
            bottlenecks.append(BottleneckIndicator(
                name="data_quality",
                description="Low output fidelity limits quality of training data",
                severity=BottleneckSeverity.HIGH,
                loop_name=self.name,
                constraint_type="data",
                current_value=data_quality_estimate,
                threshold=0.6,
                addressability_score=0.7,
                recommended_actions=[
                    "Improve base hardware fidelity before scaling experiments",
                    "Implement data filtering and quality scoring",
                    "Use ensemble methods to identify reliable data points",
                ],
            ))
        
        return bottlenecks
    
    def get_recommendations(self) -> List[str]:
        """Generate recommendations for accelerating this loop."""
        recommendations = []
        
        # Based on current state
        if self.em_state.mitigation_accuracy < 0.7:
            recommendations.append(
                "Focus on improving base ML-QEM model architecture and training"
            )
        
        if self.em_state.experiment_scale < 50:
            recommendations.append(
                "Gradually increase experiment scale to generate diverse training data"
            )
        
        if self.em_state.training_data_volume < 10000:
            recommendations.append(
                "Prioritize data collection to enable data-driven improvements"
            )
        
        if self.em_state.calibration_cost > 2.0:
            recommendations.append(
                "Invest in reducing calibration cost through efficient simulation or transfer learning"
            )
        
        # Based on loop dynamics
        if self.state.status.value == "accelerating":
            recommendations.append(
                "Maintain current trajectory; consider scaling up experiments"
            )
        elif self.state.status.value == "bottlenecked":
            recommendations.append(
                "Address identified bottlenecks before attempting to scale"
            )
        
        return recommendations
    
    def simulate_iteration(
        self,
        accuracy_improvement: float = 0.02,
        scale_growth: float = 1.1,
        data_growth: float = 1.2,
    ) -> LoopState:
        """
        Simulate one iteration with specified growth rates.
        
        This is useful for modeling and prediction.
        
        Args:
            accuracy_improvement: Additive improvement in accuracy
            scale_growth: Multiplicative growth in experiment scale
            data_growth: Multiplicative growth in training data
            
        Returns:
            Updated loop state
        """
        # Apply improvements
        new_accuracy = min(0.99, self.em_state.mitigation_accuracy + accuracy_improvement)
        new_scale = self.em_state.experiment_scale * scale_growth
        new_data = self.em_state.training_data_volume * data_growth
        
        # Update state
        self.set_mitigation_accuracy(new_accuracy)
        self.set_experiment_scale(new_scale)
        self.set_training_data_volume(new_data)
        
        # Compute output fidelity based on accuracy
        self.set_output_fidelity(new_accuracy * 0.95)
        
        # Run iteration
        return self.iterate()
    
    def summary(self) -> Dict[str, Any]:
        """Generate a summary including error mitigation-specific state."""
        base_summary = super().summary()
        base_summary["em_state"] = self.em_state.to_dict()
        return base_summary
