<!-- ai-generated: 100% - Codex documented the actual isolated Kubernetes run and its reproduction. -->
# Kubernetes monitoring (M-31)

This track uses kube-prometheus-stack **89.2.2**, kind **0.33.0**, Kubernetes
**1.35.8**, kubectl **1.35.8** and Helm **3.22.0**. The kind node image is pinned
by digest below. Install the command-line tools from their official releases and
verify their published SHA-256 checksums. The cluster is separate from Compose;
use a separate kubeconfig throughout to preserve any existing Kubernetes context.

From the repository root, with `kind`, `kubectl`, `helm` and Docker available:

```sh
export KUBECONFIG="$(mktemp /tmp/lab3-kubeconfig.XXXXXX)"
kind create cluster --name lab3-monitoring \
  --image kindest/node:v1.35.8@sha256:07b2536e30b803ed61d1677a79df6115f798ce64c80f9e22f6ed45afd09323c0 \
  --kubeconfig "$KUBECONFIG" --wait 5m
docker compose build svcdesk
docker compose pull kb-index
kind load docker-image lab1-svcdesk:local ghcr.io/swasik/seeded-toxic:2026 \
  --name lab3-monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install lab3 prometheus-community/kube-prometheus-stack \
  --version 89.2.2 --namespace monitoring --create-namespace \
  -f k8s/values.yaml --wait --timeout 5m
kubectl apply -f k8s/workloads.yaml
kubectl apply -f k8s/prometheusrule.yaml -f k8s/servicemonitor.yaml
kubectl -n svcdesk rollout status deployment/svcdesk --timeout=120s
kubectl -n monitoring wait pod --selector app.kubernetes.io/name=prometheus \
  --for=condition=Ready --timeout=180s
kubectl get prometheusrules,servicemonitors,pods -A -o json > k8s/evidence.json
```

`workloads.yaml` runs the same locally built application and seeded index as
Compose, with the `adiker` profile. Images are loaded into kind before deployment;
the workload does not install dependencies at startup. Application data is
ephemeral in this demonstration. Prometheus retains two hours of data and has a
1 GiB memory limit. Unused cluster exporters, default rules, Grafana and
Alertmanager are disabled; the existing Compose dashboard remains available.

The Service carries `app: svcdesk`. ServiceMonitor `jobLabel: app` preserves
`job="svcdesk"`, which the alert expressions require. Its namespace selector
discovers the application in `svcdesk`, while both monitoring custom resources
live in `monitoring`. The Prometheus selectors select these resources by their
`app: svcdesk` label. `prometheusrule.yaml` wraps the exact groups from
`prometheus/alerts.yml`; copy the groups again if the source rules change.

Inspect real scraping and the loaded alert rules with:

```sh
kubectl -n monitoring port-forward service/lab3-kube-prometheus-stack-prometheus 19091:9090
# In another terminal:
curl -fsS 'http://127.0.0.1:19091/api/v1/query?query=up%7Bjob%3D%22svcdesk%22%7D'
curl -fsS http://127.0.0.1:19091/api/v1/rules
```

The submitted `evidence.json` is the unedited stdout of the command above from a
running local cluster, not a hand-written Kubernetes List. It includes the
running Prometheus pod and the two applied monitoring objects. Additional live
checks are recorded in `evidence/lab3-attempt2.md`.
Kubeconfig files and credentials are never committed. To remove only this
demonstration cluster after inspection, run `kind delete cluster --name lab3-monitoring`.

References: [kind quick start](https://kind.sigs.k8s.io/docs/user/quick-start/),
[pinned chart](https://github.com/prometheus-community/helm-charts/tree/kube-prometheus-stack-89.2.2/charts/kube-prometheus-stack).
