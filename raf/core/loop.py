"""
Base acceleration loop definition for the Reciprocal Acceleration Framework.

An acceleration loop is a closed feedback cycle where advances in one domain
(QC or ML) produce outputs that enable accelerated progress in the other domain,
which then feeds back to further advance the first.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
import numpy as np

from raf.core.metrics import (
    AccelerationMetric,
    BottleneckIndicator,
    BottleneckSeverity,
    ProgressMetric,
)


class LoopLevel(Enum):
    """The level of the QC-ML stack where the loop operates."""
    APPLICATION = "application"  # Output/application level
    ALGORITHM = "algorithm"      # Algorithm/circuit level
    HARDWARE = "hardware"        # Hardware/physics level


class LoopStatus(Enum):
    """Current operational status of a loop."""
    INACTIVE = "inactive"        # Not yet started
    INITIALIZING = "initializing"  # Setting up
    ACTIVE = "active"            # Running normally
    ACCELERATING = "accelerating"  # Positive feedback observed
    BOTTLENECKED = "bottlenecked"  # Limited by constraints
    SATURATING = "saturating"    # Approaching limits
    CONVERGED = "converged"      # Reached stable state


@dataclass
class LoopState:
    """
    Represents the current state of an acceleration loop.
    
    Attributes:
        iteration: Current iteration number
        status: Current operational status
        acceleration_rate: Current acceleration (>1 = positive feedback)
        efficiency: How efficiently the loop is operating (0-1)
        data_volume: Amount of data flowing through the loop
        last_update: When the state was last updated
        metrics: Dictionary of current metric values
    """
    iteration: int = 0
    status: LoopStatus = LoopStatus.INACTIVE
    acceleration_rate: float = 1.0
    efficiency: float = 0.0
    data_volume: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def update(self, **kwargs):
        """Update state with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_update = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "iteration": self.iteration,
            "status": self.status.value,
            "acceleration_rate": self.acceleration_rate,
            "efficiency": self.efficiency,
            "data_volume": self.data_volume,
            "last_update": self.last_update.isoformat(),
            "metrics": self.metrics,
        }


@dataclass
class LoopMetrics:
    """
    Collection of metrics for an acceleration loop.
    
    Attributes:
        acceleration_history: Historical acceleration values
        bottlenecks: Currently identified bottlenecks
        progress: Progress metrics for this loop
        iteration_times: Time taken for each iteration
    """
    acceleration_history: List[AccelerationMetric] = field(default_factory=list)
    bottlenecks: List[BottleneckIndicator] = field(default_factory=list)
    progress: Dict[str, ProgressMetric] = field(default_factory=dict)
    iteration_times: List[float] = field(default_factory=list)
    
    def add_acceleration(self, metric: AccelerationMetric):
        """Record an acceleration measurement."""
        self.acceleration_history.append(metric)
    
    def add_bottleneck(self, bottleneck: BottleneckIndicator):
        """Add or update a bottleneck."""
        # Replace if same name exists
        self.bottlenecks = [b for b in self.bottlenecks if b.name != bottleneck.name]
        self.bottlenecks.append(bottleneck)
    
    def get_active_bottlenecks(self) -> List[BottleneckIndicator]:
        """Get currently active bottlenecks."""
        return [b for b in self.bottlenecks if b.is_active]
    
    def get_acceleration_trend(self, window: int = 5) -> Optional[float]:
        """Calculate acceleration trend over recent iterations."""
        if len(self.acceleration_history) < 2:
            return None
        recent = self.acceleration_history[-window:]
        values = [m.acceleration_ratio for m in recent]
        if len(values) < 2:
            return None
        x = np.arange(len(values))
        return float(np.polyfit(x, values, 1)[0])
    
    def summary(self) -> Dict[str, Any]:
        """Generate metrics summary."""
        return {
            "total_iterations": len(self.acceleration_history),
            "current_acceleration": (
                self.acceleration_history[-1].acceleration_ratio 
                if self.acceleration_history else 1.0
            ),
            "acceleration_trend": self.get_acceleration_trend(),
            "active_bottlenecks": len(self.get_active_bottlenecks()),
            "progress_domains": list(self.progress.keys()),
        }


class AccelerationLoop(ABC):
    """
    Abstract base class for acceleration loops in the RAF.
    
    An acceleration loop represents a closed feedback cycle where:
    1. Advances in one domain (QC or ML) produce outputs/capabilities
    2. These outputs serve as inputs/enablers for the other domain
    3. Resulting advances feed back to further advance the first domain
    
    Subclasses implement specific loops:
    - ErrorMitigationLoop: Output/application level
    - AnsatzDesignLoop: Algorithm/circuit level
    - CalibrationControlLoop: Hardware/physics level
    """
    
    def __init__(
        self,
        name: str,
        level: LoopLevel,
        description: str = "",
    ):
        """
        Initialize an acceleration loop.
        
        Args:
            name: Unique identifier for this loop
            level: Which level of the stack this operates at
            description: Human-readable description
        """
        self.name = name
        self.level = level
        self.description = description
        self.state = LoopState()
        self.metrics = LoopMetrics()
        self._callbacks: Dict[str, List[Callable]] = {
            "on_iteration": [],
            "on_acceleration": [],
            "on_bottleneck": [],
        }
    
    @property
    @abstractmethod
    def stages(self) -> List[str]:
        """
        The stages of this acceleration loop.
        
        Returns a list of stage names that describe the feedback cycle.
        Example for Error Mitigation Loop:
        ["ml_qem", "cleaner_outputs", "larger_experiments", 
         "more_training_data", "improved_models"]
        """
        pass
    
    @property
    @abstractmethod
    def bottleneck_types(self) -> List[str]:
        """
        Types of bottlenecks that can affect this loop.
        
        Returns a list of bottleneck category names specific to this loop.
        """
        pass
    
    @abstractmethod
    def compute_acceleration(self) -> AccelerationMetric:
        """
        Compute the current acceleration rate for this loop.
        
        Returns:
            AccelerationMetric with current acceleration measurement
        """
        pass
    
    @abstractmethod
    def identify_bottlenecks(self) -> List[BottleneckIndicator]:
        """
        Identify current bottlenecks limiting this loop.
        
        Returns:
            List of BottleneckIndicator objects for active constraints
        """
        pass
    
    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """
        Generate recommendations for accelerating this loop.
        
        Returns:
            List of actionable recommendations
        """
        pass
    
    def iterate(self) -> LoopState:
        """
        Execute one iteration of the loop.
        
        This updates the loop state, computes new metrics,
        and triggers any registered callbacks.
        
        Returns:
            Updated LoopState
        """
        start_time = datetime.now()
        
        # Increment iteration
        self.state.iteration += 1
        
        # Compute acceleration
        acceleration = self.compute_acceleration()
        self.metrics.add_acceleration(acceleration)
        self.state.acceleration_rate = acceleration.acceleration_ratio
        
        # Identify bottlenecks
        bottlenecks = self.identify_bottlenecks()
        for b in bottlenecks:
            self.metrics.add_bottleneck(b)
        
        # Update status based on state
        self._update_status()
        
        # Record iteration time
        elapsed = (datetime.now() - start_time).total_seconds()
        self.metrics.iteration_times.append(elapsed)
        
        # Trigger callbacks
        self._trigger_callbacks("on_iteration", self.state)
        if acceleration.is_accelerating:
            self._trigger_callbacks("on_acceleration", acceleration)
        for b in bottlenecks:
            if b.is_active:
                self._trigger_callbacks("on_bottleneck", b)
        
        return self.state
    
    def _update_status(self):
        """Update loop status based on current state."""
        active_bottlenecks = self.metrics.get_active_bottlenecks()
        acceleration_trend = self.metrics.get_acceleration_trend()
        
        if self.state.iteration == 0:
            self.state.status = LoopStatus.INACTIVE
        elif self.state.iteration < 3:
            self.state.status = LoopStatus.INITIALIZING
        elif any(b.severity == BottleneckSeverity.CRITICAL for b in active_bottlenecks):
            self.state.status = LoopStatus.BOTTLENECKED
        elif acceleration_trend is not None and acceleration_trend < -0.1:
            self.state.status = LoopStatus.SATURATING
        elif self.state.acceleration_rate > 1.1:
            self.state.status = LoopStatus.ACCELERATING
        else:
            self.state.status = LoopStatus.ACTIVE
    
    def register_callback(self, event: str, callback: Callable):
        """
        Register a callback for loop events.
        
        Args:
            event: Event name ("on_iteration", "on_acceleration", "on_bottleneck")
            callback: Function to call when event occurs
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, data: Any):
        """Trigger all callbacks for an event."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Callback error in {self.name}.{event}: {e}")
    
    def reset(self):
        """Reset the loop to initial state."""
        self.state = LoopState()
        self.metrics = LoopMetrics()
    
    def summary(self) -> Dict[str, Any]:
        """Generate a summary of the loop's current state."""
        return {
            "name": self.name,
            "level": self.level.value,
            "description": self.description,
            "stages": self.stages,
            "state": self.state.to_dict(),
            "metrics": self.metrics.summary(),
            "recommendations": self.get_recommendations(),
        }
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"level={self.level.value}, "
            f"status={self.state.status.value}, "
            f"iteration={self.state.iteration})"
        )
