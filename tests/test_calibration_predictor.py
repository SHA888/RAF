"""Tests for calibration prediction and recalibration scheduling."""

import numpy as np
import pytest

from raf.analysis.calibration_predictor import (
    CalibrationMetrics,
    CalibrationPredictor,
    DriftTrajectoryGenerator,
    PredictionResult,
    PredictorType,
    RecalibrationScheduler,
)
from raf.backends.noise_models import DeviceNoiseProfile, DriftType


class TestPredictionResult:
    """Tests for PredictionResult dataclass."""

    def test_prediction_result_creation(self) -> None:
        """Test creating a PredictionResult."""
        result = PredictionResult(
            predicted_params={"t1_us": 50.0, "t2_us": 100.0},
            confidence=0.85,
            prediction_horizon_hours=2.0,
            model_type=PredictorType.MLP,
        )
        assert result.confidence == 0.85
        assert result.predicted_params["t1_us"] == 50.0

    def test_prediction_result_to_dict(self) -> None:
        """Test PredictionResult serialization."""
        result = PredictionResult(
            predicted_params={"t1_us": 50.0},
            confidence=0.9,
            prediction_horizon_hours=1.0,
            model_type=PredictorType.LINEAR,
        )
        d = result.to_dict()
        assert d["confidence"] == 0.9
        assert d["model_type"] == "linear"
        assert "metadata" in d


class TestCalibrationMetrics:
    """Tests for CalibrationMetrics dataclass."""

    def test_calibration_metrics_creation(self) -> None:
        """Test creating CalibrationMetrics."""
        metrics = CalibrationMetrics(
            mae=0.05,
            rmse=0.08,
            mape=5.0,
            prediction_accuracy=0.9,
            recalibration_reduction=0.2,
            samples_evaluated=100,
        )
        assert metrics.mae == 0.05
        assert metrics.samples_evaluated == 100

    def test_calibration_metrics_to_dict(self) -> None:
        """Test CalibrationMetrics serialization."""
        metrics = CalibrationMetrics(
            mae=0.1,
            rmse=0.15,
            mape=10.0,
            prediction_accuracy=0.8,
            recalibration_reduction=0.25,
        )
        d = metrics.to_dict()
        assert d["mae"] == 0.1
        assert d["rmse"] == 0.15
        assert "samples_evaluated" in d


class TestDriftTrajectoryGenerator:
    """Tests for DriftTrajectoryGenerator."""

    def test_generator_creation(self) -> None:
        """Test creating a DriftTrajectoryGenerator."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        assert gen.base_profiles is not None
        assert len(gen.base_profiles) >= 3

    def test_generator_with_custom_profiles(self) -> None:
        """Test generator with custom base profiles."""
        profiles = [DeviceNoiseProfile.ionq_harmony_like()]
        gen = DriftTrajectoryGenerator(base_profiles=profiles)
        assert gen.base_profiles == profiles

    def test_generate_trajectory_linear_drift(self) -> None:
        """Test trajectory generation with linear drift."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        times, params, metadata = gen.generate_trajectory(
            duration_hours=4.0,
            sample_interval_hours=1.0,
            drift_type=DriftType.LINEAR,
            drift_rate=0.1,
            add_noise=False,
        )
        assert len(times) > 0
        assert params.shape[0] == len(times)
        assert params.shape[1] == 5  # 5 parameters
        assert metadata["drift_type"] == "linear"
        assert metadata["drift_rate"] == 0.1

    def test_generate_trajectory_exponential_drift(self) -> None:
        """Test trajectory generation with exponential drift."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        times, params, metadata = gen.generate_trajectory(
            duration_hours=2.0,
            sample_interval_hours=0.5,
            drift_type=DriftType.EXPONENTIAL,
            drift_rate=0.15,
        )
        assert metadata["drift_type"] == "exponential"
        assert params.shape[0] > 0

    def test_generate_trajectory_with_noise(self) -> None:
        """Test trajectory generation with measurement noise."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        times, params, metadata = gen.generate_trajectory(
            duration_hours=2.0,
            sample_interval_hours=0.5,
            add_noise=True,
            noise_level=0.1,
        )
        assert metadata["noise_level"] == 0.1
        assert np.all(params >= 0)  # Ensure non-negative after noise

    def test_generate_trajectory_without_noise(self) -> None:
        """Test trajectory generation without noise."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        times, params, metadata = gen.generate_trajectory(
            duration_hours=2.0,
            sample_interval_hours=0.5,
            add_noise=False,
        )
        assert metadata["noise_level"] == 0.0

    def test_generate_dataset(self) -> None:
        """Test dataset generation for training."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, metadata_list = gen.generate_dataset(
            n_trajectories=5,
            duration_hours=8.0,
            sample_interval_hours=0.5,
            lookback_steps=4,
            forecast_steps=2,
        )
        assert X.shape[0] > 0  # At least some samples
        assert X.shape[1] == 4  # lookback_steps
        assert X.shape[2] == 5  # 5 parameters
        assert y.shape[0] == X.shape[0]
        assert y.shape[1] == 2  # forecast_steps
        assert len(metadata_list) == 5

    def test_generate_dataset_deterministic(self) -> None:
        """Test that same seed produces same dataset."""
        gen1 = DriftTrajectoryGenerator(random_seed=42)
        X1, y1, _ = gen1.generate_dataset(n_trajectories=3, duration_hours=1.0)

        gen2 = DriftTrajectoryGenerator(random_seed=42)
        X2, y2, _ = gen2.generate_dataset(n_trajectories=3, duration_hours=1.0)

        np.testing.assert_array_almost_equal(X1, X2)
        np.testing.assert_array_almost_equal(y1, y2)


class TestCalibrationPredictor:
    """Tests for CalibrationPredictor."""

    def test_predictor_creation_mlp(self) -> None:
        """Test creating an MLP CalibrationPredictor."""
        pred = CalibrationPredictor(
            model_type=PredictorType.MLP,
            hidden_sizes=[32, 16],
            learning_rate=0.01,
            random_seed=42,
        )
        assert pred.model_type == PredictorType.MLP
        assert pred.hidden_sizes == [32, 16]
        assert not pred.is_trained

    def test_predictor_creation_linear(self) -> None:
        """Test creating a LINEAR CalibrationPredictor."""
        pred = CalibrationPredictor(model_type=PredictorType.LINEAR, random_seed=42)
        assert pred.model_type == PredictorType.LINEAR

    def test_predictor_creation_lstm(self) -> None:
        """Test creating an LSTM CalibrationPredictor."""
        pred = CalibrationPredictor(model_type=PredictorType.LSTM, random_seed=42)
        assert pred.model_type == PredictorType.LSTM

    def test_predict_before_training_raises(self) -> None:
        """Test that predicting before training raises RuntimeError."""
        pred = CalibrationPredictor(random_seed=42)
        X = np.random.randn(10, 4, 5)
        with pytest.raises(RuntimeError, match="must be trained"):
            pred.predict(X)

    def test_train_and_predict(self) -> None:
        """Test training and prediction."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(
            n_trajectories=10,
            duration_hours=8.0,
            sample_interval_hours=0.5,
            lookback_steps=4,
            forecast_steps=3,
        )

        pred = CalibrationPredictor(
            model_type=PredictorType.MLP,
            hidden_sizes=[16],
            random_seed=42,
        )
        history = pred.train(X, y, epochs=5, verbose=False)

        assert pred.is_trained
        assert "train_loss" in history
        assert "val_loss" in history
        assert len(history["train_loss"]) == 5

        # Test prediction
        y_pred, confidence = pred.predict(X[:5], return_confidence=True)
        assert y_pred.shape == (5, 3, 5)  # 5 samples, 3 steps, 5 params
        assert confidence is not None
        assert confidence.shape == (5,)

    def test_predict_without_confidence(self) -> None:
        """Test prediction without confidence scores."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=5, lookback_steps=4, forecast_steps=2)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=3, verbose=False)

        y_pred, confidence = pred.predict(X[:2], return_confidence=False)
        assert y_pred.shape == (2, 2, 5)
        assert confidence is None

    def test_predict_single(self) -> None:
        """Test single prediction."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=10, lookback_steps=5, forecast_steps=3)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=3, verbose=False)

        history = X[0]  # (5, 5) - 5 steps of 5 parameters
        result = pred.predict_single(history, forecast_horizon_hours=1.5, sample_interval_hours=0.5)

        assert isinstance(result, PredictionResult)
        assert "t1_us" in result.predicted_params
        assert result.prediction_horizon_hours == 1.5
        assert 0.0 <= result.confidence <= 1.0

    def test_evaluate(self) -> None:
        """Test model evaluation."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=10, lookback_steps=4, forecast_steps=2)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=5, verbose=False)

        metrics = pred.evaluate(X, y, threshold=0.15)

        assert isinstance(metrics, CalibrationMetrics)
        assert metrics.mae >= 0.0
        assert metrics.rmse >= metrics.mae
        assert 0.0 <= metrics.prediction_accuracy <= 1.0
        assert metrics.samples_evaluated > 0

    def test_training_history(self) -> None:
        """Test training history is recorded."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=5, lookback_steps=4, forecast_steps=2)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=10, verbose=False)

        assert len(pred.training_history) == 10
        # Loss should generally decrease over epochs
        assert pred.training_history[-1] < pred.training_history[0]

    def test_normalization(self) -> None:
        """Test input/output normalization."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=8, lookback_steps=4, forecast_steps=2)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=3, verbose=False)

        # Check that normalization parameters are set
        assert pred._input_mean is not None
        assert pred._input_std is not None
        assert pred._output_mean is not None
        assert pred._output_std is not None

    def test_initialize_weights(self) -> None:
        """Test weight initialization."""
        pred = CalibrationPredictor(hidden_sizes=[32, 16], random_seed=42)
        pred._initialize_weights(input_dim=20, output_dim=10)

        assert len(pred._weights) == 3  # [20->32, 32->16, 16->10]
        assert len(pred._biases) == 3
        assert pred._weights[0].shape == (20, 32)
        assert pred._biases[-1].shape == (10,)

    def test_forward_pass(self) -> None:
        """Test forward pass through network."""
        pred = CalibrationPredictor(hidden_sizes=[16], random_seed=42)
        pred._initialize_weights(input_dim=10, output_dim=5)

        X = np.random.randn(3, 10)
        output, activations = pred._forward(X)

        assert output.shape == (3, 5)
        assert len(activations) == 3  # input + 2 layers

    def test_relu_activation(self) -> None:
        """Test ReLU activation function."""
        pred = CalibrationPredictor()
        x = np.array([[-1.0, 0.0, 1.0, 2.0]])
        result = pred._relu(x)
        np.testing.assert_array_equal(result, [[0.0, 0.0, 1.0, 2.0]])

    def test_batch_training(self) -> None:
        """Test training with different batch sizes."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=10, lookback_steps=4, forecast_steps=2)

        pred = CalibrationPredictor(random_seed=42)
        history = pred.train(X, y, epochs=3, batch_size=8, verbose=False)

        assert len(history["train_loss"]) == 3
        assert len(history["val_loss"]) == 3


class TestRecalibrationScheduler:
    """Tests for RecalibrationScheduler."""

    def test_scheduler_creation(self) -> None:
        """Test creating a RecalibrationScheduler."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=5, lookback_steps=4, forecast_steps=2)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=3, verbose=False)

        scheduler = RecalibrationScheduler(predictor=pred, error_threshold=0.15)
        assert scheduler.error_threshold == 0.15
        assert scheduler.confidence_threshold == 0.7

    def test_should_recalibrate_low_confidence(self) -> None:
        """Test that low confidence results in no recalibration."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=5, lookback_steps=4, forecast_steps=2)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=3, verbose=False)

        scheduler = RecalibrationScheduler(
            predictor=pred,
            error_threshold=0.1,
            confidence_threshold=0.8,
        )

        current = {"t1_us": 50.0, "t2_us": 100.0}
        predicted = {"t1_us": 50.5, "t2_us": 100.5}

        should_recal, reason = scheduler.should_recalibrate(current, predicted, confidence=0.5)
        assert not should_recal
        assert "confidence" in reason.lower()

    def test_should_recalibrate_drift_detected(self) -> None:
        """Test that large drift triggers recalibration."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=5, lookback_steps=4, forecast_steps=2)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=3, verbose=False)

        scheduler = RecalibrationScheduler(predictor=pred, error_threshold=0.1)

        current = {"t1_us": 50.0, "t2_us": 100.0}
        # 20% drift should exceed 10% threshold
        predicted = {"t1_us": 60.0, "t2_us": 100.0}

        should_recal, reason = scheduler.should_recalibrate(current, predicted, confidence=0.9)
        assert should_recal
        assert "t1_us" in reason

    def test_should_recalibrate_no_drift(self) -> None:
        """Test that small drift does not trigger recalibration."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=5, lookback_steps=4, forecast_steps=2)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=3, verbose=False)

        scheduler = RecalibrationScheduler(predictor=pred, error_threshold=0.1)

        current = {"t1_us": 50.0, "t2_us": 100.0}
        # 2% drift should be within 10% threshold
        predicted = {"t1_us": 51.0, "t2_us": 100.0}

        should_recal, reason = scheduler.should_recalibrate(current, predicted, confidence=0.9)
        assert not should_recal

    def test_should_recalibrate_zero_parameter(self) -> None:
        """Test handling of zero-valued parameters."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=5, lookback_steps=4, forecast_steps=2)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=3, verbose=False)

        scheduler = RecalibrationScheduler(predictor=pred)

        current = {"param1": 0.0, "param2": 50.0}
        predicted = {"param1": 1.0, "param2": 50.5}

        # Should not crash on zero value
        should_recal, reason = scheduler.should_recalibrate(current, predicted, confidence=0.9)
        assert isinstance(should_recal, bool)

    def test_estimate_time_to_recalibration_untrained(self) -> None:
        """Test time estimation with untrained model."""
        pred = CalibrationPredictor()
        scheduler = RecalibrationScheduler(predictor=pred)

        history = np.random.randn(10, 5)
        hours, reason = scheduler.estimate_time_to_recalibration(history)

        assert hours == 0.0
        assert "not trained" in reason.lower()

    def test_estimate_time_to_recalibration(self) -> None:
        """Test estimating time until recalibration needed."""
        gen = DriftTrajectoryGenerator(random_seed=42)
        X, y, _ = gen.generate_dataset(n_trajectories=10, lookback_steps=10, forecast_steps=5)

        pred = CalibrationPredictor(random_seed=42)
        pred.train(X, y, epochs=3, verbose=False)

        scheduler = RecalibrationScheduler(
            predictor=pred,
            error_threshold=0.2,
            confidence_threshold=0.5,
        )

        history = X[0]  # Use first sample history
        hours, reason = scheduler.estimate_time_to_recalibration(
            history,
            sample_interval_hours=0.5,
            max_horizon_hours=12.0,
        )

        assert hours >= 0.0
        assert hours <= 12.0
        assert isinstance(reason, str)


class TestPredictorTypes:
    """Tests for different predictor types."""

    def test_all_predictor_types_exist(self) -> None:
        """Test that all predictor types are defined."""
        assert PredictorType.MLP.value == "mlp"
        assert PredictorType.LSTM.value == "lstm"
        assert PredictorType.LINEAR.value == "linear"

    def test_predictor_type_from_value(self) -> None:
        """Test creating predictor type from string value."""
        mlp = PredictorType("mlp")
        assert mlp == PredictorType.MLP

        lstm = PredictorType("lstm")
        assert lstm == PredictorType.LSTM
