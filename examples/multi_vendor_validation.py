#!/usr/bin/env python3
"""
Multi-Vendor Hardware Validation Script

This script runs RAF experiments across multiple quantum hardware vendors
to validate hardware-agnostic acceleration dynamics.

Supported vendors:
- Qiskit Aer (local simulation - always available)
- Azure Quantum (IonQ, Quantinuum)
- AWS Braket (IonQ, Rigetti, OQC)

Usage:
    # Test with simulators only
    python multi_vendor_validation.py --simulators-only

    # Run on real hardware (requires credentials)
    python multi_vendor_validation.py --azure --braket

    # Specific vendor
    python multi_vendor_validation.py --azure-ionq
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_backend_availability():
    """Check which backends are available."""
    from raf.backends import list_available_backends

    backends = list_available_backends()
    print("\n=== Backend Availability ===")
    for name, info in backends.items():
        status = "✓" if info["available"] else "✗"
        print(f"  {status} {name}: {info['description']}")
    print()
    return backends


def run_aer_validation(noise_profile: str = "manila"):
    """Run validation with Qiskit Aer simulator."""
    from raf.backends import create_backend
    from raf.experiments import ErrorMitigationExperiment

    print(f"\n=== Qiskit Aer Validation ({noise_profile}) ===")

    # Create noisy backend using factory function
    # Available profiles: ideal, manila, kolkata, ionq, sycamore
    backend = create_backend(noise_profile)

    # Run experiment
    experiment = ErrorMitigationExperiment(backend=backend, noise_profile_name=noise_profile)
    results = experiment.run_acceleration_study(num_iterations=3, circuits_per_iteration=5)

    # Extract metrics from nested structure
    accel_metrics = results.get("acceleration_metrics", {})
    iteration_stats = accel_metrics.get("iteration_stats", [])

    final_reduction = 0
    if iteration_stats:
        final_reduction = iteration_stats[-1].get("avg_error_reduction", 0)

    accel_factor = accel_metrics.get("acceleration_factor", 1)

    metrics = {
        "vendor": "qiskit_aer",
        "noise_profile": noise_profile,
        "iterations": accel_metrics.get("iterations", 0),
        "final_error_reduction": final_reduction,
        "acceleration_observed": accel_factor > 1,
        "acceleration_factor": accel_factor,
    }

    print(f"  Acceleration factor: {metrics['acceleration_factor']:.2f}x")
    print(f"  Final error reduction: {metrics['final_error_reduction']:.1%}")

    return metrics


def run_azure_validation(target: str = "ionq.simulator"):
    """Run validation with Azure Quantum."""
    try:
        from raf.backends import AzureQuantumBackend
    except ImportError:
        print("  ✗ Azure Quantum not available (install azure-quantum)")
        return None

    print(f"\n=== Azure Quantum Validation ({target}) ===")

    # Check for credentials
    resource_id = os.environ.get("AZURE_QUANTUM_RESOURCE_ID")
    if not resource_id:
        print("  ✗ AZURE_QUANTUM_RESOURCE_ID not set")
        print("  Set environment variables:")
        print("    export AZURE_QUANTUM_RESOURCE_ID='...'")
        print("    export AZURE_QUANTUM_LOCATION='...'")
        return None

    try:
        backend = AzureQuantumBackend(target=target)
        # Run simple test circuit
        from qiskit import QuantumCircuit

        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        result = backend.execute(qc, shots=100)
        print("  ✓ Connection successful")
        print(f"  Test circuit results: {result.counts}")

        return {
            "vendor": "azure_quantum",
            "target": target,
            "connection": "success",
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def run_braket_validation(device: str = "sv1"):
    """Run validation with AWS Braket."""
    try:
        from raf.backends import BraketBackend
    except ImportError:
        print("  ✗ AWS Braket not available (install amazon-braket-sdk)")
        return None

    print(f"\n=== AWS Braket Validation ({device}) ===")

    # Check for credentials
    if not os.environ.get("AWS_DEFAULT_REGION"):
        print("  ✗ AWS credentials not configured")
        print("  Run: aws configure")
        return None

    try:
        backend = BraketBackend(device_type=device)
        # Run simple test
        from qiskit import QuantumCircuit

        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        result = backend.execute(qc, shots=100)
        print("  ✓ Connection successful")
        print(f"  Test circuit results: {result.counts}")

        return {
            "vendor": "aws_braket",
            "device": device,
            "connection": "success",
        }
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def run_full_comparison():
    """Run full comparison across available backends."""
    print("\n" + "=" * 60)
    print("RAF Multi-Vendor Hardware Validation")
    print("=" * 60)

    results = {
        "timestamp": datetime.now().isoformat(),
        "backends": [],
    }

    # Always run Aer with different noise profiles
    for profile in ["manila", "ionq"]:
        metrics = run_aer_validation(profile)
        if metrics:
            results["backends"].append(metrics)

    # Try Azure if available
    azure_result = run_azure_validation()
    if azure_result:
        results["backends"].append(azure_result)

    # Try Braket if available
    braket_result = run_braket_validation()
    if braket_result:
        results["backends"].append(braket_result)

    # Save results
    output_dir = Path(__file__).parent.parent / "results" / "multi_vendor"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "validation_results.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n=== Summary ===")
    print(f"Backends tested: {len(results['backends'])}")
    print(f"Results saved to: {output_file}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Multi-vendor quantum validation")
    parser.add_argument(
        "--simulators-only",
        action="store_true",
        help="Only run local simulators",
    )
    parser.add_argument(
        "--azure",
        action="store_true",
        help="Include Azure Quantum",
    )
    parser.add_argument(
        "--braket",
        action="store_true",
        help="Include AWS Braket",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check backend availability",
    )

    args = parser.parse_args()

    if args.check:
        check_backend_availability()
        return

    if args.simulators_only:
        run_aer_validation("manila")
        run_aer_validation("ionq")
    else:
        run_full_comparison()


if __name__ == "__main__":
    main()
