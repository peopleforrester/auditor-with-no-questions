# ABOUTME: Main CLI entry point for sovereign compliance demo
# ABOUTME: Provides setup, validate, demo, and evidence commands

"""CLI entry point for sovereign compliance demo."""

import click
from rich.console import Console

from src import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="sovereign")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Sovereign Compliance Demo - Continuous compliance evidence for Kubernetes.

    Demonstrates a production architecture combining ArgoCD (GitOps audit trails)
    and Falco (runtime threat detection) for sovereign and regulated environments.
    """
    ctx.ensure_object(dict)


@main.command()
@click.option(
    "--cluster-name",
    default="sovereign-demo",
    help="Name for the EKS cluster",
)
@click.option(
    "--region",
    default="eu-central-1",
    help="AWS region for the cluster",
)
@click.option(
    "--method",
    type=click.Choice(["opentofu", "eksctl"]),
    default="opentofu",
    help="Infrastructure provisioning method",
)
@click.option(
    "--skip-cluster",
    is_flag=True,
    help="Skip cluster creation (use existing cluster)",
)
def setup(cluster_name: str, region: str, method: str, skip_cluster: bool) -> None:
    """Set up the demo infrastructure.

    Creates an EKS cluster and bootstraps ArgoCD with all demo components.
    """
    from src.setup import run_setup

    run_setup(
        cluster_name=cluster_name,
        region=region,
        method=method,
        skip_cluster=skip_cluster,
    )


@main.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed output",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
def validate(verbose: bool, output_json: bool) -> None:
    """Validate the demo environment.

    Checks health of all components: EKS, ArgoCD, Falco, Kyverno, etc.
    """
    from src.validate import run_validate

    run_validate(verbose=verbose, output_json=output_json)


@main.group()
def demo() -> None:
    """Run demo scenarios.

    Execute various compliance demonstration scenarios.
    """
    pass


@demo.command("list")
def demo_list() -> None:
    """List available demo scenarios."""
    from src.demo import list_scenarios

    list_scenarios()


@demo.command("run")
@click.argument("scenario")
@click.option(
    "--no-wait",
    is_flag=True,
    help="Don't wait for response chain to complete",
)
def demo_run(scenario: str, no_wait: bool) -> None:
    """Run a specific demo scenario.

    SCENARIO is the name of the scenario to run (e.g., shell-access, crypto-miner).
    """
    from src.demo import run_scenario

    run_scenario(scenario=scenario, wait=not no_wait)


@demo.command("reset")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Skip confirmation prompt",
)
def demo_reset(force: bool) -> None:
    """Reset the demo environment.

    Cleans up any running demo scenarios and resets state.
    """
    from src.demo import reset_demo

    reset_demo(force=force)


@main.group()
def evidence() -> None:
    """Export and verify compliance evidence.

    Generate evidence packages for auditors.
    """
    pass


@evidence.command("export")
@click.option(
    "--days",
    default=90,
    help="Number of days of evidence to export",
)
@click.option(
    "--output",
    "-o",
    default="evidence-package.zip",
    help="Output file path",
)
def evidence_export(days: int, output: str) -> None:
    """Export compliance evidence package.

    Generates a ZIP file containing Falco alerts, ArgoCD history,
    Kyverno reports, and Git commit history.
    """
    from src.evidence import export_evidence

    export_evidence(days=days, output_path=output)


@evidence.command("verify")
@click.argument("package_path")
def evidence_verify(package_path: str) -> None:
    """Verify an evidence package.

    Checks the integrity and completeness of an exported evidence package.
    """
    from src.evidence import verify_evidence

    verify_evidence(package_path=package_path)


if __name__ == "__main__":
    main()
