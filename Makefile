# ABOUTME: Makefile for common development and deployment operations
# ABOUTME: Provides shortcuts for testing, linting, and infrastructure management

.PHONY: help install install-dev lint format test validate clean tf-init tf-plan tf-apply

PYTHON := python3
UV := uv

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package with uv
	$(UV) pip install -e .

install-dev:  ## Install package with dev dependencies
	$(UV) pip install -e ".[dev]"

lint:  ## Run linter (ruff)
	$(UV) run ruff check src/ tests/
	$(UV) run mypy src/

format:  ## Format code with ruff
	$(UV) run ruff format src/ tests/
	$(UV) run ruff check --fix src/ tests/

test:  ## Run tests with pytest
	$(UV) run pytest tests/ -v

validate:  ## Run all validations (lint + test)
	@echo "Running linter..."
	$(UV) run ruff check src/ tests/
	@echo "Running type checker..."
	$(UV) run mypy src/
	@echo "Running tests..."
	$(UV) run pytest tests/ -v
	@echo "All validations passed!"

clean:  ## Clean up build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# OpenTofu commands (drop-in replacement for Terraform)
tf-init:  ## Initialize OpenTofu
	tofu -chdir=infrastructure/terraform init

tf-plan:  ## Plan OpenTofu changes
	tofu -chdir=infrastructure/terraform plan

tf-apply:  ## Apply OpenTofu changes
	tofu -chdir=infrastructure/terraform apply

tf-destroy:  ## Destroy OpenTofu resources
	tofu -chdir=infrastructure/terraform destroy

# eksctl commands
eksctl-create:  ## Create EKS cluster with eksctl
	eksctl create cluster -f infrastructure/eksctl/cluster.yaml

eksctl-delete:  ## Delete EKS cluster with eksctl
	eksctl delete cluster -f infrastructure/eksctl/cluster.yaml

# ArgoCD bootstrap
bootstrap-argocd:  ## Install ArgoCD to cluster
	kubectl apply -k bootstrap/argocd/
	@echo "Waiting for ArgoCD to be ready..."
	kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s
	@echo "ArgoCD installed. Get initial password with:"
	@echo "  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"

bootstrap-apps:  ## Deploy app-of-apps
	kubectl apply -f bootstrap/app-of-apps/root-app.yaml

# Demo commands
demo-reset:  ## Reset demo environment
	sovereign demo reset

demo-shell:  ## Run shell access demo
	sovereign demo run shell-access

demo-drift:  ## Run drift detection demo
	sovereign demo run drift-detection

demo-crypto:  ## Run crypto miner demo
	sovereign demo run crypto-miner
