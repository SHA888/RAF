#!/usr/bin/env python3
"""
Basic usage example for the Reciprocal Acceleration Framework.

This example demonstrates:
1. Creating the framework with all three acceleration loops
2. Running iterations and observing acceleration dynamics
3. Analyzing bottlenecks and cross-loop effects
4. Generating recommendations
"""

from raf import ReciprocalAccelerationFramework
from raf.analysis import BottleneckAnalyzer, CrossLoopAnalyzer, ResearchPrioritizer
from raf.loops import AnsatzDesignLoop, CalibrationControlLoop, ErrorMitigationLoop
from raf.visualization import LoopDynamicsVisualizer, RAFDashboard


def main():
    print("=" * 60)
    print("Reciprocal Acceleration Framework - Basic Example")
    print("=" * 60)
    print()

    # 1. Create the framework
    print("1. Creating framework with three acceleration loops...")
    raf = ReciprocalAccelerationFramework(name="QML_Research")

    # 2. Add acceleration loops
    error_loop = ErrorMitigationLoop(
        initial_accuracy=0.6,
        initial_scale=20.0,
    )
    ansatz_loop = AnsatzDesignLoop(
        initial_quality=0.5,
        initial_surrogate_accuracy=0.4,
        search_strategy="evolutionary",
    )
    calibration_loop = CalibrationControlLoop(
        initial_model_accuracy=0.5,
        initial_gate_fidelity=0.995,
        hardware_modality="superconducting",
    )

    raf.add_loop(error_loop)
    raf.add_loop(ansatz_loop)
    raf.add_loop(calibration_loop)

    print(f"   Added loops: {list(raf.loops.keys())}")
    print()

    # 3. Run several iterations
    print("2. Running 5 iterations...")
    for i in range(5):
        # Simulate improvements in each loop
        error_loop.simulate_iteration(
            accuracy_improvement=0.03,
            scale_growth=1.15,
            data_growth=1.2,
        )
        ansatz_loop.simulate_iteration(
            quality_improvement=0.04,
            efficiency_improvement=0.05,
            surrogate_improvement=0.06,
        )
        calibration_loop.simulate_iteration(
            model_improvement=0.04,
            fidelity_improvement=0.0005,
            depth_growth=1.1,
        )

        print(f"   Iteration {i+1}:")
        for name, loop in raf.loops.items():
            print(
                f"      {name}: accel={loop.state.acceleration_rate:.3f}, "
                f"status={loop.state.status.value}"
            )
    print()

    # 4. Perform analysis
    print("3. Analyzing framework state...")
    analysis = raf.analyze()

    print(f"   Overall acceleration: {analysis.overall_acceleration:.3f}")
    print(f"   Active bottlenecks: {len([b for b in analysis.bottlenecks if b.get('is_active')])}")
    print()

    # 5. Bottleneck analysis
    print("4. Bottleneck Analysis:")
    bottleneck_analyzer = BottleneckAnalyzer()
    bottleneck_results = bottleneck_analyzer.analyze(raf)

    print(f"   Total bottlenecks: {bottleneck_results['total_bottlenecks']}")
    print(f"   Active bottlenecks: {bottleneck_results['active_bottlenecks']}")

    if bottleneck_results["priority_ranking"]:
        print("   Top priority bottleneck:")
        top = bottleneck_results["priority_ranking"][0]
        print(f"      {top['name']} ({top['loop']}): priority={top['priority_score']:.2f}")
    print()

    # 6. Cross-loop analysis
    print("5. Cross-Loop Analysis:")
    cross_analyzer = CrossLoopAnalyzer()
    cross_results = cross_analyzer.analyze(raf)

    print(f"   Network density: {cross_results['network_density']:.2f}")
    print(f"   Total coupling strength: {cross_results['total_coupling_strength']:.2f}")

    if cross_results["leverage_points"]:
        print("   Highest leverage point:")
        top_leverage = cross_results["leverage_points"][0]
        print(f"      {top_leverage['loop']}: leverage={top_leverage['leverage_score']:.2f}")
    print()

    # 7. Research prioritization
    print("6. Research Prioritization:")
    prioritizer = ResearchPrioritizer()
    roadmap = prioritizer.generate_roadmap(raf)

    print("   Top 3 investment opportunities:")
    for i, inv in enumerate(roadmap["priority_investments"][:3], 1):
        print(f"      {i}. {inv['name']} (ROI: {inv['roi_score']:.2f})")
    print()

    # 8. Recommendations
    print("7. Top Recommendations:")
    for i, rec in enumerate(analysis.recommendations[:5], 1):
        print(f"   {i}. {rec}")
    print()

    # 9. Generate visualization report
    print("8. Generating report...")
    visualizer = LoopDynamicsVisualizer()
    report = visualizer.generate_report(raf)

    print("\n" + "=" * 60)
    print(report)

    # 10. Display dashboard (if rich is available)
    print("\n" + "=" * 60)
    print("9. Dashboard Display:")
    dashboard = RAFDashboard()
    summary = dashboard.display_summary(raf)
    print(summary)

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
