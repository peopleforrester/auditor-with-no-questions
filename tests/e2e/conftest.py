# ABOUTME: Pytest fixtures for E2E testing with Kind cluster
# ABOUTME: Provides cluster setup, namespace management, and wait utilities

import subprocess
import time
from collections.abc import Generator

import pytest
from kubernetes import client, config


def _cluster_available() -> bool:
    """Check if a Kubernetes cluster is reachable."""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        v1.list_namespace(limit=1)
        return True
    except Exception:
        return False


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip all E2E tests when no Kubernetes cluster is available."""
    if not _cluster_available():
        skip_marker = pytest.mark.skip(reason="No Kubernetes cluster available")
        for item in items:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def k8s_client() -> Generator[client.CoreV1Api, None, None]:
    """Load kubeconfig and return Kubernetes API client."""
    config.load_kube_config()
    yield client.CoreV1Api()


@pytest.fixture(scope="session")
def apps_client() -> Generator[client.AppsV1Api, None, None]:
    """Return Kubernetes Apps API client."""
    config.load_kube_config()
    yield client.AppsV1Api()


@pytest.fixture(scope="session")
def custom_objects_client() -> Generator[client.CustomObjectsApi, None, None]:
    """Return Kubernetes Custom Objects API client."""
    config.load_kube_config()
    yield client.CustomObjectsApi()


def wait_for_deployment(
    apps_client: client.AppsV1Api,
    name: str,
    namespace: str,
    timeout: int = 300,
) -> bool:
    """Wait for a deployment to become ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            deployment = apps_client.read_namespaced_deployment(name, namespace)
            ready = deployment.status.ready_replicas or 0
            desired = deployment.spec.replicas or 1
            if ready >= desired:
                return True
        except client.ApiException:
            pass
        time.sleep(5)
    return False


def wait_for_statefulset(
    apps_client: client.AppsV1Api,
    name: str,
    namespace: str,
    timeout: int = 300,
) -> bool:
    """Wait for a statefulset to become ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sts = apps_client.read_namespaced_stateful_set(name, namespace)
            ready = sts.status.ready_replicas or 0
            desired = sts.spec.replicas or 1
            if ready >= desired:
                return True
        except client.ApiException:
            pass
        time.sleep(5)
    return False


def wait_for_namespace(
    k8s_client: client.CoreV1Api,
    name: str,
    timeout: int = 60,
) -> bool:
    """Wait for a namespace to exist."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            k8s_client.read_namespace(name)
            return True
        except client.ApiException:
            pass
        time.sleep(2)
    return False


def run_helm_install(
    release_name: str,
    chart: str,
    namespace: str,
    repo_url: str | None = None,
    version: str | None = None,
    values_file: str | None = None,
    create_namespace: bool = True,
) -> subprocess.CompletedProcess:
    """Run helm install command."""
    cmd = ["helm", "install", release_name, chart, "-n", namespace]

    if create_namespace:
        cmd.append("--create-namespace")
    if version:
        cmd.extend(["--version", version])
    if values_file:
        cmd.extend(["-f", values_file])
    if repo_url:
        cmd.extend(["--repo", repo_url])

    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


def run_helm_uninstall(release_name: str, namespace: str) -> subprocess.CompletedProcess:
    """Run helm uninstall command."""
    cmd = ["helm", "uninstall", release_name, "-n", namespace]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


@pytest.fixture(scope="session")
def helm_repos_configured() -> bool:
    """Ensure Helm repos are configured."""
    repos = [
        ("falcosecurity", "https://falcosecurity.github.io/charts"),
        ("kyverno", "https://kyverno.github.io/kyverno"),
        ("argo", "https://argoproj.github.io/argo-helm"),
    ]

    for name, url in repos:
        subprocess.run(
            ["helm", "repo", "add", name, url],
            capture_output=True,
            text=True,
        )

    subprocess.run(["helm", "repo", "update"], capture_output=True, text=True)
    return True
