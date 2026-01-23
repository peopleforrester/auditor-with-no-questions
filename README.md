# The Auditor Who Had Nothing Left To Ask

> *"The ability to move the needle without permission is a form of sovereignty."*
> — Kelsey Hightower, Civo Navigate London 2025

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![CNCF Projects](https://img.shields.io/badge/CNCF-Graduated%20Projects-326CE5)](https://www.cncf.io/projects/)

**Continuous compliance evidence for sovereign Kubernetes using CNCF projects.**

Companion code for **Open Sovereign Cloud Day** at KubeCon EU 2026 Amsterdam.

---

## What This Does

An auditor walks into your infrastructure. They expect scattered logs and engineers scrambling. Instead, they find a system that already knows what they'll ask—and is currently detecting issues they haven't thought to check.

This repository demonstrates a production architecture combining:

| Component | Version | Role | CNCF Status |
|-----------|---------|------|-------------|
| **ArgoCD** | 3.2.x | GitOps audit trails | Graduated |
| **Falco** | 0.41.x | Runtime threat detection (eBPF) | Graduated |
| **Kyverno** | 1.16.x | Policy enforcement (CEL-based) | Incubating |
| **Argo Events** | 1.10.x | Event-driven automation | Incubating |
| **Argo Workflows** | 3.6.x | Response orchestration | Graduated |

**No vendor lock-in. Runs anywhere Kubernetes runs.**

## Author

**Michael Forrester**
Principal Training Architect & DevOps Advocate

## Quick Start

```bash
# Clone and install
git clone https://github.com/michaelrishiforrester/auditor-with-no-questions.git
cd auditor-with-no-questions

# Python environment (requires 3.11+)
uv venv && source .venv/bin/activate
uv pip install -e .

# Or with pip
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Set up infrastructure and validate
sovereign setup --method eksctl --region eu-central-1
sovereign validate

# Run a demo scenario
sovereign demo run shell-access
```

## CLI Commands

```bash
# Setup
sovereign setup --cluster-name demo --region eu-central-1 --method terraform

# Validation
sovereign validate              # Check all components
sovereign validate --json       # Output as JSON
sovereign validate --verbose    # Show details

# Demo scenarios
sovereign demo list             # List available scenarios
sovereign demo run shell-access # Run specific scenario
sovereign demo reset            # Clean up for fresh demo

# Evidence export
sovereign evidence export --days 90 --output evidence.zip
sovereign evidence verify evidence.zip
```

## Demo Scenarios

| Scenario | What It Shows | Duration |
|----------|---------------|----------|
| `shell-access` | Falco detects `kubectl exec` with compliance tags | ~30s |
| `drift-detection` | ArgoCD catches non-GitOps changes | ~30s |
| `crypto-miner` | Full response: detect - capture - isolate - ticket | ~45s |
| `evidence-export` | Generate 90-day compliance package | ~15s |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SOVEREIGN COMPLIANCE LAYER                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐      RUNTIME DETECTION       ┌─────────────────────┐    │
│   │  FALCO   │──────────────────────────────│    ALERT STREAM     │    │
│   │  (eBPF)  │   syscalls, k8s audit        │    (evidence)       │    │
│   └──────────┘                              └──────────┬──────────┘    │
│        │                                               │               │
│   ┌────▼─────┐      EVENT ROUTING           ┌─────────▼──────────┐    │
│   │ SIDEKICK │──────────────────────────────│   ARGO EVENTS      │    │
│   └──────────┘                              └──────────┬──────────┘    │
│                                                        │               │
│   ┌──────────┐      AUTOMATED RESPONSE      ┌─────────▼──────────┐    │
│   │  ARGO    │◀─────────────────────────────│   ARGO WORKFLOWS   │    │
│   │   CD     │   capture, isolate, ticket   └────────────────────┘    │
│   └────┬─────┘                                                         │
│        │            POLICY ENFORCEMENT      ┌────────────────────┐    │
│   ┌────▼─────┐                              │      KYVERNO       │    │
│   │   GIT    │   immutable audit trail      │   (CEL policies)   │    │
│   └──────────┘                              └────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Version Requirements (January 2026)

**Important version updates:**

- **EKS**: Use 1.32+ (1.29 is now extended support)
- **ArgoCD**: 3.2.x (breaking changes from 2.x - new RBAC model)
- **Falco**: 0.41.x with `modern-bpf` driver
- **Kyverno**: 1.16.x with new CEL-based ValidatingPolicy

## Compliance Mappings

Every Falco rule includes framework tags:

```yaml
tags:
  - mitre_execution      # MITRE ATT&CK T1059
  - NIS2_access_control  # NIS2 Article 21
  - DORA_incident_detection  # DORA Chapter III
  - SOC2_CC6.1          # SOC2 Logical Access
```

## Project Structure

```
├── src/                      # Python CLI and automation
│   ├── cli.py                # Main CLI entry point
│   ├── validate.py           # Health checks
│   ├── demo.py               # Demo orchestration
│   └── evidence.py           # Evidence export
├── infrastructure/           # Terraform + eksctl
├── bootstrap/                # ArgoCD 3.2 installation
├── apps/                     # All managed applications
│   ├── falco/                # Detection + rules
│   ├── kyverno/              # CEL-based policies
│   └── argo-*/               # Events + Workflows
├── demo/                     # Demo scenarios
└── presentation/             # Slides and backup videos
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 - See [LICENSE](LICENSE)

## Security

For security concerns, see [SECURITY.md](SECURITY.md)

---

**The auditor had nothing left to ask. Now you have everything you need to build this.**
