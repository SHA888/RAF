#!/usr/bin/env python3
"""
RAF Empirical Validation Example

Demonstrates the Error Mitigation acceleration loop using realistic
noisy quantum simulation with Qiskit Aer.

This script:
1. Creates noisy quantum circuits
2. Applies Zero-Noise Extrapolation (ZNE) error mitigation
3. Tracks acceleration metrics across iterations
4. Identifies bottlenecks in the mitigation process
5. Generates visualization of results

Requirements:
    pip install qiskit qiskit-aer

Usage:
    python examples/empirical_validation.py
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from raf.backends import DeviceNoiseProfile
from raf.experiments import ErrorMitigationExperiment
from raf.utils import persist_run_config, set_all_seeds


def run_quick_demo(seed: int | None = None):
    """Run a quick demonstration (2-3 minutes)."""
    print("=" * 70)
    print("RAF Error Mitigation Loop - Quick Demo")
    print("=" * 70)
    print()

    # Create experiment with IBM Manila-like noise
    experiment = ErrorMitigationExperiment(noise_profile_name="manila", random_seed=seed)

    print("Configuration:")
    print(f"  Noise profile: {experiment.noise_profile_name}")
    print(f"  Backend: {experiment.backend.name}")
    print()

    # Run acceleration study
    results = experiment.run_acceleration_study(
        num_iterations=3,
        circuits_per_iteration=5,
        depths=[3, 5, 7],
        shots=512,
    )

    print()
    print("=" * 70)
    print("Results Summary")
    print("=" * 70)
    print(results["summary"])

    return experiment, results


def run_full_study(seed: int | None = None):
    """Run a comprehensive study (10-15 minutes)."""
    print("=" * 70)
    print("RAF Error Mitigation Loop - Full Study")
    print("=" * 70)
    print()

    # Compare different noise profiles
    profiles = ["manila", "kolkata", "ionq"]
    all_results = {}

    for profile_name in profiles:
        print(f"\n{'='*50}")
        print(f"Testing with {profile_name} noise profile")
        print(f"{'='*50}\n")

        experiment = ErrorMitigationExperiment(noise_profile_name=profile_name, random_seed=seed)

        results = experiment.run_acceleration_study(
            num_iterations=5,
            circuits_per_iteration=8,
            depths=[3, 5, 7, 10],
            shots=1024,
        )

        all_results[profile_name] = {
            "experiment": experiment,
            "results": results,
        }

        # Save results
        experiment.save_results(f"results_{profile_name}.json")
        print(f"Results saved to results_{profile_name}.json")

    # Summary comparison
    print("\n" + "=" * 70)
    print("Cross-Profile Comparison")
    print("=" * 70)

    for profile_name, data in all_results.items():
        results_dict = data["results"]  # type: ignore[index]
        metrics = results_dict["acceleration_metrics"]  # type: ignore[index]
        print(f"\n{profile_name}:")
        print(f"  Acceleration: {metrics.get('overall_acceleration', 1.0):.3f}")  # type: ignore[union-attr]
        print(
            f"  Final error reduction: {metrics.get('final_error_reduction', 0):.1%}"
            if metrics.get("final_error_reduction")  # type: ignore[union-attr]
            else "  Final error reduction: N/A"
        )

        bottlenecks = results_dict["bottleneck_indicators"]  # type: ignore[index]
        print(f"  Bottlenecks: {bottlenecks.get('num_bottlenecks', 0)}")

    return all_results


def demonstrate_noise_profiles():
    """Demonstrate different noise profiles."""
    print("=" * 70)
    print("Available Noise Profiles")
    print("=" * 70)
    print()

    profiles = [
        ("ideal", "Ideal (noiseless) simulation"),
        ("manila", "IBM Manila-like (5 qubits, superconducting)"),
        ("kolkata", "IBM Kolkata-like (27 qubits, superconducting)"),
        ("ionq", "IonQ Harmony-like (11 qubits, trapped ion)"),
        ("sycamore", "Google Sycamore-like (53 qubits, superconducting)"),
    ]

    for name, description in profiles:
        print(f"\n{name}: {description}")

        if name == "ideal":
            print("  No noise model")
            continue

        if name == "manila":
            profile = DeviceNoiseProfile.ibm_manila_like()
        elif name == "kolkata":
            profile = DeviceNoiseProfile.ibm_kolkata_like()
        elif name == "ionq":
            profile = DeviceNoiseProfile.ionq_harmony_like()
        elif name == "sycamore":
            profile = DeviceNoiseProfile.google_sycamore_like()

        print(f"  Qubits: {profile.num_qubits}")
        print(f"  T1: {profile.t1_us:.1f} μs")
        print(f"  T2: {profile.t2_us:.1f} μs")
        print(f"  1Q gate error: {profile.single_qubit_error:.2e}")
        print(f"  2Q gate error: {profile.two_qubit_error:.2e}")
        print(f"  Readout error: {profile.readout_error:.2e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="RAF Empirical Validation Example")
    parser.add_argument(
        "--mode",
        choices=["quick", "full", "profiles"],
        default="quick",
        help="Run mode: quick (2-3 min), full (10-15 min), or profiles (info only)",
    )
    parser.add_argument(
        "--save-plots", action="store_true", help="Save plots to files instead of displaying"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Global seed for reproducibility (applies to Python/NumPy/Qiskit and experiments)",
    )
    parser.add_argument(
        "--save-config",
        type=str,
        default=None,
        help="Optional path to persist run configuration (JSON)",
    )

    args = parser.parse_args()

    # Apply global seed if provided
    if args.seed is not None:
        set_all_seeds(args.seed)

    if args.mode == "profiles":
        demonstrate_noise_profiles()
    elif args.mode == "quick":
        experiment, results = run_quick_demo(seed=args.seed)

        if args.save_plots:
            try:
                experiment.plot_results(save_path="em_loop_results.png")
            except Exception as e:
                print(f"Could not save plots: {e}")

        if args.save_config:
            persist_run_config(
                {
                    "mode": "quick",
                    "seed": args.seed,
                    "noise_profile": experiment.noise_profile_name,
                    "shots": 512,
                    "depths": [3, 5, 7],
                    "num_iterations": 3,
                    "circuits_per_iteration": 5,
                },
                args.save_config,
            )
    elif args.mode == "full":
        all_results = run_full_study(seed=args.seed)

        if args.save_plots:
            for profile_name, data in all_results.items():
                try:
                    data["experiment"].plot_results(save_path=f"em_loop_{profile_name}.png")
                except Exception as e:
                    print(f"Could not save plots for {profile_name}: {e}")

        if args.save_config:
            persist_run_config(
                {
                    "mode": "full",
                    "seed": args.seed,
                    "profiles": list(all_results.keys()),
                    "shots": 1024,
                    "depths": [3, 5, 7, 10],
                    "num_iterations": 5,
                    "circuits_per_iteration": 8,
                },
                args.save_config,
            )

    print("\n" + "=" * 70)
    print("Empirical validation complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
