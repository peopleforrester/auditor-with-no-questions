# ABOUTME: Staging environment configuration for cost-effective testing
# ABOUTME: Uses smaller instances and fewer nodes than production

region              = "us-west-2"
cluster_name        = "auditor-staging"
cluster_version     = "1.33"  # Latest available, target 1.34 for production
environment         = "staging"

# Smaller instances for cost savings
node_instance_type  = "t3.medium"
node_desired_size   = 2
node_min_size       = 1
node_max_size       = 3

# Keep encryption enabled for security testing
enable_cluster_encryption = true
