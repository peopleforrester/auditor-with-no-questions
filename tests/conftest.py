# ABOUTME: Pytest configuration and shared fixtures
# ABOUTME: Provides mock Kubernetes client and test utilities

"""Pytest configuration and fixtures."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_k8s_client():
    """Mock Kubernetes client for testing without cluster."""
    with patch("src.utils.kubernetes.config") as mock_config:
        mock_config.load_kube_config.return_value = None
        yield mock_config


@pytest.fixture
def mock_k8s_core_v1():
    """Mock CoreV1Api client."""
    with patch("src.utils.kubernetes.client.CoreV1Api") as mock_api:
        mock_instance = MagicMock()
        mock_api.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for testing."""
    with patch.dict(
        "os.environ",
        {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_DEFAULT_REGION": "eu-central-1",
        },
    ):
        yield


@pytest.fixture
def sample_pod_list():
    """Sample pod list response."""
    return {
        "items": [
            {
                "metadata": {
                    "name": "test-pod-1",
                    "namespace": "default",
                },
                "spec": {
                    "node_name": "node-1",
                    "containers": [{"name": "main"}],
                },
                "status": {
                    "phase": "Running",
                    "container_statuses": [{"ready": True}],
                },
            },
        ],
    }


@pytest.fixture
def sample_argocd_apps():
    """Sample ArgoCD applications response."""
    return {
        "items": [
            {
                "metadata": {
                    "name": "demo-app",
                    "namespace": "argocd",
                },
                "spec": {
                    "source": {
                        "repoURL": "https://github.com/example/repo",
                    },
                },
                "status": {
                    "sync": {"status": "Synced"},
                    "health": {"status": "Healthy"},
                },
            },
        ],
    }
