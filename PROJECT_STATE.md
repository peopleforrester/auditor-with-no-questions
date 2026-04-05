# PROJECT_STATE.md — April 2026 Best Practices Update

**Started:** 2026-04-06
**Branch:** staging → main
**Prior work:** Senior review remediation (completed)

## Plan Summary

Update all project dependencies, CI tooling, and practices to April 2026 standards.

## Phase 1: GitHub Actions — Safe Updates
- [ ] actions/checkout v4 → v6
- [ ] actions/setup-python v5 → v6
- [ ] astral-sh/setup-uv v5 → v8
- [ ] azure/setup-helm v4 → v5
- [ ] opentofu/setup-opentofu v1 → v2
- [ ] helm/kind-action v1.10.0 → v1.14.0
- [ ] Add workflow-level `permissions: read-all` default

## Phase 2: Security — tfsec removal + trivy fix
- [ ] Remove deprecated tfsec-action step (replaced by trivy)
- [ ] Update trivy-action 0.32.0 → 0.35.0 (supply chain attack on older tags)
- [ ] Update kube-linter 0.6.8 → 0.8.1

## Phase 3: PEP 735 — Dependency Groups Migration
- [ ] Convert [project.optional-dependencies] dev/e2e to [dependency-groups]
- [ ] Update CI from `uv sync --extra dev` to `uv sync --group dev`
- [ ] Regenerate uv.lock

## Phase 4: CNCF Version Bumps (minor/patch — safe)
- [ ] README tech stack table: ArgoCD 3.2.4→3.3.6, Falco 0.42.0→0.43.0, Kyverno 1.16.2→1.17.1
- [ ] README version requirements section update
- [ ] CI Helm chart versions: update to latest compatible
- [ ] OpenTofu 1.9.0 → 1.11.5 in CI env var

## Phase 5: Major Version Upgrades (needs research)
- [ ] Helm 3.14.0 → 4.1.3 in CI (pending compatibility research)
- [ ] Argo Workflows chart + app version update (pending research)
- [ ] Update Helm chart version pins for all charts

## Current Status
- Phase: Starting
- Branch: main (need to switch to staging)
