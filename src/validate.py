# ABOUTME: Validate command implementation for health checks
# ABOUTME: Checks status of EKS, ArgoCD, Falco, Kyverno and other components

"""Validate command implementation."""

import json
import sys
from dataclasses import asdict, dataclass
from typing import Any

from rich.console import Console
from rich.table import Table

from src.utils import print_error, print_success


def get_kubernetes_client():
    """Get Kubernetes API client.

    Returns:
        CoreV1Api client instance
    """
    from kubernetes import client, config

    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    return client.CoreV1Api()


@dataclass
class ComponentStatus:
    """Status of a single component."""

    name: str
    status: str
    healthy: bool
    details: str


@dataclass
class ValidationResult:
    """Complete validation result."""

    cluster_connected: bool
    components: list[ComponentStatus]

    @property
    def all_healthy(self) -> bool:
        """Check if all components are healthy."""
        return self.cluster_connected and all(c.healthy for c in self.components)


def check_cluster_connection() -> tuple[bool, str]:
    """Check if we can connect to the Kubernetes cluster.

    Returns:
        Tuple of (connected, details)
    """
    try:
        from src.utils.kubernetes import get_cluster_info

        info = get_cluster_info()
        return True, f"v{info.version}, {info.node_count} nodes ({info.context})"
    except Exception as e:
        return False, str(e)


def check_argocd() -> ComponentStatus:
    """Check ArgoCD health.

    Returns:
        ComponentStatus for ArgoCD
    """
    try:
        from src.utils.kubernetes import get_argocd_apps, list_pods

        pods = list_pods(namespace="argocd", label_selector="app.kubernetes.io/name=argocd-server")
        if not pods:
            return ComponentStatus(
                name="ArgoCD",
                status="Not Found",
                healthy=False,
                details="No ArgoCD server pods found",
            )

        healthy_pods = [p for p in pods if p["ready"]]
        apps = get_argocd_apps()
        synced = [a for a in apps if a["sync_status"] == "Synced"]

        return ComponentStatus(
            name="ArgoCD",
            status="Running" if healthy_pods else "Degraded",
            healthy=len(healthy_pods) > 0,
            details=f"{len(healthy_pods)}/{len(pods)} pods, {len(synced)}/{len(apps)} apps synced",
        )
    except Exception as e:
        return ComponentStatus(
            name="ArgoCD",
            status="Error",
            healthy=False,
            details=str(e),
        )


def check_falco() -> ComponentStatus:
    """Check Falco health.

    Returns:
        ComponentStatus for Falco
    """
    try:
        from src.utils.kubernetes import get_falco_pods

        pods = get_falco_pods()
        if not pods:
            return ComponentStatus(
                name="Falco",
                status="Not Found",
                healthy=False,
                details="No Falco pods found",
            )

        healthy_pods = [p for p in pods if p["ready"]]

        return ComponentStatus(
            name="Falco",
            status="Running" if healthy_pods else "Degraded",
            healthy=len(healthy_pods) > 0,
            details=f"{len(healthy_pods)}/{len(pods)} pods ready",
        )
    except Exception as e:
        return ComponentStatus(
            name="Falco",
            status="Error",
            healthy=False,
            details=str(e),
        )


def check_kyverno() -> ComponentStatus:
    """Check Kyverno health.

    Returns:
        ComponentStatus for Kyverno
    """
    try:
        from src.utils.kubernetes import get_kyverno_pods, get_policy_reports

        pods = get_kyverno_pods()
        if not pods:
            return ComponentStatus(
                name="Kyverno",
                status="Not Found",
                healthy=False,
                details="No Kyverno pods found",
            )

        healthy_pods = [p for p in pods if p["ready"]]

        try:
            reports = get_policy_reports()
            report_info = f", {len(reports)} reports"
        except Exception:
            report_info = ""

        return ComponentStatus(
            name="Kyverno",
            status="Running" if healthy_pods else "Degraded",
            healthy=len(healthy_pods) > 0,
            details=f"{len(healthy_pods)}/{len(pods)} pods ready{report_info}",
        )
    except Exception as e:
        return ComponentStatus(
            name="Kyverno",
            status="Error",
            healthy=False,
            details=str(e),
        )


def check_argo_events() -> ComponentStatus:
    """Check Argo Events health.

    Returns:
        ComponentStatus for Argo Events
    """
    try:
        from src.utils.kubernetes import list_pods

        pods = list_pods(
            namespace="argo-events",
            label_selector="app.kubernetes.io/name=argo-events",
        )
        if not pods:
            return ComponentStatus(
                name="Argo Events",
                status="Not Found",
                healthy=False,
                details="No Argo Events pods found",
            )

        healthy_pods = [p for p in pods if p["ready"]]

        return ComponentStatus(
            name="Argo Events",
            status="Running" if healthy_pods else "Degraded",
            healthy=len(healthy_pods) > 0,
            details=f"{len(healthy_pods)}/{len(pods)} pods ready",
        )
    except Exception as e:
        return ComponentStatus(
            name="Argo Events",
            status="Error",
            healthy=False,
            details=str(e),
        )


def check_argo_workflows() -> ComponentStatus:
    """Check Argo Workflows health.

    Returns:
        ComponentStatus for Argo Workflows
    """
    try:
        from src.utils.kubernetes import list_pods

        pods = list_pods(
            namespace="argo-workflows",
            label_selector="app.kubernetes.io/name=argo-workflows-controller",
        )
        if not pods:
            return ComponentStatus(
                name="Argo Workflows",
                status="Not Found",
                healthy=False,
                details="No Argo Workflows controller found",
            )

        healthy_pods = [p for p in pods if p["ready"]]

        return ComponentStatus(
            name="Argo Workflows",
            status="Running" if healthy_pods else "Degraded",
            healthy=len(healthy_pods) > 0,
            details=f"{len(healthy_pods)}/{len(pods)} pods ready",
        )
    except Exception as e:
        return ComponentStatus(
            name="Argo Workflows",
            status="Error",
            healthy=False,
            details=str(e),
        )


def run_validate(verbose: bool = False, output_json: bool = False) -> None:
    """Run validation checks on all components.

    Args:
        verbose: Show detailed output
        output_json: Output as JSON instead of table
    """
    console = Console()

    if not output_json:
        console.print("\n[bold blue]Validating Sovereign Compliance Demo Environment[/bold blue]\n")

    # Check cluster connection
    cluster_ok, cluster_details = check_cluster_connection()

    # Check all components
    components = [
        check_argocd(),
        check_falco(),
        check_kyverno(),
        check_argo_events(),
        check_argo_workflows(),
    ]

    result = ValidationResult(
        cluster_connected=cluster_ok,
        components=components,
    )

    if output_json:
        output = {
            "cluster_connected": result.cluster_connected,
            "cluster_details": cluster_details,
            "all_healthy": result.all_healthy,
            "components": [asdict(c) for c in result.components],
        }
        console.print_json(json.dumps(output, indent=2))
        return

    # Display as table
    table = Table(title="Component Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status")
    table.add_column("Details")

    # Add cluster row
    if cluster_ok:
        table.add_row("Kubernetes Cluster", "[green]Connected[/green]", cluster_details)
    else:
        table.add_row("Kubernetes Cluster", "[red]Disconnected[/red]", cluster_details)

    # Add component rows
    for comp in components:
        if comp.healthy:
            status = f"[green]{comp.status}[/green]"
        else:
            status = f"[red]{comp.status}[/red]"
        table.add_row(comp.name, status, comp.details)

    console.print(table)

    # Summary
    console.print()
    if result.all_healthy:
        print_success("All components healthy!")
    else:
        unhealthy = [c.name for c in components if not c.healthy]
        if not cluster_ok:
            unhealthy.insert(0, "Cluster")
        print_error(f"Unhealthy components: {', '.join(unhealthy)}")
        sys.exit(1)


# Test-compatible health check functions


def check_argocd_health() -> dict[str, Any]:
    """Check ArgoCD health (test-compatible interface).

    Returns:
        Dict with healthy, component, and message keys
    """
    try:
        k8s = get_kubernetes_client()
        pods = k8s.list_namespaced_pod(
            namespace="argocd",
            label_selector="app.kubernetes.io/name=argocd-server",
        )

        if not pods.items:
            return {
                "healthy": False,
                "component": "argocd",
                "message": "No pods found in argocd namespace",
            }

        running_pods = [p for p in pods.items if p.status.phase == "Running"]
        return {
            "healthy": len(running_pods) > 0,
            "component": "argocd",
            "message": f"{len(running_pods)}/{len(pods.items)} pods running",
        }
    except Exception as e:
        return {
            "healthy": False,
            "component": "argocd",
            "message": f"Error checking ArgoCD: {e}",
        }


def check_falco_health() -> dict[str, Any]:
    """Check Falco health (test-compatible interface).

    Returns:
        Dict with healthy, component, and message keys
    """
    try:
        from kubernetes import client

        apps_v1 = client.AppsV1Api()
        ds = apps_v1.read_namespaced_daemon_set(
            name="falco",
            namespace="falco",
        )

        desired = ds.status.desired_number_scheduled or 0
        ready = ds.status.number_ready or 0

        return {
            "healthy": ready == desired and desired > 0,
            "component": "falco",
            "message": f"{ready}/{desired} pods ready",
        }
    except Exception as e:
        return {
            "healthy": False,
            "component": "falco",
            "message": f"Error checking Falco: {e}",
        }


def check_kyverno_health() -> dict[str, Any]:
    """Check Kyverno health (test-compatible interface).

    Returns:
        Dict with healthy, component, and message keys
    """
    try:
        from kubernetes import client

        apps_v1 = client.AppsV1Api()
        # Kyverno 1.16+ uses kyverno-admission-controller as the main deployment
        deployment = apps_v1.read_namespaced_deployment(
            name="kyverno-admission-controller",
            namespace="kyverno",
        )

        ready = deployment.status.ready_replicas or 0
        desired = deployment.status.replicas or 0

        return {
            "healthy": ready == desired and desired > 0,
            "component": "kyverno",
            "message": f"{ready}/{desired} replicas ready",
        }
    except Exception as e:
        return {
            "healthy": False,
            "component": "kyverno",
            "message": f"Error checking Kyverno: {e}",
        }


def check_argo_events_health() -> dict[str, Any]:
    """Check Argo Events health (test-compatible interface).

    Returns:
        Dict with healthy, component, and message keys
    """
    try:
        k8s = get_kubernetes_client()
        pods = k8s.list_namespaced_pod(
            namespace="argo-events",
            label_selector="app.kubernetes.io/part-of=argo-events",
        )

        if not pods.items:
            return {
                "healthy": False,
                "component": "argo-events",
                "message": "No pods found in argo-events namespace",
            }

        running_pods = [p for p in pods.items if p.status.phase == "Running"]
        return {
            "healthy": len(running_pods) > 0,
            "component": "argo-events",
            "message": f"{len(running_pods)}/{len(pods.items)} pods running",
        }
    except Exception as e:
        return {
            "healthy": False,
            "component": "argo-events",
            "message": f"Error checking Argo Events: {e}",
        }
