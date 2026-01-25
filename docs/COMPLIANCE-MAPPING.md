# Compliance Mapping

This document maps Falco detection rules to regulatory compliance controls for NIS2, DORA, and SOC2 frameworks.

## Overview

Each Falco rule in this repo includes compliance tags that map directly to regulatory requirements. When an alert fires, the evidence package automatically includes the relevant compliance context.

---

## NIS2 (EU Network and Information Security Directive)

Article 21 requires "appropriate and proportionate technical and organisational measures to manage risks."

| Falco Rule | NIS2 Article | Control Description |
|------------|--------------|---------------------|
| Terminal shell in container | Art. 21(2)(g) | Access control and authentication policies |
| Unexpected outbound connection | Art. 21(2)(e) | Network security and segmentation |
| Sensitive file access | Art. 21(2)(i) | Data protection and integrity |
| Privilege escalation detected | Art. 21(2)(g) | Access control violations |
| Non-GitOps modification | Art. 21(2)(j) | Change management and configuration control |
| Crypto mining activity | Art. 21(2)(e) | Threat detection and response |

### Evidence Requirements

NIS2 Article 23 requires incident reporting within 24 hours. This system provides:
- Automated detection timestamps
- Forensic evidence capture
- Immutable audit trails via Git

---

## DORA (Digital Operational Resilience Act)

Applies to EU financial entities. Chapter II requires ICT risk management frameworks.

| Falco Rule | DORA Article | Control Description |
|------------|--------------|---------------------|
| Terminal shell in container | Art. 9(4)(c) | Detection of anomalous activities |
| Container drift detected | Art. 9(3)(a) | ICT change management procedures |
| Crypto mining activity | Art. 10(1) | ICT-related incident detection |
| Unexpected process execution | Art. 9(4)(c) | Continuous monitoring mechanisms |
| Sensitive file access | Art. 9(3)(b) | Data integrity controls |
| Privilege escalation detected | Art. 9(4)(c) | Access control monitoring |

### Evidence Requirements

DORA Article 17 requires major incident reporting. This system provides:
- Real-time detection and classification
- Automated evidence preservation
- Complete incident timeline reconstruction

---

## SOC2 (Trust Service Criteria)

SOC2 Type II requires operational evidence over time.

| Falco Rule | SOC2 Control | Control Description |
|------------|--------------|---------------------|
| Terminal shell in container | CC6.1 | Logical access security controls |
| Sensitive file access | CC6.1 | Restricted access enforcement |
| Privilege escalation detected | CC6.2 | Access removal/modification controls |
| Container drift detected | CC8.1 | Change management controls |
| Unexpected network connection | CC6.6 | Network access restrictions |
| Crypto mining activity | CC7.2 | System monitoring and anomaly detection |

### Evidence Requirements

SOC2 auditors need 3-12 months of operational evidence. This system provides:
- Continuous compliance monitoring
- 90-day evidence export packages
- Git-based audit trail with timestamps

---

## MITRE ATT&CK Mapping

All rules also map to MITRE ATT&CK tactics and techniques:

| Falco Rule | Technique | Tactic |
|------------|-----------|--------|
| Terminal shell in container | T1059 (Command and Scripting Interpreter) | Execution |
| Sensitive file access | T1552 (Unsecured Credentials) | Credential Access |
| Crypto mining activity | T1496 (Resource Hijacking) | Impact |
| Privilege escalation detected | T1548 (Abuse Elevation Control) | Privilege Escalation |
| Unexpected outbound connection | T1048 (Exfiltration Over Alternative Protocol) | Exfiltration |

---

## How Rules Are Tagged

Each Falco rule includes compliance tags in its definition:

```yaml
- rule: Terminal shell in container
  desc: Detect interactive shell sessions in containers
  condition: >
    spawned_process and container and shell_procs and proc.tty != 0
  output: >
    Shell spawned in container
    (user=%user.name container=%container.name shell=%proc.name
     parent=%proc.pname cmdline=%proc.cmdline terminal=%proc.tty
     namespace=%k8s.ns.name pod=%k8s.pod.name)
  priority: WARNING
  tags:
    - container
    - shell
    - mitre_execution
    - T1059
    - NIS2_access_control
    - DORA_incident_detection
    - SOC2_CC6.1
```

---

## Evidence Chain

When a rule fires, the following evidence chain executes:

1. **Falco** detects the event and tags with compliance frameworks
2. **Falcosidekick** routes the alert to Argo Events
3. **Argo Workflows** triggers forensic capture:
   - Pod state snapshot (labels, annotations, spec)
   - Network connections (`netstat`, DNS queries)
   - Process tree (`ps aux`)
   - Container logs (last 1000 lines)
   - Resource consumption metrics
4. **Evidence** stored with immutable timestamp and compliance tags

This creates an auditor-ready evidence package mapped to specific compliance controls.

---

## Evidence Export

Generate a compliance evidence package:

```bash
# Export last 90 days of evidence
sovereign evidence export --days 90 --output evidence-package.zip

# Filter by framework
sovereign evidence export --framework NIS2 --output nis2-evidence.zip

# Verify package integrity
sovereign evidence verify evidence-package.zip
```

The evidence package includes:
- Falco alerts with compliance tags
- ArgoCD sync history (GitOps audit trail)
- Kyverno policy reports
- Git commit history
- Manifest of all included evidence
