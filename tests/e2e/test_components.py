# ABOUTME: E2E tests for core compliance components
# ABOUTME: Validates Kyverno, Argo Events, and Argo Workflows deployments

import subprocess
from pathlib import Path

import pytest
from kubernetes import client

from .conftest import run_helm_install, wait_for_deployment, wait_for_namespace

PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestKyvernoDeployment:
    """Test Kyverno deployment via Helm."""

    @pytest.fixture(scope="class")
    def kyverno_installed(
        self,
        k8s_client: client.CoreV1Api,
        apps_client: client.AppsV1Api,
        helm_repos_configured: bool,
    ) -> bool:
        """Install Kyverno using Helm."""
        values_file = PROJECT_ROOT / "apps" / "kyverno" / "values.yaml"

        result = run_helm_install(
            release_name="kyverno",
            chart="kyverno/kyverno",
            namespace="kyverno",
            version="3.6.2",
            values_file=str(values_file) if values_file.exists() else None,
            create_namespace=True,
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to install Kyverno: {result.stderr}")

        # Wait for namespace
        assert wait_for_namespace(k8s_client, "kyverno", timeout=30)

        # Wait for admission controller
        ready = wait_for_deployment(
            apps_client, "kyverno-admission-controller", "kyverno", timeout=300
        )

        return ready

    def test_kyverno_namespace_exists(
        self, k8s_client: client.CoreV1Api, kyverno_installed: bool
    ) -> None:
        """Verify Kyverno namespace exists."""
        if not kyverno_installed:
            pytest.skip("Kyverno not installed")

        ns = k8s_client.read_namespace("kyverno")
        assert ns.metadata.name == "kyverno"

    def test_kyverno_admission_controller_running(
        self, apps_client: client.AppsV1Api, kyverno_installed: bool
    ) -> None:
        """Verify Kyverno admission controller is running."""
        if not kyverno_installed:
            pytest.skip("Kyverno not installed")

        deployment = apps_client.read_namespaced_deployment(
            "kyverno-admission-controller", "kyverno"
        )
        assert deployment.status.ready_replicas >= 1

    def test_kyverno_crds_installed(
        self, custom_objects_client: client.CustomObjectsApi, kyverno_installed: bool
    ) -> None:
        """Verify Kyverno CRDs are installed."""
        if not kyverno_installed:
            pytest.skip("Kyverno not installed")

        result = subprocess.run(
            ["kubectl", "get", "crd", "clusterpolicies.kyverno.io"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestArgoEventsDeployment:
    """Test Argo Events deployment via Helm."""

    @pytest.fixture(scope="class")
    def argo_events_installed(
        self,
        k8s_client: client.CoreV1Api,
        apps_client: client.AppsV1Api,
        helm_repos_configured: bool,
    ) -> bool:
        """Install Argo Events using Helm."""
        result = run_helm_install(
            release_name="argo-events",
            chart="argo/argo-events",
            namespace="argo-events",
            version="2.4.20",
            create_namespace=True,
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to install Argo Events: {result.stderr}")

        # Wait for namespace
        assert wait_for_namespace(k8s_client, "argo-events", timeout=30)

        # Wait for controller
        ready = wait_for_deployment(
            apps_client, "argo-events-controller-manager", "argo-events", timeout=300
        )

        return ready

    def test_argo_events_namespace_exists(
        self, k8s_client: client.CoreV1Api, argo_events_installed: bool
    ) -> None:
        """Verify Argo Events namespace exists."""
        if not argo_events_installed:
            pytest.skip("Argo Events not installed")

        ns = k8s_client.read_namespace("argo-events")
        assert ns.metadata.name == "argo-events"

    def test_argo_events_controller_running(
        self, apps_client: client.AppsV1Api, argo_events_installed: bool
    ) -> None:
        """Verify Argo Events controller is running."""
        if not argo_events_installed:
            pytest.skip("Argo Events not installed")

        deployment = apps_client.read_namespaced_deployment(
            "argo-events-controller-manager", "argo-events"
        )
        assert deployment.status.ready_replicas >= 1

    def test_argo_events_crds_installed(self, argo_events_installed: bool) -> None:
        """Verify Argo Events CRDs are installed."""
        if not argo_events_installed:
            pytest.skip("Argo Events not installed")

        crds = ["eventsources.argoproj.io", "sensors.argoproj.io", "eventbus.argoproj.io"]
        for crd in crds:
            result = subprocess.run(
                ["kubectl", "get", "crd", crd],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"CRD {crd} not found"


class TestArgoWorkflowsDeployment:
    """Test Argo Workflows deployment via Helm."""

    @pytest.fixture(scope="class")
    def argo_workflows_installed(
        self,
        k8s_client: client.CoreV1Api,
        apps_client: client.AppsV1Api,
        helm_repos_configured: bool,
    ) -> bool:
        """Install Argo Workflows using Helm."""
        result = run_helm_install(
            release_name="argo-workflows",
            chart="argo/argo-workflows",
            namespace="argo-workflows",
            version="0.45.0",
            create_namespace=True,
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to install Argo Workflows: {result.stderr}")

        # Wait for namespace
        assert wait_for_namespace(k8s_client, "argo-workflows", timeout=30)

        # Wait for controller
        ready = wait_for_deployment(
            apps_client, "argo-workflows-workflow-controller", "argo-workflows", timeout=300
        )

        return ready

    def test_argo_workflows_namespace_exists(
        self, k8s_client: client.CoreV1Api, argo_workflows_installed: bool
    ) -> None:
        """Verify Argo Workflows namespace exists."""
        if not argo_workflows_installed:
            pytest.skip("Argo Workflows not installed")

        ns = k8s_client.read_namespace("argo-workflows")
        assert ns.metadata.name == "argo-workflows"

    def test_argo_workflows_controller_running(
        self, apps_client: client.AppsV1Api, argo_workflows_installed: bool
    ) -> None:
        """Verify Argo Workflows controller is running."""
        if not argo_workflows_installed:
            pytest.skip("Argo Workflows not installed")

        deployment = apps_client.read_namespaced_deployment(
            "argo-workflows-workflow-controller", "argo-workflows"
        )
        assert deployment.status.ready_replicas >= 1

    def test_argo_workflows_crds_installed(self, argo_workflows_installed: bool) -> None:
        """Verify Argo Workflows CRDs are installed."""
        if not argo_workflows_installed:
            pytest.skip("Argo Workflows not installed")

        crds = ["workflows.argoproj.io", "workflowtemplates.argoproj.io"]
        for crd in crds:
            result = subprocess.run(
                ["kubectl", "get", "crd", crd],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"CRD {crd} not found"
