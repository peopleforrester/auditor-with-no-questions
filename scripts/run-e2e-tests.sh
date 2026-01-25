#!/bin/bash
# ABOUTME: Script to run E2E tests locally using Kind
# ABOUTME: Creates a Kind cluster, runs tests, and cleans up

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLUSTER_NAME="e2e-test"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=()

    if ! command -v kind &> /dev/null; then
        missing+=("kind")
    fi

    if ! command -v kubectl &> /dev/null; then
        missing+=("kubectl")
    fi

    if ! command -v helm &> /dev/null; then
        missing+=("helm")
    fi

    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing[*]}"
        log_info "Please install the missing tools and try again."
        exit 1
    fi

    log_info "All prerequisites met."
}

# Create Kind cluster
create_cluster() {
    log_info "Creating Kind cluster: $CLUSTER_NAME"

    if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
        log_warn "Cluster $CLUSTER_NAME already exists. Deleting..."
        kind delete cluster --name "$CLUSTER_NAME"
    fi

    kind create cluster --name "$CLUSTER_NAME" --config "$PROJECT_ROOT/tests/e2e/kind-config.yaml"

    log_info "Waiting for cluster to be ready..."
    kubectl wait --for=condition=Ready nodes --all --timeout=120s

    log_info "Cluster created successfully."
}

# Configure Helm repos
configure_helm() {
    log_info "Configuring Helm repositories..."

    helm repo add falcosecurity https://falcosecurity.github.io/charts 2>/dev/null || true
    helm repo add kyverno https://kyverno.github.io/kyverno 2>/dev/null || true
    helm repo add argo https://argoproj.github.io/argo-helm 2>/dev/null || true
    helm repo update

    log_info "Helm repositories configured."
}

# Setup Python environment
setup_python() {
    log_info "Setting up Python environment..."

    cd "$PROJECT_ROOT"

    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi

    source .venv/bin/activate

    if command -v uv &> /dev/null; then
        uv pip install -e ".[dev]"
    else
        pip install -e ".[dev]"
    fi

    log_info "Python environment ready."
}

# Run tests
run_tests() {
    log_info "Running E2E tests..."

    cd "$PROJECT_ROOT"
    source .venv/bin/activate

    pytest tests/e2e/ -v --tb=short "$@"

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log_info "All E2E tests passed!"
    else
        log_error "E2E tests failed with exit code: $exit_code"
    fi

    return $exit_code
}

# Cleanup
cleanup() {
    local keep_cluster=${KEEP_CLUSTER:-false}

    if [ "$keep_cluster" = "true" ]; then
        log_info "Keeping cluster $CLUSTER_NAME for debugging."
        log_info "Run 'kind delete cluster --name $CLUSTER_NAME' to remove it."
    else
        log_info "Deleting Kind cluster..."
        kind delete cluster --name "$CLUSTER_NAME" 2>/dev/null || true
        log_info "Cleanup complete."
    fi
}

# Main
main() {
    trap cleanup EXIT

    check_prerequisites
    create_cluster
    configure_helm
    setup_python
    run_tests "$@"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-cluster)
            export KEEP_CLUSTER=true
            shift
            ;;
        --skip-cluster)
            # Skip cluster creation for debugging
            export SKIP_CLUSTER=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

if [ "${SKIP_CLUSTER:-false}" = "true" ]; then
    setup_python
    run_tests "$@"
else
    main "$@"
fi
