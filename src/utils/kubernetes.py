# ABOUTME: Kubernetes client helpers for interacting with clusters
# ABOUTME: Provides wrappers for common K8s operations and ArgoCD/Falco queries

"""Kubernetes client helpers."""

from dataclasses import dataclass
from typing import Any

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException


@dataclass
class ClusterInfo:
    """Information about the connected Kubernetes cluster."""

    version: str
    node_count: int
    context: str


def get_client() -> client.CoreV1Api:
    """Get a configured Kubernetes client.

    Returns:
        Configured CoreV1Api client

    Raises:
        RuntimeError: If unable to configure client
    """
    try:
        config.load_kube_config()
    except config.ConfigException:
        try:
            config.load_incluster_config()
        except config.ConfigException as e:
            raise RuntimeError(
                "Unable to configure Kubernetes client. "
                "Ensure kubectl is configured or running in-cluster."
            ) from e

    return client.CoreV1Api()


def get_custom_objects_client() -> client.CustomObjectsApi:
    """Get a configured CustomObjects client for CRDs.

    Returns:
        Configured CustomObjectsApi client
    """
    try:
        config.load_kube_config()
    except config.ConfigException:
        config.load_incluster_config()

    return client.CustomObjectsApi()


def get_cluster_info() -> ClusterInfo:
    """Get information about the connected cluster.

    Returns:
        ClusterInfo with version, node count, and context
    """
    try:
        config.load_kube_config()
    except config.ConfigException:
        config.load_incluster_config()

    v1 = client.CoreV1Api()
    version_api = client.VersionApi()

    version_info = version_api.get_code()
    nodes = v1.list_node()

    contexts, active_context = config.list_kube_config_contexts()
    context_name = active_context.get("name", "unknown") if active_context else "in-cluster"

    return ClusterInfo(
        version=f"{version_info.major}.{version_info.minor}",
        node_count=len(nodes.items),
        context=context_name,
    )


def list_pods(
    namespace: str = "default",
    label_selector: str | None = None,
) -> list[dict[str, Any]]:
    """List pods in a namespace.

    Args:
        namespace: Kubernetes namespace
        label_selector: Optional label selector (e.g., "app=nginx")

    Returns:
        List of pod information dictionaries
    """
    v1 = get_client()

    kwargs: dict[str, Any] = {"namespace": namespace}
    if label_selector:
        kwargs["label_selector"] = label_selector

    pods = v1.list_namespaced_pod(**kwargs)

    return [
        {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": pod.status.phase,
            "node": pod.spec.node_name,
            "containers": [c.name for c in pod.spec.containers],
            "ready": all(cs.ready for cs in (pod.status.container_statuses or [])),
        }
        for pod in pods.items
    ]


def get_argocd_apps() -> list[dict[str, Any]]:
    """List ArgoCD Applications.

    Returns:
        List of ArgoCD Application information
    """
    custom_api = get_custom_objects_client()

    try:
        apps = custom_api.list_namespaced_custom_object(
            group="argoproj.io",
            version="v1alpha1",
            namespace="argocd",
            plural="applications",
        )
    except ApiException as e:
        if e.status == 404:
            return []
        raise

    return [
        {
            "name": app["metadata"]["name"],
            "namespace": app["metadata"]["namespace"],
            "sync_status": app.get("status", {}).get("sync", {}).get("status", "Unknown"),
            "health_status": app.get("status", {}).get("health", {}).get("status", "Unknown"),
            "repo": app.get("spec", {}).get("source", {}).get("repoURL", ""),
        }
        for app in apps.get("items", [])
    ]


def get_falco_pods() -> list[dict[str, Any]]:
    """Get Falco pod information.

    Returns:
        List of Falco pod information
    """
    return list_pods(namespace="falco", label_selector="app.kubernetes.io/name=falco")


def get_kyverno_pods() -> list[dict[str, Any]]:
    """Get Kyverno pod information.

    Returns:
        List of Kyverno pod information
    """
    return list_pods(namespace="kyverno", label_selector="app.kubernetes.io/name=kyverno")


def get_policy_reports(namespace: str | None = None) -> list[dict[str, Any]]:
    """Get Kyverno policy reports.

    Args:
        namespace: Optional namespace to filter reports

    Returns:
        List of policy report summaries
    """
    custom_api = get_custom_objects_client()

    try:
        if namespace:
            reports = custom_api.list_namespaced_custom_object(
                group="wgpolicyk8s.io",
                version="v1alpha2",
                namespace=namespace,
                plural="policyreports",
            )
        else:
            reports = custom_api.list_cluster_custom_object(
                group="wgpolicyk8s.io",
                version="v1alpha2",
                plural="clusterpolicyreports",
            )
    except ApiException as e:
        if e.status == 404:
            return []
        raise

    return [
        {
            "name": report["metadata"]["name"],
            "namespace": report["metadata"].get("namespace", "cluster"),
            "pass": report.get("summary", {}).get("pass", 0),
            "fail": report.get("summary", {}).get("fail", 0),
            "warn": report.get("summary", {}).get("warn", 0),
            "error": report.get("summary", {}).get("error", 0),
            "skip": report.get("summary", {}).get("skip", 0),
        }
        for report in reports.get("items", [])
    ]


def exec_in_pod(
    pod_name: str,
    namespace: str,
    command: list[str],
    container: str | None = None,
) -> str:
    """Execute a command in a pod.

    Args:
        pod_name: Name of the pod
        namespace: Namespace of the pod
        command: Command to execute as list
        container: Optional container name

    Returns:
        Command output
    """
    from kubernetes.stream import stream

    v1 = get_client()

    kwargs: dict[str, Any] = {
        "name": pod_name,
        "namespace": namespace,
        "command": command,
        "stderr": True,
        "stdin": False,
        "stdout": True,
        "tty": False,
    }
    if container:
        kwargs["container"] = container

    result: str = stream(v1.connect_get_namespaced_pod_exec, **kwargs)
    return result


def apply_manifest(manifest: dict[str, Any]) -> None:
    """Apply a Kubernetes manifest.

    Args:
        manifest: Kubernetes manifest as dictionary
    """
    from kubernetes import utils

    try:
        config.load_kube_config()
    except config.ConfigException:
        config.load_incluster_config()

    k8s_client = client.ApiClient()
    utils.create_from_dict(k8s_client, manifest)


def delete_resource(
    api_version: str,
    kind: str,
    name: str,
    namespace: str | None = None,
) -> None:
    """Delete a Kubernetes resource.

    Args:
        api_version: API version (e.g., "v1", "apps/v1")
        kind: Resource kind (e.g., "Pod", "Deployment")
        name: Resource name
        namespace: Namespace (None for cluster-scoped)
    """
    try:
        config.load_kube_config()
    except config.ConfigException:
        config.load_incluster_config()

    # Map kind to appropriate API and method
    if kind == "Pod":
        v1 = client.CoreV1Api()
        v1.delete_namespaced_pod(name=name, namespace=namespace or "default")
    elif kind == "Deployment":
        apps_v1 = client.AppsV1Api()
        apps_v1.delete_namespaced_deployment(name=name, namespace=namespace or "default")
    elif kind == "Job":
        batch_v1 = client.BatchV1Api()
        batch_v1.delete_namespaced_job(
            name=name,
            namespace=namespace or "default",
            propagation_policy="Background",
        )
    elif kind == "NetworkPolicy":
        networking_v1 = client.NetworkingV1Api()
        networking_v1.delete_namespaced_network_policy(
            name=name,
            namespace=namespace or "default",
        )
    else:
        raise ValueError(f"Unsupported kind: {kind}")
