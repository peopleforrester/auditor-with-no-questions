# ABOUTME: IAM roles for IRSA (IAM Roles for Service Accounts)
# ABOUTME: Creates roles for ArgoCD, Falco, and Argo Workflows with least privilege

# ArgoCD IRSA role
module "argocd_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${var.cluster_name}-argocd"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["argocd:argocd-server", "argocd:argocd-application-controller"]
    }
  }

  role_policy_arns = {
    # ArgoCD may need S3 access for artifact storage
    # Add specific policies as needed
  }

  tags = {
    Name = "${var.cluster_name}-argocd-irsa"
  }
}

# Falco IRSA role (for CloudWatch Logs if needed)
module "falco_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${var.cluster_name}-falco"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["falco:falco"]
    }
  }

  role_policy_arns = {
    cloudwatch = aws_iam_policy.falco_cloudwatch.arn
  }

  tags = {
    Name = "${var.cluster_name}-falco-irsa"
  }
}

# Falco CloudWatch policy
resource "aws_iam_policy" "falco_cloudwatch" {
  name        = "${var.cluster_name}-falco-cloudwatch"
  description = "Allow Falco to write to CloudWatch Logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${var.region}:*:log-group:/aws/eks/${var.cluster_name}/falco:*"
      }
    ]
  })

  tags = {
    Name = "${var.cluster_name}-falco-cloudwatch"
  }
}

# Argo Workflows IRSA role
module "argo_workflows_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${var.cluster_name}-argo-workflows"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["argo-workflows:argo-workflows-controller", "argo-workflows:argo-workflows-server"]
    }
  }

  role_policy_arns = {
    # Add S3 access for artifact storage if needed
  }

  tags = {
    Name = "${var.cluster_name}-argo-workflows-irsa"
  }
}
