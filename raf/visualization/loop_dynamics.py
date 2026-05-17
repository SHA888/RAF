"""
Loop dynamics visualization for the Reciprocal Acceleration Framework.
"""

from typing import Any

import numpy as np

try:
    import matplotlib.patches as mpatches  # noqa: F401
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap  # noqa: F401

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class LoopDynamicsVisualizer:
    """
    Visualizes acceleration loop dynamics.

    Provides various visualizations:
    - Acceleration over time
    - Loop coupling network
    - Bottleneck heatmaps
    - Progress dashboards

    Example:
        >>> from raf import ReciprocalAccelerationFramework
        >>> from raf.visualization import LoopDynamicsVisualizer
        >>>
        >>> raf = ReciprocalAccelerationFramework()
        >>> # ... add loops and run iterations ...
        >>>
        >>> viz = LoopDynamicsVisualizer()
        >>> viz.plot_acceleration_history(raf)
        >>> viz.plot_coupling_network(raf)
    """

    # Color schemes
    LOOP_COLORS = {
        "error_mitigation": "#3498db",  # Blue
        "ansatz_design": "#2ecc71",  # Green
        "calibration_control": "#e74c3c",  # Red
    }

    STATUS_COLORS = {
        "inactive": "#95a5a6",
        "initializing": "#f39c12",
        "active": "#3498db",
        "accelerating": "#2ecc71",
        "bottlenecked": "#e74c3c",
        "saturating": "#9b59b6",
        "converged": "#1abc9c",
    }

    def __init__(self, figsize: tuple[int, int] = (10, 6)) -> None:
        """
        Initialize the visualizer.

        Args:
            figsize: Default figure size for plots
        """
        self.figsize = figsize

        if not HAS_MATPLOTLIB:
            print("Warning: matplotlib not installed. Visualization will be limited.")

    def plot_acceleration_history(self, framework: Any, save_path: str | None = None) -> Any | None:
        """
        Plot acceleration history for all loops.

        Args:
            framework: RAF instance
            save_path: Optional path to save figure

        Returns:
            matplotlib figure or None
        """
        if not HAS_MATPLOTLIB:
            return self._text_acceleration_history(framework)

        fig, ax = plt.subplots(figsize=self.figsize)

        for name, loop in framework.loops.items():
            if loop.metrics.acceleration_history:
                iterations = [m.iteration for m in loop.metrics.acceleration_history]
                values = [m.acceleration_ratio for m in loop.metrics.acceleration_history]

                color = self.LOOP_COLORS.get(name, "#7f8c8d")
                ax.plot(iterations, values, "o-", label=name, color=color, linewidth=2)

        ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5, label="Baseline")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Acceleration Rate")
        ax.set_title("Loop Acceleration History")
        ax.legend()
        ax.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")

        return fig

    def _text_acceleration_history(self, framework: Any) -> str:
        """Text-based acceleration history when matplotlib unavailable."""
        lines = ["=== Acceleration History ===\n"]

        for name, loop in framework.loops.items():
            lines.append(f"\n{name}:")
            if loop.metrics.acceleration_history:
                for m in loop.metrics.acceleration_history[-5:]:  # Last 5
                    bar = "█" * int(m.acceleration_ratio * 10)
                    lines.append(f"  Iter {m.iteration}: {m.acceleration_ratio:.3f} {bar}")
            else:
                lines.append("  No history")

        return "\n".join(lines)

    def plot_coupling_network(self, framework: Any, save_path: str | None = None) -> Any | None:
        """
        Plot the loop coupling network.

        Args:
            framework: RAF instance
            save_path: Optional path to save figure

        Returns:
            matplotlib figure or None
        """
        if not HAS_MATPLOTLIB or not HAS_NETWORKX:
            return self._text_coupling_network(framework)

        fig, ax = plt.subplots(figsize=self.figsize)

        # Create directed graph
        G = nx.DiGraph()

        # Add nodes
        for name in framework.loops:
            G.add_node(name)

        # Add edges with coupling strength
        for coupling in framework.couplings:
            if coupling.source_loop in G and coupling.target_loop in G:
                G.add_edge(
                    coupling.source_loop, coupling.target_loop, weight=coupling.coupling_strength
                )

        # Layout
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Draw nodes
        node_colors = [self.LOOP_COLORS.get(n, "#7f8c8d") for n in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", ax=ax)

        # Draw edges with varying width based on coupling strength
        edges = G.edges(data=True)
        weights: list[float] = [e[2]["weight"] * 3 for e in edges]
        nx.draw_networkx_edges(
            G, pos, width=weights, alpha=0.6, edge_color="gray", arrows=True, arrowsize=20, ax=ax
        )

        ax.set_title("Loop Coupling Network")
        ax.axis("off")

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")

        return fig

    def _text_coupling_network(self, framework: Any) -> str:
        """Text-based coupling network when libraries unavailable."""
        lines = ["=== Coupling Network ===\n"]

        for coupling in framework.couplings:
            strength_bar = "█" * int(coupling.coupling_strength * 10)
            lines.append(
                f"{coupling.source_loop} → {coupling.target_loop}: "
                f"{coupling.coupling_strength:.2f} {strength_bar}"
            )

        return "\n".join(lines)

    def plot_bottleneck_heatmap(self, framework: Any, save_path: str | None = None) -> Any | None:
        """
        Plot bottleneck severity heatmap.

        Args:
            framework: RAF instance
            save_path: Optional path to save figure

        Returns:
            matplotlib figure or None
        """
        if not HAS_MATPLOTLIB:
            return self._text_bottleneck_summary(framework)

        # Collect bottleneck data
        loop_names = list(framework.loops.keys())
        bottleneck_types = set()

        data: dict[str, dict[str, float]] = {}
        for name, loop in framework.loops.items():
            bottlenecks = loop.identify_bottlenecks()
            data[name] = {}
            for b in bottlenecks:
                btype: str = b.constraint_type
                bottleneck_types.add(btype)
                data[name][btype] = b.severity_score if b.is_active else 0

        bottleneck_types_sorted = sorted(bottleneck_types)

        # Create matrix
        matrix = np.zeros((len(loop_names), len(bottleneck_types_sorted)))
        for i, loop in enumerate(loop_names):
            for j, btype in enumerate(bottleneck_types_sorted):
                matrix[i, j] = data.get(loop, {}).get(btype, 0)

        fig, ax = plt.subplots(figsize=self.figsize)

        im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)

        ax.set_xticks(range(len(bottleneck_types)))
        ax.set_xticklabels(bottleneck_types, rotation=45, ha="right")
        ax.set_yticks(range(len(loop_names)))
        ax.set_yticklabels(loop_names)

        ax.set_title("Bottleneck Severity Heatmap")
        plt.colorbar(im, ax=ax, label="Severity")

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")

        return fig

    def _text_bottleneck_summary(self, framework: Any) -> str:
        """Text-based bottleneck summary."""
        lines = ["=== Bottleneck Summary ===\n"]

        for name, loop in framework.loops.items():
            lines.append(f"\n{name}:")
            bottlenecks = loop.identify_bottlenecks()
            if bottlenecks:
                for b in bottlenecks:
                    status = "🔴" if b.is_active else "⚪"
                    lines.append(f"  {status} {b.name}: {b.severity.value}")
            else:
                lines.append("  No bottlenecks")

        return "\n".join(lines)

    def plot_progress_dashboard(self, framework: Any, save_path: str | None = None) -> Any | None:
        """
        Plot a comprehensive progress dashboard.

        Args:
            framework: RAF instance
            save_path: Optional path to save figure

        Returns:
            matplotlib figure or None
        """
        if not HAS_MATPLOTLIB:
            return self._text_progress_dashboard(framework)

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Loop status
        ax1 = axes[0, 0]
        loop_names = list(framework.loops.keys())
        statuses = [loop.state.status.value for loop in framework.loops.values()]
        colors = [self.STATUS_COLORS.get(s, "#7f8c8d") for s in statuses]

        bars = ax1.barh(loop_names, [1] * len(loop_names), color=colors)
        ax1.set_xlim(0, 1)
        ax1.set_xlabel("")
        ax1.set_title("Loop Status")

        # Add status labels
        for i, (_bar, status) in enumerate(zip(bars, statuses, strict=False)):
            ax1.text(0.5, i, status.upper(), ha="center", va="center", fontweight="bold")

        # 2. Acceleration rates
        ax2 = axes[0, 1]
        accels = [loop.state.acceleration_rate for loop in framework.loops.values()]
        colors = [self.LOOP_COLORS.get(n, "#7f8c8d") for n in loop_names]

        ax2.bar(loop_names, accels, color=colors)
        ax2.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5)
        ax2.set_ylabel("Acceleration Rate")
        ax2.set_title("Current Acceleration")
        ax2.tick_params(axis="x", rotation=45)

        # 3. Iteration counts
        ax3 = axes[1, 0]
        iterations = [loop.state.iteration for loop in framework.loops.values()]
        ax3.bar(loop_names, iterations, color=colors)
        ax3.set_ylabel("Iterations")
        ax3.set_title("Loop Iterations")
        ax3.tick_params(axis="x", rotation=45)

        # 4. Bottleneck counts
        ax4 = axes[1, 1]
        bottleneck_counts = []
        for loop in framework.loops.values():
            active = len([b for b in loop.identify_bottlenecks() if b.is_active])
            bottleneck_counts.append(active)

        ax4.bar(loop_names, bottleneck_counts, color="#e74c3c")
        ax4.set_ylabel("Active Bottlenecks")
        ax4.set_title("Bottleneck Count")
        ax4.tick_params(axis="x", rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")

        return fig

    def _text_progress_dashboard(self, framework: Any) -> str:
        """Text-based progress dashboard."""
        lines = ["=== Progress Dashboard ===\n"]

        for name, loop in framework.loops.items():
            lines.append(f"\n{name}:")
            lines.append(f"  Status: {loop.state.status.value}")
            lines.append(f"  Iteration: {loop.state.iteration}")
            lines.append(f"  Acceleration: {loop.state.acceleration_rate:.3f}")

            active_bottlenecks = len([b for b in loop.identify_bottlenecks() if b.is_active])
            lines.append(f"  Active Bottlenecks: {active_bottlenecks}")

        return "\n".join(lines)

    def generate_report(self, framework: Any) -> str:
        """
        Generate a text-based report of loop dynamics.

        Args:
            framework: RAF instance

        Returns:
            Formatted report string
        """
        lines = [
            "=" * 60,
            "RECIPROCAL ACCELERATION FRAMEWORK - DYNAMICS REPORT",
            "=" * 60,
            "",
        ]

        # Overall status
        analysis = framework.analyze()
        lines.append(f"Overall Acceleration: {analysis.overall_acceleration:.3f}")
        lines.append(
            f"Active Bottlenecks: {len([b for b in analysis.bottlenecks if b.get('is_active')])}"
        )
        lines.append("")

        # Per-loop details
        lines.append("-" * 40)
        lines.append("LOOP DETAILS")
        lines.append("-" * 40)

        for name, loop in framework.loops.items():
            lines.append(f"\n[{name.upper()}]")
            lines.append(f"  Level: {loop.level.value}")
            lines.append(f"  Status: {loop.state.status.value}")
            lines.append(f"  Iteration: {loop.state.iteration}")
            lines.append(f"  Acceleration: {loop.state.acceleration_rate:.3f}")

            # Recommendations
            recs = loop.get_recommendations()
            if recs:
                lines.append("  Recommendations:")
                lines += [f"    • {rec}" for rec in recs[:3]]

        # Cross-loop effects
        lines.append("")
        lines.append("-" * 40)
        lines.append("CROSS-LOOP EFFECTS")
        lines.append("-" * 40)

        lines += [
            f"  {effect['source']} → {effect['target']}: "
            f"strength={effect['coupling_strength']:.2f}, "
            f"effect={effect['estimated_effect']:.3f}"
            for effect in analysis.cross_loop_effects[:5]
        ]

        # Recommendations
        lines.append("")
        lines.append("-" * 40)
        lines.append("TOP RECOMMENDATIONS")
        lines.append("-" * 40)

        lines += [f"  • {rec}" for rec in analysis.recommendations[:5]]

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)
