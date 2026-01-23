# ABOUTME: Terraform outputs for EKS cluster information
# ABOUTME: Provides cluster endpoint, ARN, and IRSA role ARNs

output "cluster_name" {
  description = "The name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint for the EKS cluster API server"
  value       = module.eks.cluster_endpoint
}

output "cluster_arn" {
  description = "ARN of the EKS cluster"
  value       = module.eks.cluster_arn
}

output "cluster_version" {
  description = "Kubernetes version of the EKS cluster"
  value       = module.eks.cluster_version
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data for the cluster"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "oidc_provider_arn" {
  description = "ARN of the OIDC provider for IRSA"
  value       = module.eks.oidc_provider_arn
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "IDs of the private subnets"
  value       = module.vpc.private_subnets
}

# IRSA role ARNs
output "argocd_role_arn" {
  description = "ARN of the IAM role for ArgoCD"
  value       = module.argocd_irsa.iam_role_arn
}

output "falco_role_arn" {
  description = "ARN of the IAM role for Falco"
  value       = module.falco_irsa.iam_role_arn
}

output "argo_workflows_role_arn" {
  description = "ARN of the IAM role for Argo Workflows"
  value       = module.argo_workflows_irsa.iam_role_arn
}

# Kubeconfig update command
output "kubeconfig_command" {
  description = "Command to update kubeconfig"
  value       = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.region}"
}
