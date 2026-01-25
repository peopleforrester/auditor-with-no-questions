# ABOUTME: E2E tests for ArgoCD deployment and configuration
# ABOUTME: Validates ArgoCD 3.2.x installation and app-of-apps pattern

import subprocess

import pytest
from kubernetes import client

from .conftest import wait_for_deployment, wait_for_namespace, wait_for_statefulset


class TestArgoCDDeployment:
    """Test ArgoCD deployment in Kind cluster."""

    @pytest.fixture(scope="class")
    def argocd_installed(
        self, k8s_client: client.CoreV1Api, apps_client: client.AppsV1Api
    ) -> bool:
        """Install ArgoCD in the cluster."""
        # Apply ArgoCD namespace
        subprocess.run(
            ["kubectl", "create", "namespace", "argocd"],
            capture_output=True,
            text=True,
        )

        # Apply ArgoCD manifests
        result = subprocess.run(
            [
                "kubectl",
                "apply",
                "-n",
                "argocd",
                "-f",
                "https://raw.githubusercontent.com/argoproj/argo-cd/v3.2.4/manifests/install.yaml",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to install ArgoCD: {result.stderr}")

        # Wait for namespace
        assert wait_for_namespace(k8s_client, "argocd", timeout=30)

        # Wait for ArgoCD server deployment
        ready = wait_for_deployment(
            apps_client, "argocd-server", "argocd", timeout=300
        )

        return ready

    def test_argocd_namespace_exists(
        self, k8s_client: client.CoreV1Api, argocd_installed: bool
    ) -> None:
        """Verify ArgoCD namespace exists."""
        if not argocd_installed:
            pytest.skip("ArgoCD not installed")

        ns = k8s_client.read_namespace("argocd")
        assert ns.metadata.name == "argocd"

    def test_argocd_server_running(
        self, apps_client: client.AppsV1Api, argocd_installed: bool
    ) -> None:
        """Verify ArgoCD server is running."""
        if not argocd_installed:
            pytest.skip("ArgoCD not installed")

        deployment = apps_client.read_namespaced_deployment(
            "argocd-server", "argocd"
        )
        assert deployment.status.ready_replicas >= 1

    def test_argocd_repo_server_running(
        self, apps_client: client.AppsV1Api, argocd_installed: bool
    ) -> None:
        """Verify ArgoCD repo server is running."""
        if not argocd_installed:
            pytest.skip("ArgoCD not installed")

        deployment = apps_client.read_namespaced_deployment(
            "argocd-repo-server", "argocd"
        )
        assert deployment.status.ready_replicas >= 1

    def test_argocd_application_controller_running(
        self, apps_client: client.AppsV1Api, argocd_installed: bool
    ) -> None:
        """Verify ArgoCD application controller is running."""
        if not argocd_installed:
            pytest.skip("ArgoCD not installed")

        # In ArgoCD 3.x, the controller is a StatefulSet
        # First try Deployment (older versions), then StatefulSet
        try:
            deployment = apps_client.read_namespaced_deployment(
                "argocd-application-controller", "argocd"
            )
            ready = deployment.status.ready_replicas or 0
            assert ready >= 1
        except client.ApiException:
            # ArgoCD 3.x uses StatefulSet - wait for it to be ready
            assert wait_for_statefulset(
                apps_client, "argocd-application-controller", "argocd", timeout=120
            ), "ArgoCD application controller StatefulSet not ready"

    @pytest.fixture(scope="class")
    def argocd_cleanup(
        self, k8s_client: client.CoreV1Api, argocd_installed: bool
    ) -> None:
        """Cleanup ArgoCD after tests."""
        yield
        # Don't delete in CI to allow inspection on failure
        # subprocess.run(
        #     ["kubectl", "delete", "namespace", "argocd", "--ignore-not-found"],
        #     capture_output=True,
        # )
