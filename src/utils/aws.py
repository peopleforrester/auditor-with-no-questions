# ABOUTME: AWS and EKS helper functions using boto3
# ABOUTME: Provides cluster info, region detection, and IAM role assumption

"""AWS and EKS helper functions."""

import os
from dataclasses import dataclass
from typing import Any

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


@dataclass
class EKSClusterInfo:
    """Information about an EKS cluster."""

    name: str
    arn: str
    version: str
    status: str
    endpoint: str
    region: str
    node_groups: list[str]


def get_current_region() -> str:
    """Get the current AWS region.

    Returns region from:
    1. AWS_DEFAULT_REGION environment variable
    2. AWS_REGION environment variable
    3. boto3 session configuration
    4. Default to eu-central-1

    Returns:
        AWS region string
    """
    region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION")

    if not region:
        session = boto3.Session()
        region = session.region_name

    return region or "eu-central-1"


def get_eks_client(region: str | None = None) -> Any:
    """Get an EKS client.

    Args:
        region: AWS region (defaults to current region)

    Returns:
        boto3 EKS client
    """
    return boto3.client("eks", region_name=region or get_current_region())


def get_eks_cluster_info(cluster_name: str, region: str | None = None) -> EKSClusterInfo:
    """Get information about an EKS cluster.

    Args:
        cluster_name: Name of the EKS cluster
        region: AWS region (defaults to current region)

    Returns:
        EKSClusterInfo with cluster details

    Raises:
        RuntimeError: If cluster not found or API error
    """
    region = region or get_current_region()
    eks = get_eks_client(region)

    try:
        response = eks.describe_cluster(name=cluster_name)
        cluster = response["cluster"]

        # Get node groups
        ng_response = eks.list_nodegroups(clusterName=cluster_name)
        node_groups = ng_response.get("nodegroups", [])

        return EKSClusterInfo(
            name=cluster["name"],
            arn=cluster["arn"],
            version=cluster["version"],
            status=cluster["status"],
            endpoint=cluster["endpoint"],
            region=region,
            node_groups=node_groups,
        )
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "ResourceNotFoundException":
            raise RuntimeError(f"EKS cluster '{cluster_name}' not found in {region}") from e
        raise RuntimeError(f"Failed to describe EKS cluster: {e}") from e
    except NoCredentialsError as e:
        raise RuntimeError(
            "AWS credentials not configured. Run 'aws configure' or set environment variables."
        ) from e


def list_eks_clusters(region: str | None = None) -> list[str]:
    """List all EKS clusters in a region.

    Args:
        region: AWS region (defaults to current region)

    Returns:
        List of cluster names
    """
    eks = get_eks_client(region)

    try:
        response = eks.list_clusters()
        clusters: list[str] = response.get("clusters", [])
        return clusters
    except (ClientError, NoCredentialsError) as e:
        raise RuntimeError(f"Failed to list EKS clusters: {e}") from e


def update_kubeconfig(cluster_name: str, region: str | None = None) -> None:
    """Update kubeconfig to use the specified EKS cluster.

    Args:
        cluster_name: Name of the EKS cluster
        region: AWS region (defaults to current region)

    Raises:
        RuntimeError: If aws eks update-kubeconfig fails
    """
    import subprocess

    region = region or get_current_region()

    cmd = [
        "aws",
        "eks",
        "update-kubeconfig",
        "--name",
        cluster_name,
        "--region",
        region,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to update kubeconfig: {result.stderr}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to update kubeconfig: {e.stderr}") from e
    except FileNotFoundError as e:
        raise RuntimeError("AWS CLI not found. Please install the AWS CLI.") from e


def assume_role_if_needed(role_arn: str | None = None) -> dict[str, str] | None:
    """Assume an IAM role if specified.

    Args:
        role_arn: ARN of the role to assume (optional)

    Returns:
        Credentials dictionary if role assumed, None otherwise
    """
    if not role_arn:
        return None

    sts = boto3.client("sts")

    try:
        response = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName="sovereign-compliance-demo",
            DurationSeconds=3600,
        )
        credentials = response["Credentials"]
        return {
            "AWS_ACCESS_KEY_ID": credentials["AccessKeyId"],
            "AWS_SECRET_ACCESS_KEY": credentials["SecretAccessKey"],
            "AWS_SESSION_TOKEN": credentials["SessionToken"],
        }
    except ClientError as e:
        raise RuntimeError(f"Failed to assume role {role_arn}: {e}") from e


def get_caller_identity() -> dict[str, str]:
    """Get the current AWS caller identity.

    Returns:
        Dictionary with Account, Arn, UserId
    """
    sts = boto3.client("sts")

    try:
        response = sts.get_caller_identity()
        return {
            "account": response["Account"],
            "arn": response["Arn"],
            "user_id": response["UserId"],
        }
    except (ClientError, NoCredentialsError) as e:
        raise RuntimeError(f"Failed to get caller identity: {e}") from e
