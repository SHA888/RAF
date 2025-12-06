#!/usr/bin/env python3
"""
Simulation study for the Reciprocal Acceleration Framework.

This example demonstrates:
1. Running extended simulations
2. Comparing different investment strategies
3. Predicting future acceleration
4. Analyzing convergence properties
"""

from typing import Dict, List

import numpy as np

from raf import ReciprocalAccelerationFramework
from raf.analysis import CrossLoopAnalyzer
from raf.loops import AnsatzDesignLoop, CalibrationControlLoop, ErrorMitigationLoop


def run_simulation(iterations: int = 20, scenario: str = "baseline") -> Dict[str, List[float]]:
    """
    Run a simulation with specified parameters.

    Args:
        iterations: Number of iterations to run
        scenario: Simulation scenario name

    Returns:
        Dictionary of acceleration histories
    """
    # Create framework
    raf = ReciprocalAccelerationFramework(name=f"Simulation_{scenario}")

    # Configure loops based on scenario
    if scenario == "baseline":
        em_params = {"accuracy_improvement": 0.02, "scale_growth": 1.1, "data_growth": 1.15}
        ad_params = {
            "quality_improvement": 0.03,
            "efficiency_improvement": 0.04,
            "surrogate_improvement": 0.04,
        }
        cc_params = {
            "model_improvement": 0.03,
            "fidelity_improvement": 0.0003,
            "depth_growth": 1.08,
        }
    elif scenario == "surrogate_investment":
        # Heavy investment in surrogate models
        em_params = {"accuracy_improvement": 0.025, "scale_growth": 1.12, "data_growth": 1.18}
        ad_params = {
            "quality_improvement": 0.04,
            "efficiency_improvement": 0.08,
            "surrogate_improvement": 0.08,
        }
        cc_params = {"model_improvement": 0.04, "fidelity_improvement": 0.0004, "depth_growth": 1.1}
    elif scenario == "hardware_focus":
        # Focus on hardware improvements
        em_params = {"accuracy_improvement": 0.015, "scale_growth": 1.08, "data_growth": 1.1}
        ad_params = {
            "quality_improvement": 0.025,
            "efficiency_improvement": 0.03,
            "surrogate_improvement": 0.03,
        }
        cc_params = {
            "model_improvement": 0.05,
            "fidelity_improvement": 0.0008,
            "depth_growth": 1.15,
        }
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    # Create loops
    error_loop = ErrorMitigationLoop(initial_accuracy=0.5, initial_scale=10.0)
    ansatz_loop = AnsatzDesignLoop(initial_quality=0.4, initial_surrogate_accuracy=0.3)
    calibration_loop = CalibrationControlLoop(
        initial_model_accuracy=0.4, initial_gate_fidelity=0.99
    )

    raf.add_loop(error_loop)
    raf.add_loop(ansatz_loop)
    raf.add_loop(calibration_loop)

    # Run simulation
    history = {
        "error_mitigation": [],
        "ansatz_design": [],
        "calibration_control": [],
        "overall": [],
    }

    for _ in range(iterations):
        error_loop.simulate_iteration(**em_params)
        ansatz_loop.simulate_iteration(**ad_params)
        calibration_loop.simulate_iteration(**cc_params)

        history["error_mitigation"].append(error_loop.state.acceleration_rate)
        history["ansatz_design"].append(ansatz_loop.state.acceleration_rate)
        history["calibration_control"].append(calibration_loop.state.acceleration_rate)

        analysis = raf.analyze()
        history["overall"].append(analysis.overall_acceleration)

    return history


def compare_scenarios():
    """Compare different investment scenarios."""
    print("=" * 60)
    print("Scenario Comparison Study")
    print("=" * 60)
    print()

    scenarios = ["baseline", "surrogate_investment", "hardware_focus"]
    results = {}

    for scenario in scenarios:
        print(f"Running scenario: {scenario}...")
        results[scenario] = run_simulation(iterations=20, scenario=scenario)

    print()
    print("Results Summary:")
    print("-" * 60)
    print(f"{'Scenario':<25} {'Final Overall':<15} {'Max Overall':<15} {'Avg Overall':<15}")
    print("-" * 60)

    for scenario, history in results.items():
        final = history["overall"][-1]
        max_val = max(history["overall"])
        avg_val = np.mean(history["overall"])
        print(f"{scenario:<25} {final:<15.3f} {max_val:<15.3f} {avg_val:<15.3f}")

    print("-" * 60)
    print()

    # Determine best scenario
    best_scenario = max(results.keys(), key=lambda s: np.mean(results[s]["overall"]))
    print(f"Best performing scenario: {best_scenario}")
    print()

    return results


def analyze_convergence():
    """Analyze convergence properties of the loops."""
    print("=" * 60)
    print("Convergence Analysis")
    print("=" * 60)
    print()

    # Run extended simulation
    history = run_simulation(iterations=50, scenario="baseline")

    # Analyze convergence
    print("Convergence Analysis:")
    print("-" * 40)

    for loop_name in ["error_mitigation", "ansatz_design", "calibration_control"]:
        values = history[loop_name]

        # Check if converging
        last_10 = values[-10:]
        variance = np.var(last_10)
        trend = np.polyfit(range(len(last_10)), last_10, 1)[0]

        if variance < 0.001 and abs(trend) < 0.01:
            status = "CONVERGED"
        elif trend > 0:
            status = "ACCELERATING"
        elif trend < -0.01:
            status = "DECELERATING"
        else:
            status = "STABLE"

        print(f"{loop_name}:")
        print(f"  Final value: {values[-1]:.3f}")
        print(f"  Variance (last 10): {variance:.4f}")
        print(f"  Trend: {trend:+.4f}")
        print(f"  Status: {status}")
        print()

    return history


def intervention_study():
    """Study the effect of targeted interventions."""
    print("=" * 60)
    print("Intervention Study")
    print("=" * 60)
    print()

    # Create baseline framework
    raf = ReciprocalAccelerationFramework()

    error_loop = ErrorMitigationLoop(initial_accuracy=0.5, initial_scale=10.0)
    ansatz_loop = AnsatzDesignLoop(initial_quality=0.4, initial_surrogate_accuracy=0.3)
    calibration_loop = CalibrationControlLoop(
        initial_model_accuracy=0.4, initial_gate_fidelity=0.99
    )

    raf.add_loop(error_loop)
    raf.add_loop(ansatz_loop)
    raf.add_loop(calibration_loop)

    # Run 5 iterations to establish baseline
    for _ in range(5):
        error_loop.simulate_iteration()
        ansatz_loop.simulate_iteration()
        calibration_loop.simulate_iteration()

    # Analyze cross-loop effects
    analyzer = CrossLoopAnalyzer()

    print("Simulating interventions on each loop:")
    print("-" * 50)

    for target_loop in raf.loops.keys():
        effects = analyzer.simulate_intervention(raf, target_loop, improvement=0.3)

        print(f"\nIntervention on {target_loop}:")
        for loop, effect in effects.items():
            bar = "█" * int(effect * 20)
            print(f"  {loop}: {effect:.3f} {bar}")

    print()

    # Identify best intervention target
    best_target = None
    best_total_effect = 0

    for target_loop in raf.loops.keys():
        effects = analyzer.simulate_intervention(raf, target_loop, improvement=0.3)
        total_effect = sum(effects.values())

        if total_effect > best_total_effect:
            best_total_effect = total_effect
            best_target = target_loop

    print(f"Best intervention target: {best_target}")
    print(f"Total system effect: {best_total_effect:.3f}")


def main():
    """Run all simulation studies."""
    print("\n" + "=" * 60)
    print("RECIPROCAL ACCELERATION FRAMEWORK - SIMULATION STUDIES")
    print("=" * 60 + "\n")

    # 1. Scenario comparison
    compare_scenarios()

    # 2. Convergence analysis
    analyze_convergence()

    # 3. Intervention study
    intervention_study()

    print("\n" + "=" * 60)
    print("All simulation studies completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
