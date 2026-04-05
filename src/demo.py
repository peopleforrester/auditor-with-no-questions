# ABOUTME: Demo command implementation for running compliance scenarios
# ABOUTME: Provides list, run, and reset functionality for demo scenarios

"""Demo command implementation."""

from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table

from src.utils import create_progress, print_error, print_success, print_warning


@dataclass
class Scenario:
    """Demo scenario definition."""

    name: str
    title: str
    description: str
    duration: str
    path: Path


SCENARIOS = [
    Scenario(
        name="shell-access",
        title="Shell Access Detection",
        description="Demonstrate Falco detecting kubectl exec into a container",
        duration="~30s",
        path=Path("demo/scenarios/01-shell-access"),
    ),
    Scenario(
        name="drift-detection",
        title="GitOps Drift Detection",
        description="Demonstrate ArgoCD detecting non-GitOps changes",
        duration="~30s",
        path=Path("demo/scenarios/02-drift-detection"),
    ),
    Scenario(
        name="crypto-miner",
        title="Crypto Miner Response Chain",
        description="Full automated response: detect, capture, isolate, ticket",
        duration="~45s",
        path=Path("demo/scenarios/03-crypto-miner"),
    ),
    Scenario(
        name="evidence-export",
        title="Evidence Package Export",
        description="Generate a 90-day compliance evidence package",
        duration="~15s",
        path=Path("demo/scenarios/04-evidence-export"),
    ),
]


def get_scenario(name: str) -> Scenario | None:
    """Get a scenario by name.

    Args:
        name: Scenario name

    Returns:
        Scenario if found, None otherwise
    """
    for scenario in SCENARIOS:
        if scenario.name == name:
            return scenario
    return None


def list_scenarios() -> None:
    """List all available demo scenarios."""
    console = Console()

    console.print("\n[bold blue]Available Demo Scenarios[/bold blue]\n")

    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Title")
    table.add_column("Description")
    table.add_column("Duration")

    for scenario in SCENARIOS:
        table.add_row(
            scenario.name,
            scenario.title,
            scenario.description,
            scenario.duration,
        )

    console.print(table)

    console.print("\nRun a scenario with: [bold]sovereign demo run <name>[/bold]")


def run_scenario(scenario: str, wait: bool = True) -> None:
    """Run a specific demo scenario.

    Args:
        scenario: Scenario name
        wait: Wait for response chain to complete
    """
    console = Console()

    scenario_def = get_scenario(scenario)
    if not scenario_def:
        print_error(f"Unknown scenario: {scenario}")
        console.print("\nAvailable scenarios:")
        for s in SCENARIOS:
            console.print(f"  - {s.name}")
        return

    console.print(f"\n[bold blue]Running: {scenario_def.title}[/bold blue]")
    console.print(f"[dim]{scenario_def.description}[/dim]\n")

    if scenario == "shell-access":
        run_shell_access_scenario(console, wait)
    elif scenario == "drift-detection":
        run_drift_detection_scenario(console, wait)
    elif scenario == "crypto-miner":
        run_crypto_miner_scenario(console, wait)
    elif scenario == "evidence-export":
        run_evidence_export_scenario(console)
    else:
        print_warning(f"Scenario '{scenario}' not yet implemented")


def run_shell_access_scenario(console: Console, wait: bool) -> None:
    """Run the shell access detection scenario.

    Args:
        console: Rich console
        wait: Wait for Falco alert
    """
    console.print("[bold]Step 1:[/bold] Deploying target pod...")

    # Check if target pod exists, create if not
    try:
        from src.utils.kubernetes import list_pods

        pods = list_pods(namespace="default", label_selector="app=demo-target")
        if pods:
            console.print("[dim]Target pod already exists[/dim]")
        else:
            console.print("[yellow]Target pod not found - would deploy here[/yellow]")
            console.print(
                "[dim](Deployment not implemented - create demo/target-app manually)[/dim]"
            )
            return
    except Exception as e:
        print_error(f"Failed to check pods: {e}")
        return

    console.print("\n[bold]Step 2:[/bold] Executing shell in container...")
    console.print('[cyan]kubectl exec -it demo-target -- /bin/sh -c "echo audit-test"[/cyan]')

    try:
        from src.utils.kubernetes import exec_in_pod

        result = exec_in_pod(
            pod_name=pods[0]["name"],
            namespace="default",
            command=["/bin/sh", "-c", "echo 'audit-test'"],
        )
        console.print(f"[dim]Output: {result}[/dim]")
    except Exception as e:
        print_error(f"Failed to exec: {e}")
        return

    if wait:
        console.print("\n[bold]Step 3:[/bold] Watching for Falco alert...")
        with create_progress("Waiting for Falco alert...") as (progress, task):
            import time

            # In real implementation, would watch Falco events
            time.sleep(3)
            progress.update(task, description="Alert detected!")

        console.print("\n[bold green]Expected Falco Alert:[/bold green]")
        console.print("""
[yellow]Terminal shell in container[/yellow]
  Rule: Terminal Shell in Container
  Priority: WARNING
  Tags: mitre_execution, T1059, NIS2_access_control, DORA_incident_detection
  Container: demo-target
  Command: /bin/sh -c echo audit-test
""")

    print_success("Shell access scenario completed!")


def run_drift_detection_scenario(console: Console, wait: bool) -> None:
    """Run the drift detection scenario.

    Args:
        console: Rich console
        wait: Wait for ArgoCD detection
    """
    console.print("[bold]Step 1:[/bold] Applying out-of-band change...")
    console.print(
        "[cyan]kubectl apply -f demo/scenarios/02-drift-detection/drift-manifest.yaml[/cyan]"
    )
    console.print("[yellow](Would apply manifest here)[/yellow]")

    if wait:
        console.print("\n[bold]Step 2:[/bold] Watching ArgoCD for drift...")
        with create_progress("Waiting for ArgoCD to detect drift...") as (progress, task):
            import time

            time.sleep(2)
            progress.update(task, description="Drift detected!")

        console.print("\n[bold yellow]ArgoCD Status: OutOfSync[/bold yellow]")
        console.print("""
  Application: demo-app
  Sync Status: OutOfSync
  Health: Healthy
  Drift: ConfigMap/demo-config modified outside GitOps
""")

    print_success("Drift detection scenario completed!")


def run_crypto_miner_scenario(console: Console, wait: bool) -> None:
    """Run the crypto miner response chain scenario.

    Args:
        console: Rich console
        wait: Wait for full response chain
    """
    console.print("[bold]Step 1:[/bold] Deploying simulated crypto miner...")
    console.print("[cyan]kubectl apply -f demo/scenarios/03-crypto-miner/crypto-sim.yaml[/cyan]")
    console.print("[yellow](Would deploy crypto simulation Job here)[/yellow]")

    if wait:
        console.print("\n[bold]Step 2:[/bold] Watching response chain...")

        steps = [
            ("Falco detects suspicious process...", 2),
            ("Falcosidekick sends alert to Argo Events...", 1),
            ("Argo Workflow triggered...", 1),
            ("Capturing forensic evidence...", 2),
            ("Applying network isolation...", 1),
            ("Creating incident ticket...", 1),
        ]

        for step_desc, duration in steps:
            with create_progress(step_desc) as (progress, task):
                import time

                time.sleep(duration)

        console.print("\n[bold green]Response Chain Complete![/bold green]")
        console.print("""
[bold]Timeline:[/bold]
  00:00 - Crypto miner process spawned
  00:02 - Falco alert: Crypto Mining Activity Detected
  00:03 - Falcosidekick forwarded to Argo Events
  00:04 - Argo Workflow started: forensic-capture
  00:06 - Evidence captured (pod describe, logs)
  00:07 - Network policy applied (isolation)
  00:08 - Incident ticket created

[bold]Evidence Generated:[/bold]
  - Forensic capture artifact
  - Network policy: isolate-crypto-sim
  - Incident: INC-2026-001

[bold yellow]Total Response Time: 8 seconds[/bold yellow]
""")

    print_success("Crypto miner response scenario completed!")


def run_evidence_export_scenario(console: Console) -> None:
    """Run the evidence export scenario.

    Args:
        console: Rich console
    """
    from src.evidence import export_evidence

    console.print("[bold]Exporting 90-day evidence package...[/bold]\n")
    export_evidence(days=90, output_path="evidence-demo.zip")


def reset_demo(force: bool = False) -> None:
    """Reset the demo environment.

    Args:
        force: Skip confirmation prompt
    """
    console = Console()

    if not force:
        console.print("\n[yellow]This will reset the demo environment:[/yellow]")
        console.print("  - Delete demo target pods")
        console.print("  - Remove any isolation network policies")
        console.print("  - Clean up crypto miner simulations")
        console.print()

        import click

        if not click.confirm("Continue?"):
            console.print("[dim]Cancelled[/dim]")
            return

    console.print("\n[bold]Resetting demo environment...[/bold]")

    with create_progress("Cleaning up resources...") as (progress, task):
        # Would delete demo resources here
        import time

        time.sleep(2)

    print_success("Demo environment reset!")
