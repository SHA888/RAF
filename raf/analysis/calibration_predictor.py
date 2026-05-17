"""
ML-based calibration tracking and noise parameter prediction.

This module implements predictive models for quantum device calibration,
enabling proactive recalibration and drift compensation.

Key components:
- CalibrationPredictor: MLP/LSTM-based noise parameter prediction
- DriftTrajectoryGenerator: Synthetic training data generation
- RecalibrationScheduler: Optimal recalibration timing
"""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, cast

import numpy as np

from raf.backends.noise_models import DeviceNoiseProfile, DriftConfig, DriftingNoiseModel, DriftType


class PredictorType(Enum):
    """Types of prediction models."""

    MLP = "mlp"  # Multi-layer perceptron
    LSTM = "lstm"  # Long short-term memory
    LINEAR = "linear"  # Simple linear regression (baseline)


@dataclass
class PredictionResult:
    """Result from noise parameter prediction."""

    predicted_params: dict[str, float]
    confidence: float  # 0-1 confidence score
    prediction_horizon_hours: float
    model_type: PredictorType
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "predicted_params": self.predicted_params,
            "confidence": self.confidence,
            "prediction_horizon_hours": self.prediction_horizon_hours,
            "model_type": self.model_type.value,
            "metadata": self.metadata,
        }


@dataclass
class CalibrationMetrics:
    """Metrics for calibration prediction performance."""

    mae: float  # Mean absolute error
    rmse: float  # Root mean squared error
    mape: float  # Mean absolute percentage error
    prediction_accuracy: float  # Fraction within threshold
    recalibration_reduction: float  # Reduction in recalibration frequency
    samples_evaluated: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "mae": self.mae,
            "rmse": self.rmse,
            "mape": self.mape,
            "prediction_accuracy": self.prediction_accuracy,
            "recalibration_reduction": self.recalibration_reduction,
            "samples_evaluated": self.samples_evaluated,
        }


class DriftTrajectoryGenerator:
    """
    Generate synthetic drift trajectories for training ML models.

    Creates diverse training data by varying:
    - Drift types (linear, exponential, sinusoidal, etc.)
    - Drift rates
    - Initial conditions
    - Noise levels
    """

    def __init__(
        self,
        base_profiles: list[DeviceNoiseProfile] | None = None,
        random_seed: int | None = None,
    ):
        """
        Initialize trajectory generator.

        Args:
            base_profiles: List of base noise profiles to use
            random_seed: For reproducibility
        """
        self.base_profiles = base_profiles or [
            DeviceNoiseProfile.ibm_manila_like(),
            DeviceNoiseProfile.ibm_kolkata_like(),
            DeviceNoiseProfile.ionq_harmony_like(),
        ]
        self.rng = np.random.default_rng(random_seed)

    def generate_trajectory(
        self,
        duration_hours: float = 24.0,
        sample_interval_hours: float = 0.5,
        drift_type: DriftType | None = None,
        drift_rate: float | None = None,
        add_noise: bool = True,
        noise_level: float = 0.05,
    ) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
        """
        Generate a single drift trajectory.

        Args:
            duration_hours: Total duration of trajectory
            sample_interval_hours: Time between samples
            drift_type: Type of drift (random if None)
            drift_rate: Drift rate (random if None)
            add_noise: Whether to add measurement noise
            noise_level: Standard deviation of noise (relative)

        Returns:
            Tuple of (time_points, parameter_values, metadata)
            parameter_values shape: (n_samples, n_params)
        """
        # Select random drift type if not specified
        if drift_type is None:
            drift_type = random.choice(list(DriftType))

        # Select random drift rate if not specified
        if drift_rate is None:
            drift_rate = self.rng.uniform(0.05, 0.3)

        # Select random base profile
        base_profile = random.choice(self.base_profiles)

        # Create drift config
        drift_config = DriftConfig(
            drift_type=drift_type,
            drift_rate=drift_rate,
            amplitude=self.rng.uniform(0.3, 0.7),
            period_hours=self.rng.uniform(12.0, 48.0),
            random_seed=int(self.rng.integers(0, 10000)),
        )

        # Generate trajectory using DriftingNoiseModel
        drifting_model = DriftingNoiseModel(base_profile, drift_config)
        trajectory = drifting_model.generate_drift_trajectory(
            duration_hours=duration_hours,
            sample_interval_hours=sample_interval_hours,
        )

        # Extract time points and parameters
        time_points = np.array([t for t, _ in trajectory])
        n_samples = len(trajectory)

        # Extract key parameters as feature vector
        param_names = [
            "t1_us",
            "t2_us",
            "single_qubit_error",
            "two_qubit_error",
            "readout_error",
        ]
        parameter_values = np.zeros((n_samples, len(param_names)))

        for i, (_, profile) in enumerate(trajectory):
            parameter_values[i, 0] = profile.t1_us
            parameter_values[i, 1] = profile.t2_us
            parameter_values[i, 2] = profile.single_qubit_error
            parameter_values[i, 3] = profile.two_qubit_error
            parameter_values[i, 4] = profile.readout_error

        # Add measurement noise
        if add_noise:
            noise = self.rng.normal(0, noise_level, parameter_values.shape)
            # Relative noise
            parameter_values = parameter_values * (1 + noise)
            # Ensure non-negative
            parameter_values = np.maximum(parameter_values, 1e-10)

        metadata = {
            "drift_type": drift_type.value,
            "drift_rate": drift_rate,
            "base_profile": base_profile.name,
            "duration_hours": duration_hours,
            "sample_interval_hours": sample_interval_hours,
            "param_names": param_names,
            "noise_level": noise_level if add_noise else 0.0,
        }

        return time_points, parameter_values, metadata

    def generate_dataset(
        self,
        n_trajectories: int = 100,
        duration_hours: float = 24.0,
        sample_interval_hours: float = 0.5,
        lookback_steps: int = 10,
        forecast_steps: int = 5,
    ) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
        """
        Generate a dataset of trajectories for training.

        Creates input-output pairs where:
        - Input: lookback_steps of historical parameters
        - Output: forecast_steps of future parameters

        Args:
            n_trajectories: Number of trajectories to generate
            duration_hours: Duration of each trajectory
            sample_interval_hours: Sampling interval
            lookback_steps: Number of historical steps as input
            forecast_steps: Number of future steps to predict

        Returns:
            Tuple of (X, y, metadata_list)
            X shape: (n_samples, lookback_steps, n_params)
            y shape: (n_samples, forecast_steps, n_params)
        """
        X_list = []
        y_list = []
        metadata_list = []

        for _ in range(n_trajectories):
            # Generate trajectory
            times, params, meta = self.generate_trajectory(
                duration_hours=duration_hours,
                sample_interval_hours=sample_interval_hours,
            )

            n_samples = len(times)

            # Create sliding window samples
            for i in range(n_samples - lookback_steps - forecast_steps + 1):
                X_sample = params[i : i + lookback_steps]
                y_sample = params[i + lookback_steps : i + lookback_steps + forecast_steps]
                X_list.append(X_sample)
                y_list.append(y_sample)

            metadata_list.append(meta)

        X = np.array(X_list)
        y = np.array(y_list)

        return X, y, metadata_list


class CalibrationPredictor:
    """
    ML-based predictor for quantum device calibration parameters.

    Supports MLP and LSTM architectures for time-series prediction
    of noise parameters, enabling proactive recalibration.

    Example:
        >>> predictor = CalibrationPredictor(model_type=PredictorType.MLP)
        >>> generator = DriftTrajectoryGenerator(random_seed=42)
        >>> X, y, _ = generator.generate_dataset(n_trajectories=50)
        >>> predictor.train(X, y)
        >>> metrics = predictor.evaluate(X_test, y_test)
        >>> print(f"Prediction accuracy: {metrics.prediction_accuracy:.2%}")
    """

    def __init__(
        self,
        model_type: PredictorType = PredictorType.MLP,
        hidden_sizes: list[int] | None = None,
        learning_rate: float = 0.001,
        random_seed: int | None = None,
    ):
        """
        Initialize calibration predictor.

        Args:
            model_type: Type of model (MLP, LSTM, or LINEAR)
            hidden_sizes: Hidden layer sizes (default: [64, 32])
            learning_rate: Learning rate for training
            random_seed: For reproducibility
        """
        self.model_type = model_type
        self.hidden_sizes = hidden_sizes or [64, 32]
        self.learning_rate = learning_rate
        self.random_seed = random_seed
        self.rng = np.random.default_rng(random_seed)

        # Model parameters (initialized during training)
        self._weights: list[np.ndarray] = []
        self._biases: list[np.ndarray] = []
        self._is_trained = False

        # Training history
        self.training_history: list[float] = []

        # Input/output dimensions
        self._input_shape: tuple[int, ...] | None = None
        self._output_shape: tuple[int, ...] | None = None

        # Normalization parameters
        self._input_mean: np.ndarray | None = None
        self._input_std: np.ndarray | None = None
        self._output_mean: np.ndarray | None = None
        self._output_std: np.ndarray | None = None

    def _initialize_weights(self, input_dim: int, output_dim: int) -> None:
        """Initialize network weights using Xavier initialization."""
        self._weights = []
        self._biases = []

        layer_sizes = [input_dim] + self.hidden_sizes + [output_dim]

        for i in range(len(layer_sizes) - 1):
            fan_in = layer_sizes[i]
            fan_out = layer_sizes[i + 1]
            # Xavier initialization
            std = np.sqrt(2.0 / (fan_in + fan_out))
            W = self.rng.normal(0, std, (fan_in, fan_out))
            b = np.zeros(fan_out)
            self._weights.append(W)
            self._biases.append(b)

    def _relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation function."""
        return cast(np.ndarray, np.maximum(0, x))

    def _relu_derivative(self, x: np.ndarray) -> np.ndarray:
        """Derivative of ReLU."""
        return (x > 0).astype(float)

    def _forward(self, X: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
        """
        Forward pass through the network.

        Returns:
            Tuple of (output, list of activations for backprop)
        """
        activations = [X]
        current = X

        for i, (W, b) in enumerate(zip(self._weights, self._biases, strict=False)):
            z = current @ W + b
            # Hidden layers use ReLU; output layer is linear
            current = self._relu(z) if i < len(self._weights) - 1 else z
            activations.append(current)

        return current, activations

    def _backward(
        self,
        y_true: np.ndarray,
        activations: list[np.ndarray],
    ) -> tuple[list[np.ndarray], list[np.ndarray]]:
        """
        Backward pass to compute gradients.

        Returns:
            Tuple of (weight_gradients, bias_gradients)
        """
        batch_size = y_true.shape[0]
        n_layers = len(self._weights)

        weight_grads: list[np.ndarray | None] = [None] * n_layers
        bias_grads: list[np.ndarray | None] = [None] * n_layers

        # Output layer gradient (MSE loss)
        delta = (activations[-1] - y_true) / batch_size

        for i in range(n_layers - 1, -1, -1):
            # Gradient for weights and biases
            weight_grads[i] = activations[i].T @ delta
            bias_grads[i] = np.sum(delta, axis=0)

            if i > 0:
                # Propagate gradient through ReLU
                delta = (delta @ self._weights[i].T) * self._relu_derivative(activations[i])

        return [g for g in weight_grads if g is not None], [g for g in bias_grads if g is not None]

    def _normalize_input(self, X: np.ndarray) -> np.ndarray:
        """Normalize input data."""
        if self._input_mean is None:
            return X
        assert self._input_std is not None
        result = (X - self._input_mean) / (self._input_std + 1e-8)
        return cast(np.ndarray, result)

    def _normalize_output(self, y: np.ndarray) -> np.ndarray:
        """Normalize output data."""
        if self._output_mean is None:
            return y
        assert self._output_std is not None
        result = (y - self._output_mean) / (self._output_std + 1e-8)
        return cast(np.ndarray, result)

    def _denormalize_output(self, y: np.ndarray) -> np.ndarray:
        """Denormalize output data."""
        if self._output_mean is None:
            return y
        assert self._output_std is not None
        result = y * (self._output_std + 1e-8) + self._output_mean
        return cast(np.ndarray, result)

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32,
        validation_split: float = 0.1,
        verbose: bool = True,
    ) -> dict[str, list[float]]:
        """
        Train the predictor on drift trajectory data.

        Args:
            X: Input data, shape (n_samples, lookback_steps, n_params)
            y: Target data, shape (n_samples, forecast_steps, n_params)
            epochs: Number of training epochs
            batch_size: Mini-batch size
            validation_split: Fraction of data for validation
            verbose: Whether to print progress

        Returns:
            Training history with loss values
        """
        # Flatten input for MLP
        n_samples = X.shape[0]
        X_flat = X.reshape(n_samples, -1)
        y_flat = y.reshape(n_samples, -1)

        # Store shapes
        self._input_shape = X.shape[1:]
        self._output_shape = y.shape[1:]

        # Compute normalization parameters
        self._input_mean = np.mean(X_flat, axis=0)
        self._input_std = np.std(X_flat, axis=0)
        self._output_mean = np.mean(y_flat, axis=0)
        self._output_std = np.std(y_flat, axis=0)

        # Normalize data
        X_norm = self._normalize_input(X_flat)
        y_norm = self._normalize_output(y_flat)

        # Split into train/validation
        n_val = int(n_samples * validation_split)
        indices = self.rng.permutation(n_samples)
        train_idx = indices[n_val:]
        val_idx = indices[:n_val]

        X_train, y_train = X_norm[train_idx], y_norm[train_idx]
        X_val, y_val = X_norm[val_idx], y_norm[val_idx]

        # Initialize weights
        input_dim = X_flat.shape[1]
        output_dim = y_flat.shape[1]
        self._initialize_weights(input_dim, output_dim)

        # Training loop
        history: dict[str, list[float]] = {"train_loss": [], "val_loss": []}
        n_train = len(X_train)

        for epoch in range(epochs):
            # Shuffle training data
            perm = self.rng.permutation(n_train)
            X_train_shuffled = X_train[perm]
            y_train_shuffled = y_train[perm]

            epoch_loss = 0.0
            n_batches = 0

            # Mini-batch training
            for i in range(0, n_train, batch_size):
                X_batch = X_train_shuffled[i : i + batch_size]
                y_batch = y_train_shuffled[i : i + batch_size]

                # Forward pass
                y_pred, activations = self._forward(X_batch)

                # Compute loss
                batch_loss = np.mean((y_pred - y_batch) ** 2)
                epoch_loss += batch_loss
                n_batches += 1

                # Backward pass
                weight_grads, bias_grads = self._backward(y_batch, activations)

                # Update weights
                for j in range(len(self._weights)):
                    self._weights[j] -= self.learning_rate * weight_grads[j]
                    self._biases[j] -= self.learning_rate * bias_grads[j]

            # Compute validation loss
            y_val_pred, _ = self._forward(X_val)
            val_loss = np.mean((y_val_pred - y_val) ** 2)

            train_loss = epoch_loss / n_batches
            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)
            self.training_history.append(train_loss)

            if verbose and (epoch + 1) % 10 == 0:
                print(
                    f"Epoch {epoch + 1}/{epochs} - Loss: {train_loss:.6f} - Val Loss: {val_loss:.6f}"
                )

        self._is_trained = True
        return history

    def predict(
        self,
        X: np.ndarray,
        return_confidence: bool = True,
    ) -> tuple[np.ndarray, np.ndarray | None]:
        """
        Predict future noise parameters.

        Args:
            X: Input data, shape (n_samples, lookback_steps, n_params)
            return_confidence: Whether to return confidence scores

        Returns:
            Tuple of (predictions, confidence_scores)
            predictions shape: (n_samples, forecast_steps, n_params)
        """
        if not self._is_trained:
            raise RuntimeError("Model must be trained before prediction")

        # Flatten and normalize
        n_samples = X.shape[0]
        X_flat = X.reshape(n_samples, -1)
        X_norm = self._normalize_input(X_flat)

        # Forward pass
        y_pred_norm, _ = self._forward(X_norm)

        # Denormalize
        y_pred_flat = self._denormalize_output(y_pred_norm)

        # Reshape to original output shape
        assert self._output_shape is not None
        y_pred = y_pred_flat.reshape((n_samples, *self._output_shape))

        # Compute confidence based on prediction variance
        confidence = None
        if return_confidence and self._output_mean is not None:
            assert self._output_std is not None
            deviation = np.abs(y_pred_flat - self._output_mean) / (self._output_std + 1e-8)
            confidence = np.exp(-np.mean(deviation, axis=1))

        return y_pred, confidence

    def predict_single(
        self,
        history: np.ndarray,
        forecast_horizon_hours: float,
        sample_interval_hours: float = 0.5,
    ) -> PredictionResult:
        """
        Predict noise parameters for a single forecast.

        Args:
            history: Historical parameter values, shape (lookback_steps, n_params)
            forecast_horizon_hours: How far ahead to predict
            sample_interval_hours: Time interval between samples

        Returns:
            PredictionResult with predicted parameters
        """
        # Add batch dimension
        X = history[np.newaxis, ...]
        y_pred, confidence = self.predict(X, return_confidence=True)

        # Extract prediction for requested horizon
        forecast_steps = int(forecast_horizon_hours / sample_interval_hours)
        forecast_idx = min(forecast_steps - 1, y_pred.shape[1] - 1)

        param_names = ["t1_us", "t2_us", "single_qubit_error", "two_qubit_error", "readout_error"]
        predicted_params = {
            name: float(y_pred[0, forecast_idx, i]) for i, name in enumerate(param_names)
        }

        return PredictionResult(
            predicted_params=predicted_params,
            confidence=float(confidence[0]) if confidence is not None else 0.5,
            prediction_horizon_hours=forecast_horizon_hours,
            model_type=self.model_type,
            metadata={
                "forecast_steps": forecast_steps,
                "lookback_steps": history.shape[0],
            },
        )

    def evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        threshold: float = 0.1,
    ) -> CalibrationMetrics:
        """
        Evaluate prediction performance.

        Args:
            X: Input data
            y: True target values
            threshold: Relative error threshold for accuracy calculation

        Returns:
            CalibrationMetrics with performance measures
        """
        y_pred, _ = self.predict(X, return_confidence=False)

        # Flatten for metric computation
        y_true_flat = y.reshape(-1)
        y_pred_flat = y_pred.reshape(-1)

        # Compute metrics
        errors = y_pred_flat - y_true_flat
        abs_errors = np.abs(errors)
        rel_errors = abs_errors / (np.abs(y_true_flat) + 1e-10)

        mae = np.mean(abs_errors)
        rmse = np.sqrt(np.mean(errors**2))
        mape = np.mean(rel_errors) * 100

        # Prediction accuracy: fraction within threshold
        within_threshold = rel_errors < threshold
        prediction_accuracy = np.mean(within_threshold)

        # Estimate recalibration reduction
        # If we can predict drift, we need fewer reactive recalibrations
        # Simple heuristic: reduction proportional to prediction accuracy
        recalibration_reduction = prediction_accuracy * 0.5  # Up to 50% reduction

        return CalibrationMetrics(
            mae=float(mae),
            rmse=float(rmse),
            mape=float(mape),
            prediction_accuracy=float(prediction_accuracy),
            recalibration_reduction=float(recalibration_reduction),
            samples_evaluated=len(y_true_flat),
        )

    @property
    def is_trained(self) -> bool:
        """Check if model has been trained."""
        return self._is_trained


class RecalibrationScheduler:
    """
    Determines optimal recalibration timing based on predictions.

    Uses the CalibrationPredictor to forecast when device parameters
    will drift beyond acceptable thresholds, enabling proactive
    recalibration instead of reactive.
    """

    def __init__(
        self,
        predictor: CalibrationPredictor,
        error_threshold: float = 0.1,
        confidence_threshold: float = 0.7,
    ):
        """
        Initialize recalibration scheduler.

        Args:
            predictor: Trained CalibrationPredictor
            error_threshold: Maximum acceptable relative error
            confidence_threshold: Minimum confidence for scheduling
        """
        self.predictor = predictor
        self.error_threshold = error_threshold
        self.confidence_threshold = confidence_threshold

    def should_recalibrate(
        self,
        current_params: dict[str, float],
        predicted_params: dict[str, float],
        confidence: float,
    ) -> tuple[bool, str]:
        """
        Determine if recalibration is needed.

        Args:
            current_params: Current calibration parameters
            predicted_params: Predicted future parameters
            confidence: Prediction confidence

        Returns:
            Tuple of (should_recalibrate, reason)
        """
        if confidence < self.confidence_threshold:
            return False, "Low prediction confidence"

        # Check each parameter for drift beyond threshold
        for param_name in current_params:
            if param_name not in predicted_params:
                continue

            current = current_params[param_name]
            predicted = predicted_params[param_name]

            if current == 0:
                continue

            rel_change = abs(predicted - current) / abs(current)

            if rel_change > self.error_threshold:
                return True, f"{param_name} predicted to drift by {rel_change:.1%}"

        return False, "Parameters within acceptable range"

    def estimate_time_to_recalibration(
        self,
        history: np.ndarray,
        sample_interval_hours: float = 0.5,
        max_horizon_hours: float = 24.0,
    ) -> tuple[float, str]:
        """
        Estimate time until recalibration is needed.

        Args:
            history: Historical parameter values
            sample_interval_hours: Time interval between samples
            max_horizon_hours: Maximum prediction horizon

        Returns:
            Tuple of (hours_until_recalibration, limiting_parameter)
        """
        if not self.predictor.is_trained:
            return 0.0, "Model not trained"

        current_params = {
            "t1_us": history[-1, 0],
            "t2_us": history[-1, 1],
            "single_qubit_error": history[-1, 2],
            "two_qubit_error": history[-1, 3],
            "readout_error": history[-1, 4],
        }

        # Check at increasing horizons
        horizons = np.arange(sample_interval_hours, max_horizon_hours, sample_interval_hours)

        for horizon in horizons:
            result = self.predictor.predict_single(history, horizon, sample_interval_hours)

            should_recal, reason = self.should_recalibrate(
                current_params, result.predicted_params, result.confidence
            )

            if should_recal:
                return float(horizon), reason

        return float(max_horizon_hours), "No recalibration needed within horizon"
