# ABOUTME: EKS cluster configuration using terraform-aws-modules
# ABOUTME: Creates EKS 1.32+ cluster with managed node groups and IRSA

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  cluster_endpoint_public_access = true

  # Enable IRSA
  enable_irsa = true

  # Cluster addons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    eks-pod-identity-agent = {
      most_recent = true
    }
  }

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Cluster encryption
  cluster_encryption_config = var.enable_cluster_encryption ? {
    provider_key_arn = aws_kms_key.eks[0].arn
    resources        = ["secrets"]
  } : {}

  # EKS Managed Node Group
  eks_managed_node_groups = {
    demo = {
      name = "${var.cluster_name}-nodes"

      instance_types = [var.node_instance_type]
      capacity_type  = "ON_DEMAND"

      min_size     = var.node_min_size
      max_size     = var.node_max_size
      desired_size = var.node_desired_size

      # Use AL2023 (Amazon Linux 2023) for EKS 1.32+
      ami_type = "AL2023_x86_64_STANDARD"

      labels = {
        role = "demo"
      }

      tags = {
        Name = "${var.cluster_name}-node"
      }
    }
  }

  # Cluster access configuration
  enable_cluster_creator_admin_permissions = true

  tags = {
    Name = var.cluster_name
  }
}

# KMS key for cluster encryption
resource "aws_kms_key" "eks" {
  count = var.enable_cluster_encryption ? 1 : 0

  description             = "KMS key for EKS cluster ${var.cluster_name} encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "${var.cluster_name}-eks-encryption"
  }
}

resource "aws_kms_alias" "eks" {
  count = var.enable_cluster_encryption ? 1 : 0

  name          = "alias/${var.cluster_name}-eks"
  target_key_id = aws_kms_key.eks[0].key_id
}
