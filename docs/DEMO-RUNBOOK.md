# Demo Runbook

Step-by-step script for demonstrating the sovereign compliance system.

## Pre-Demo Checklist

- [ ] EKS cluster running
- [ ] All ArgoCD apps synced (`kubectl get applications -n argocd`)
- [ ] Falco pods healthy (`kubectl get pods -n falco`)
- [ ] Argo Events sensor running (`kubectl get pods -n argo-events`)
- [ ] Terminal windows arranged (detection, response, evidence)
- [ ] ArgoCD UI open (optional)

## Quick Health Check

```bash
sovereign validate
```

All components should show green/healthy.

---

## Scenario 1: Shell Access Detection

**Story:** An attacker gains shell access to a container. Falco detects it instantly and captures forensic evidence.

### Setup

```bash
# Ensure demo target pod exists
kubectl get pods -n demo-targets

# If not, deploy it
kubectl apply -f demo/target-app/
```

### Trigger

```bash
# Open shell in container (this is what Falco detects)
kubectl exec -it -n demo-targets deploy/vulnerable-app -- /bin/sh
```

### Expected Results

**Within 3 seconds:**

1. **Falco Alert** (check logs):
```bash
kubectl logs -n falco -l app.kubernetes.io/name=falco --tail=10 | grep -i shell
```

Output shows:
- User identity
- Container name
- Compliance tags (NIS2, DORA, SOC2)

2. **Falcosidekick** routes to Argo Events:
```bash
kubectl logs -n falco -l app.kubernetes.io/name=falcosidekick --tail=5
```

3. **Argo Workflow** triggers (if configured):
```bash
kubectl get workflows -n argo-workflows
```

### Cleanup

```bash
# Exit the shell
exit
```

---

## Scenario 2: Configuration Drift Detection

**Story:** Someone bypasses GitOps and edits a deployment directly. ArgoCD catches it.

### Setup

Open ArgoCD UI or watch applications:
```bash
watch kubectl get applications -n argocd
```

### Trigger

```bash
# Manually edit a deployment (bypassing Git)
kubectl scale deployment -n demo-targets vulnerable-app --replicas=5
```

### Expected Results

**Within 30 seconds:**

1. **ArgoCD** shows application as "OutOfSync"

2. **Falco** (if K8s audit enabled) detects the manual modification:
```bash
kubectl logs -n falco -l app.kubernetes.io/name=falco --tail=20 | grep -i "Non-GitOps"
```

### Cleanup

```bash
# ArgoCD will auto-sync (if enabled) or manually sync:
kubectl patch application demo-targets -n argocd --type merge -p '{"operation":{"sync":{}}}'
```

---

## Scenario 3: Crypto Miner Detection

**Story:** A compromised container starts mining cryptocurrency. Falco detects the behavior and triggers isolation.

### Trigger

```bash
# Simulate crypto miner process name
kubectl exec -it -n demo-targets deploy/vulnerable-app -- /bin/sh -c "echo 'Simulating xmrig process'"

# Or deploy the crypto-miner simulation pod
kubectl apply -f demo/scenarios/03-crypto-miner/crypto-sim.yaml
```

### Expected Results

1. **Falco Alert** (CRITICAL priority):
```bash
kubectl logs -n falco -l app.kubernetes.io/name=falco --tail=20 | grep -i "crypto"
```

2. **Argo Workflow** triggers forensic capture:
```bash
kubectl get workflows -n argo-workflows
kubectl logs -n argo-workflows -l workflows.argoproj.io/workflow
```

3. **Evidence captured** includes:
- Pod state snapshot
- Network connections
- Process tree
- Container logs

### Cleanup

```bash
kubectl delete -f demo/scenarios/03-crypto-miner/crypto-sim.yaml
```

---

## Scenario 4: Evidence Export

**Story:** An auditor requests 90 days of compliance evidence. Generate it in seconds.

### Trigger

```bash
sovereign evidence export --days 90 --output /tmp/evidence-package.zip
```

### Expected Results

ZIP file containing:
- `manifest.json` - Index of all evidence
- `falco/` - Runtime alerts with compliance tags
- `argocd/` - GitOps sync history
- `kyverno/` - Policy reports
- `git/` - Commit history

### Verify

```bash
sovereign evidence verify /tmp/evidence-package.zip
```

---

## Demo Tips

### Terminal Layout

Recommended 3-pane layout:
1. **Left:** Command execution (kubectl exec, etc.)
2. **Top-right:** Falco logs (`kubectl logs -n falco -l app.kubernetes.io/name=falco -f`)
3. **Bottom-right:** Workflow status (`watch kubectl get workflows -n argo-workflows`)

### Timing

- Shell detection: **< 3 seconds**
- Drift detection: **< 30 seconds** (ArgoCD refresh interval)
- Evidence capture workflow: **30-60 seconds**

### Common Issues

**Falco not alerting:**
```bash
# Check Falco is running
kubectl get pods -n falco
# Check rules are loaded
kubectl logs -n falco -l app.kubernetes.io/name=falco | grep "Loading rules"
```

**Workflows not triggering:**
```bash
# Check Argo Events sensor
kubectl get sensors -n argo-events
kubectl logs -n argo-events -l sensor-name=compliance-response
```

**ArgoCD not detecting drift:**
```bash
# Force refresh
argocd app get demo-targets --refresh
```

---

## Reset Between Demos

```bash
sovereign demo reset

# Or manually:
kubectl delete workflows --all -n argo-workflows
kubectl delete pods -n demo-targets --all
kubectl apply -f demo/target-app/
```
