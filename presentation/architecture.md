# ABOUTME: Architecture diagrams for Sovereign Compliance presentation
# ABOUTME: Mermaid diagrams showing GitOps compliance automation

# Sovereign Compliance Architecture

## System Overview

```mermaid
graph TB
    subgraph "GitOps Source of Truth"
        Git[Git Repository]
    end

    subgraph "Kubernetes Cluster"
        subgraph "ArgoCD"
            ArgoServer[ArgoCD Server]
            AppController[Application Controller]
        end

        subgraph "Security Layer"
            Falco[Falco Runtime Security]
            Kyverno[Kyverno Policy Engine]
            Sidekick[Falcosidekick]
        end

        subgraph "Automation Layer"
            ArgoEvents[Argo Events]
            ArgoWF[Argo Workflows]
        end

        subgraph "Workloads"
            Apps[Application Pods]
        end
    end

    Git -->|Sync| ArgoServer
    AppController -->|Deploy| Apps
    Falco -->|Monitor| Apps
    Kyverno -->|Validate| Apps
    Falco -->|Alerts| Sidekick
    Sidekick -->|Webhook| ArgoEvents
    ArgoEvents -->|Trigger| ArgoWF
```

## Compliance Response Chain

```mermaid
sequenceDiagram
    participant Pod as Workload Pod
    participant Falco as Falco
    participant Sidekick as Falcosidekick
    participant Events as Argo Events
    participant WF as Argo Workflows
    participant K8s as Kubernetes API

    Pod->>Falco: Suspicious Activity
    Note over Falco: Detect via eBPF<br/>Match Compliance Rules
    Falco->>Sidekick: Alert with Tags
    Sidekick->>Events: Webhook POST
    Events->>WF: Trigger Workflow

    WF->>K8s: Capture Forensics
    WF->>K8s: Apply NetworkPolicy
    WF->>K8s: Create Evidence

    Note over WF: <5s Detection<br/><15s Isolation<br/><30s Complete
```

## GitOps Drift Detection

```mermaid
flowchart LR
    subgraph "Expected State"
        Git[Git Repository]
    end

    subgraph "Actual State"
        Cluster[Kubernetes Cluster]
    end

    subgraph "Detection"
        ArgoCD[ArgoCD]
        Falco[Falco K8s Audit]
    end

    Git -->|Declares| ArgoCD
    Cluster -->|Reports| ArgoCD
    ArgoCD -->|OutOfSync?| Alert1[Drift Alert]

    Cluster -->|kubectl ops| Falco
    Falco -->|Non-GitOps Change| Alert2[Audit Alert]
```

## App-of-Apps Sync Waves

```mermaid
gantt
    title ArgoCD Sync Wave Deployment
    dateFormat X
    axisFormat %s

    section Wave 0
    Namespaces           :a1, 0, 1

    section Wave 1
    ArgoCD               :a2, 1, 2

    section Wave 2
    Monitoring           :a3, 2, 3
    Falco                :a4, 2, 3
    Falcosidekick        :a5, 2, 3

    section Wave 3
    Kyverno              :a6, 3, 4

    section Wave 4
    Argo Events          :a7, 4, 5
    Argo Workflows       :a8, 4, 5

    section Wave 5
    Demo Application     :a9, 5, 6
```

## Evidence Package Structure

```mermaid
graph TD
    subgraph "Evidence Package"
        Manifest[manifest.json<br/>Integrity Hashes]

        subgraph "Falco Evidence"
            FA[alerts.json<br/>Runtime Detections]
        end

        subgraph "ArgoCD Evidence"
            AA[sync-history.json<br/>Deployment Audit Trail]
        end

        subgraph "Kyverno Evidence"
            KA[policy-reports.json<br/>Compliance Status]
        end

        subgraph "Git Evidence"
            GA[commit-history.json<br/>Change Attribution]
        end

        README[README.md<br/>Package Documentation]
    end

    Manifest --> FA
    Manifest --> AA
    Manifest --> KA
    Manifest --> GA
```

## Compliance Framework Mapping

```mermaid
mindmap
    root((Sovereign<br/>Compliance))
        NIS2
            Article 21 Risk Management
            Incident Handling
            Supply Chain Security
        DORA
            ICT Risk Management
            Incident Reporting
            Third-Party Risk
        SOC2
            CC6.1 Logical Access
            CC7.2 System Monitoring
            CC8.1 Change Management
        MITRE ATT&CK
            T1059 Command Execution
            T1496 Resource Hijacking
            T1562 Defense Evasion
```

## Demo Scenario Flow

```mermaid
stateDiagram-v2
    [*] --> ShellAccess: Demo 1
    ShellAccess --> FalcoDetect: Terminal spawned
    FalcoDetect --> AlertFired: <5s

    [*] --> DriftDetect: Demo 2
    DriftDetect --> ArgoOutOfSync: kubectl apply
    ArgoOutOfSync --> AuditAlert: Non-GitOps change

    [*] --> CryptoMiner: Demo 3
    CryptoMiner --> FalcoDetect2: xmrig pattern
    FalcoDetect2 --> WorkflowTrigger: <5s
    WorkflowTrigger --> ForensicCapture: Evidence collected
    ForensicCapture --> NetworkIsolation: <15s
    NetworkIsolation --> TicketCreated: <30s
    TicketCreated --> [*]: Complete

    [*] --> EvidenceExport: Demo 4
    EvidenceExport --> PackageCreated: ZIP generated
    PackageCreated --> IntegrityVerified: SHA256 hashes
    IntegrityVerified --> [*]: Auditor satisfied
```
