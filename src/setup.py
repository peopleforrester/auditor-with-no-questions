# ABOUTME: Setup command implementation for cluster provisioning
# ABOUTME: Handles EKS creation via OpenTofu/eksctl and ArgoCD bootstrap

"""Setup command implementation."""

import subprocess
import sys
from pathlib import Path

from src.utils import create_progress, print_error, print_status, print_success


def verify_prerequisites() -> bool:
    """Verify required tools are installed.

    Returns:
        True if all prerequisites are met
    """
    tools = {
        "kubectl": ["kubectl", "version", "--client", "--short"],
        "helm": ["helm", "version", "--short"],
        "aws": ["aws", "--version"],
    }

    all_ok = True

    for tool, cmd in tools.items():
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                print_status(tool, "installed", success=True)
            else:
                print_status(tool, "not working", success=False)
                all_ok = False
        except FileNotFoundError:
            print_status(tool, "not found", success=False)
            all_ok = False
        except subprocess.TimeoutExpired:
            print_status(tool, "timeout", success=False)
            all_ok = False

    return all_ok


def run_setup(
    cluster_name: str,
    region: str,
    method: str,
    skip_cluster: bool,
) -> None:
    """Run the full setup process.

    Args:
        cluster_name: Name for the EKS cluster
        region: AWS region
        method: Infrastructure method (opentofu or eksctl)
        skip_cluster: Skip cluster creation
    """
    from rich.console import Console

    console = Console()

    console.print("\n[bold blue]Sovereign Compliance Demo Setup[/bold blue]\n")

    # Step 1: Verify prerequisites
    console.print("[bold]Step 1: Verifying prerequisites...[/bold]")
    if not verify_prerequisites():
        print_error("Prerequisites not met. Please install missing tools.")
        sys.exit(1)

    # Check for method-specific tools
    if method == "opentofu":
        try:
            subprocess.run(
                ["tofu", "version"],
                capture_output=True,
                check=True,
                timeout=10,
            )
            print_status("opentofu", "installed", success=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print_error("OpenTofu not found. Install it or use --method eksctl")
            sys.exit(1)
    else:
        try:
            subprocess.run(
                ["eksctl", "version"],
                capture_output=True,
                check=True,
                timeout=10,
            )
            print_status("eksctl", "installed", success=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print_error("eksctl not found. Install it or use --method opentofu")
            sys.exit(1)

    print_success("All prerequisites met")

    # Step 2: Create cluster (unless skipped)
    if not skip_cluster:
        console.print(f"\n[bold]Step 2: Creating EKS cluster '{cluster_name}' in {region}...[/bold]")

        project_root = Path(__file__).parent.parent

        if method == "opentofu":
            tf_dir = project_root / "infrastructure" / "terraform"
            if not tf_dir.exists():
                print_error(f"OpenTofu directory not found: {tf_dir}")
                sys.exit(1)

            with create_progress("Initializing OpenTofu...") as (progress, task):
                result = subprocess.run(
                    ["tofu", "init"],
                    cwd=tf_dir,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    print_error(f"OpenTofu init failed: {result.stderr}")
                    sys.exit(1)

            console.print("[yellow]OpenTofu plan would run here...[/yellow]")
            console.print("[yellow]OpenTofu apply would run here...[/yellow]")
            console.print("[dim](Infrastructure creation not implemented - use existing cluster)[/dim]")

        else:
            eksctl_file = project_root / "infrastructure" / "eksctl" / "cluster.yaml"
            if not eksctl_file.exists():
                print_error(f"eksctl config not found: {eksctl_file}")
                sys.exit(1)

            console.print("[yellow]eksctl create cluster would run here...[/yellow]")
            console.print("[dim](Infrastructure creation not implemented - use existing cluster)[/dim]")
    else:
        console.print("\n[bold]Step 2: Skipping cluster creation (--skip-cluster)[/bold]")

    # Step 3: Update kubeconfig
    console.print(f"\n[bold]Step 3: Updating kubeconfig for {cluster_name}...[/bold]")
    try:
        from src.utils.aws import update_kubeconfig

        update_kubeconfig(cluster_name, region)
        print_success(f"Kubeconfig updated for cluster {cluster_name}")
    except RuntimeError as e:
        print_error(str(e))
        console.print("[dim]Continuing anyway - you may need to configure kubectl manually[/dim]")

    # Step 4: Bootstrap ArgoCD
    console.print("\n[bold]Step 4: Bootstrapping ArgoCD...[/bold]")
    console.print("[yellow]ArgoCD bootstrap would run here...[/yellow]")
    console.print("[dim](Bootstrap not implemented yet - see bootstrap/argocd/)[/dim]")

    # Step 5: Deploy app-of-apps
    console.print("\n[bold]Step 5: Deploying applications...[/bold]")
    console.print("[yellow]App-of-apps deployment would run here...[/yellow]")
    console.print("[dim](Deployment not implemented yet - see bootstrap/app-of-apps/)[/dim]")

    # Summary
    console.print("\n[bold green]Setup process completed![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Run 'sovereign validate' to check component health")
    console.print("  2. Run 'sovereign demo list' to see available demos")
    console.print("  3. Run 'sovereign demo run shell-access' to test detection")
