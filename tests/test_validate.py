# ABOUTME: Tests for the validate module health checks
# ABOUTME: Verifies component health checking logic

import unittest
from unittest.mock import MagicMock, patch


class TestValidateModule(unittest.TestCase):
    """Test cases for validate module functions."""

    @patch("src.validate.get_kubernetes_client")
    def test_check_argocd_health_all_running(self, mock_get_client):
        """Test ArgoCD health check when all pods are running."""
        from src.validate import check_argocd_health

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock pod list response
        mock_pod = MagicMock()
        mock_pod.status.phase = "Running"
        mock_pod.metadata.name = "argocd-server-abc123"

        mock_pod_list = MagicMock()
        mock_pod_list.items = [mock_pod]
        mock_client.list_namespaced_pod.return_value = mock_pod_list

        result = check_argocd_health()

        self.assertTrue(result["healthy"])
        self.assertEqual(result["component"], "argocd")
        mock_client.list_namespaced_pod.assert_called_once()

    @patch("src.validate.get_kubernetes_client")
    def test_check_argocd_health_no_pods(self, mock_get_client):
        """Test ArgoCD health check when no pods found."""
        from src.validate import check_argocd_health

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_pod_list = MagicMock()
        mock_pod_list.items = []
        mock_client.list_namespaced_pod.return_value = mock_pod_list

        result = check_argocd_health()

        self.assertFalse(result["healthy"])
        self.assertIn("No pods found", result["message"])

    @patch("kubernetes.client.AppsV1Api")
    def test_check_falco_health_daemonset_ready(self, mock_apps_v1):
        """Test Falco health check with ready DaemonSet."""
        from src.validate import check_falco_health

        mock_client = MagicMock()
        mock_apps_v1.return_value = mock_client

        mock_ds = MagicMock()
        mock_ds.status.desired_number_scheduled = 3
        mock_ds.status.number_ready = 3

        mock_client.read_namespaced_daemon_set.return_value = mock_ds

        result = check_falco_health()

        self.assertTrue(result["healthy"])
        self.assertEqual(result["component"], "falco")

    @patch("kubernetes.client.AppsV1Api")
    def test_check_falco_health_partial_ready(self, mock_apps_v1):
        """Test Falco health check with partially ready DaemonSet."""
        from src.validate import check_falco_health

        mock_client = MagicMock()
        mock_apps_v1.return_value = mock_client

        mock_ds = MagicMock()
        mock_ds.status.desired_number_scheduled = 3
        mock_ds.status.number_ready = 1

        mock_client.read_namespaced_daemon_set.return_value = mock_ds

        result = check_falco_health()

        self.assertFalse(result["healthy"])
        self.assertIn("1/3", result["message"])

    @patch("kubernetes.client.AppsV1Api")
    def test_check_kyverno_health_deployment_ready(self, mock_apps_v1):
        """Test Kyverno health check with ready deployment."""
        from src.validate import check_kyverno_health

        mock_client = MagicMock()
        mock_apps_v1.return_value = mock_client

        mock_deployment = MagicMock()
        mock_deployment.status.ready_replicas = 1
        mock_deployment.status.replicas = 1

        mock_client.read_namespaced_deployment.return_value = mock_deployment

        result = check_kyverno_health()

        self.assertTrue(result["healthy"])
        self.assertEqual(result["component"], "kyverno")

    @patch("kubernetes.client.AppsV1Api")
    def test_check_kyverno_health_not_ready(self, mock_apps_v1):
        """Test Kyverno health check when deployment not ready."""
        from src.validate import check_kyverno_health

        mock_client = MagicMock()
        mock_apps_v1.return_value = mock_client

        mock_deployment = MagicMock()
        mock_deployment.status.ready_replicas = 0
        mock_deployment.status.replicas = 1

        mock_client.read_namespaced_deployment.return_value = mock_deployment

        result = check_kyverno_health()

        self.assertFalse(result["healthy"])

    @patch("src.validate.get_kubernetes_client")
    def test_check_argo_events_health(self, mock_get_client):
        """Test Argo Events health check."""
        from src.validate import check_argo_events_health

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_pod = MagicMock()
        mock_pod.status.phase = "Running"
        mock_pod.metadata.name = "eventbus-default-abc123"

        mock_pod_list = MagicMock()
        mock_pod_list.items = [mock_pod]
        mock_client.list_namespaced_pod.return_value = mock_pod_list

        result = check_argo_events_health()

        self.assertTrue(result["healthy"])
        self.assertEqual(result["component"], "argo-events")

    @patch("src.validate.get_kubernetes_client")
    def test_check_handles_api_exception(self, mock_get_client):
        """Test health checks handle API exceptions gracefully."""
        from kubernetes.client.exceptions import ApiException

        from src.validate import check_argocd_health

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.list_namespaced_pod.side_effect = ApiException(status=404, reason="Not Found")

        result = check_argocd_health()

        self.assertFalse(result["healthy"])
        self.assertIn("error", result["message"].lower())


if __name__ == "__main__":
    unittest.main()
