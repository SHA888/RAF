"""
Interactive dashboard for the Reciprocal Acceleration Framework.
"""

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class RAFDashboard:
    """
    Rich-based interactive dashboard for RAF.

    Provides terminal-based visualization using the Rich library.

    Example:
        >>> from raf import ReciprocalAccelerationFramework
        >>> from raf.visualization import RAFDashboard
        >>>
        >>> raf = ReciprocalAccelerationFramework()
        >>> # ... add loops ...
        >>>
        >>> dashboard = RAFDashboard()
        >>> dashboard.display(raf)
    """

    STATUS_STYLES = {
        "inactive": "dim",
        "initializing": "yellow",
        "active": "blue",
        "accelerating": "green bold",
        "bottlenecked": "red bold",
        "saturating": "magenta",
        "converged": "cyan",
    }

    def __init__(self):
        """Initialize the dashboard."""
        self.console = Console()

    def display(self, framework):
        """
        Display the full dashboard.

        Args:
            framework: RAF instance
        """
        self.console.clear()

        # Header
        self.console.print(
            Panel(
                "[bold blue]Reciprocal Acceleration Framework[/bold blue]\n"
                "[dim]Quantum-Classical ML Co-Evolution Analysis[/dim]",
                box=box.DOUBLE,
            )
        )

        # Loop status table
        self._display_loop_status(framework)

        # Acceleration metrics
        self._display_acceleration(framework)

        # Bottlenecks
        self._display_bottlenecks(framework)

        # Cross-loop effects
        self._display_cross_loop(framework)

        # Recommendations
        self._display_recommendations(framework)

    def _display_loop_status(self, framework):
        """Display loop status table."""
        table = Table(title="Loop Status", box=box.ROUNDED)

        table.add_column("Loop", style="cyan")
        table.add_column("Level", style="dim")
        table.add_column("Status")
        table.add_column("Iteration", justify="right")
        table.add_column("Acceleration", justify="right")

        for name, loop in framework.loops.items():
            status = loop.state.status.value
            style = self.STATUS_STYLES.get(status, "")

            accel = loop.state.acceleration_rate
            accel_style = "green" if accel > 1.0 else "red" if accel < 1.0 else ""

            table.add_row(
                name,
                loop.level.value,
                Text(status.upper(), style=style),
                str(loop.state.iteration),
                Text(f"{accel:.3f}", style=accel_style),
            )

        self.console.print(table)
        self.console.print()

    def _display_acceleration(self, framework):
        """Display acceleration metrics."""
        analysis = framework.analyze()

        # Overall acceleration
        overall = analysis.overall_acceleration
        if overall > 1.1:
            style = "green bold"
            indicator = "↑"
        elif overall < 0.9:
            style = "red bold"
            indicator = "↓"
        else:
            style = "yellow"
            indicator = "→"

        self.console.print(
            Panel(
                f"[{style}]Overall Acceleration: {overall:.3f} {indicator}[/{style}]",
                title="System Acceleration",
                box=box.ROUNDED,
            )
        )
        self.console.print()

    def _display_bottlenecks(self, framework):
        """Display active bottlenecks."""
        table = Table(title="Active Bottlenecks", box=box.ROUNDED)

        table.add_column("Loop", style="cyan")
        table.add_column("Bottleneck")
        table.add_column("Severity")
        table.add_column("Type", style="dim")
        table.add_column("Priority", justify="right")

        for name, loop in framework.loops.items():
            bottlenecks = loop.identify_bottlenecks()
            active = [b for b in bottlenecks if b.is_active]

            for b in active:
                severity_style = {
                    "low": "green",
                    "medium": "yellow",
                    "high": "red",
                    "critical": "red bold",
                }.get(b.severity.value, "")

                table.add_row(
                    name,
                    b.name,
                    Text(b.severity.value.upper(), style=severity_style),
                    b.constraint_type,
                    f"{b.priority_score:.2f}",
                )

        self.console.print(table)
        self.console.print()

    def _display_cross_loop(self, framework):
        """Display cross-loop effects."""
        table = Table(title="Cross-Loop Coupling", box=box.ROUNDED)

        table.add_column("Source", style="cyan")
        table.add_column("→", style="dim")
        table.add_column("Target", style="cyan")
        table.add_column("Strength", justify="right")
        table.add_column("Effect", justify="right")

        analysis = framework.analyze()

        for effect in analysis.cross_loop_effects[:5]:
            strength = effect["coupling_strength"]
            strength_style = "green" if strength > 0.6 else "yellow" if strength > 0.3 else "dim"

            est_effect = effect["estimated_effect"]
            effect_style = "green" if est_effect > 0 else "red" if est_effect < 0 else ""

            table.add_row(
                effect["source"],
                "→",
                effect["target"],
                Text(f"{strength:.2f}", style=strength_style),
                Text(f"{est_effect:+.3f}", style=effect_style),
            )

        self.console.print(table)
        self.console.print()

    def _display_recommendations(self, framework):
        """Display recommendations."""
        analysis = framework.analyze()

        if analysis.recommendations:
            rec_text = "\n".join(f"• {rec}" for rec in analysis.recommendations[:5])
            self.console.print(
                Panel(
                    rec_text,
                    title="[bold]Recommendations[/bold]",
                    box=box.ROUNDED,
                    border_style="green",
                )
            )

    def display_loop_detail(self, loop):
        """
        Display detailed view of a single loop.

        Args:
            loop: AccelerationLoop instance
        """
        self.console.print(
            Panel(
                f"[bold]{loop.name.upper()}[/bold]\n"
                f"Level: {loop.level.value}\n"
                f"Description: {loop.description}",
                box=box.DOUBLE,
            )
        )

        # Stages
        stages_text = " → ".join(loop.stages)
        self.console.print(f"[dim]Stages:[/dim] {stages_text}")
        self.console.print()

        # Current state
        state_table = Table(title="Current State", box=box.SIMPLE)
        state_table.add_column("Metric")
        state_table.add_column("Value", justify="right")

        state_table.add_row("Iteration", str(loop.state.iteration))
        state_table.add_row("Status", loop.state.status.value)
        state_table.add_row("Acceleration", f"{loop.state.acceleration_rate:.3f}")
        state_table.add_row("Efficiency", f"{loop.state.efficiency:.2f}")

        self.console.print(state_table)
        self.console.print()

        # Bottlenecks
        bottlenecks = loop.identify_bottlenecks()
        if bottlenecks:
            self.console.print("[bold]Bottlenecks:[/bold]")
            for b in bottlenecks:
                status = "🔴" if b.is_active else "⚪"
                self.console.print(f"  {status} {b.name} ({b.severity.value})")
                if b.recommended_actions:
                    for action in b.recommended_actions[:2]:
                        self.console.print(f"      → {action}")

        # Recommendations
        recs = loop.get_recommendations()
        if recs:
            self.console.print("\n[bold]Recommendations:[/bold]")
            for rec in recs:
                self.console.print(f"  • {rec}")

    def display_summary(self, framework) -> str:
        """
        Generate and return a summary string.

        Args:
            framework: RAF instance

        Returns:
            Summary string
        """
        analysis = framework.analyze()

        lines = [
            "RAF Summary",
            "=" * 40,
            f"Loops: {len(framework.loops)}",
            f"Overall Acceleration: {analysis.overall_acceleration:.3f}",
            f"Active Bottlenecks: {len([b for b in analysis.bottlenecks if b.get('is_active')])}",
            "",
            "Loop Status:",
        ]

        for name, loop in framework.loops.items():
            lines.append(
                f"  {name}: {loop.state.status.value} (accel={loop.state.acceleration_rate:.2f})"
            )

        return "\n".join(lines)
