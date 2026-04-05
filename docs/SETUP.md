# Setup Guide

Complete deployment walkthrough for the sovereign compliance demo environment.

## Prerequisites

- **AWS Account** with permissions to create EKS clusters, VPCs, and IAM roles
- **AWS CLI** configured with credentials (`aws configure`)
- **kubectl** v1.28+
- **Helm** v4.1+
- **OpenTofu** v1.11+ (or Terraform v1.6+ as drop-in replacement)

### Install OpenTofu

```bash
# macOS
brew install opentofu

# Linux (snap)
snap install opentofu --classic

# Or download from https://opentofu.org/docs/intro/install/
```

## Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/peopleforrester/auditor-with-no-questions
cd auditor-with-no-questions
```

### 2. Deploy Infrastructure

```bash
cd infrastructure/terraform

# Initialize
tofu init

# Review the plan
tofu plan

# Deploy (takes ~15-20 minutes for EKS)
tofu apply
```

This creates:
- VPC with public/private subnets
- EKS cluster (v1.34)
- Node group (t3.medium instances)
- IRSA roles for Falco, ArgoCD, Argo Workflows

### 3. Configure kubectl

```bash
aws eks update-kubeconfig --name sovereign-demo --region eu-central-1

# Verify connection
kubectl get nodes
```

### 4. Bootstrap ArgoCD

```bash
# Install ArgoCD
kubectl apply -k bootstrap/argocd/

# Wait for ArgoCD to be ready
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
```

### 5. Deploy All Applications (App-of-Apps)

```bash
kubectl apply -f bootstrap/app-of-apps/root-app.yaml
```

ArgoCD will automatically deploy:
- Falco (runtime detection)
- Falcosidekick (alert routing)
- Kyverno (policy enforcement)
- Argo Events (event handling)
- Argo Workflows (response automation)
- Demo target application

### 6. Verify Deployment

```bash
# Check ArgoCD applications
kubectl get applications -n argocd

# All should show:
# SYNC STATUS: Synced
# HEALTH STATUS: Healthy

# Or use the CLI
sovereign validate
```

## Access ArgoCD UI

```bash
# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Open https://localhost:8080
# Username: admin
# Password: (from step 4)
```

## Verify Components

### Falco

```bash
# Check Falco pods (DaemonSet - one per node)
kubectl get pods -n falco

# View Falco logs
kubectl logs -n falco -l app.kubernetes.io/name=falco --tail=50
```

### Kyverno

```bash
# Check Kyverno pods
kubectl get pods -n kyverno

# View policies
kubectl get clusterpolicies
```

### Argo Events

```bash
# Check EventSource and Sensor
kubectl get eventsources -n argo-events
kubectl get sensors -n argo-events
```

### Argo Workflows

```bash
# Check controller
kubectl get pods -n argo-workflows

# List workflow templates
kubectl get workflowtemplates -n argo-workflows
```

## Cleanup

```bash
# Delete all Kubernetes resources first
kubectl delete -f bootstrap/app-of-apps/root-app.yaml
kubectl delete -k bootstrap/argocd/

# Destroy infrastructure
cd infrastructure/terraform
tofu destroy
```

## Troubleshooting

### ArgoCD apps stuck in "Progressing"

```bash
# Check ArgoCD application controller logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller
```

### Falco not detecting events

```bash
# Verify Falco is using modern-bpf driver
kubectl logs -n falco -l app.kubernetes.io/name=falco | grep "driver"

# Should show: "modern-bpf"
```

### Kyverno blocking pods

```bash
# Check policy reports
kubectl get policyreports -A

# View specific violations
kubectl describe policyreport -n <namespace>
```

## Alternative: eksctl Deployment

If you prefer eksctl over OpenTofu:

```bash
# Create cluster
eksctl create cluster -f infrastructure/eksctl/cluster.yaml

# Then continue from step 4 (Bootstrap ArgoCD)
```
