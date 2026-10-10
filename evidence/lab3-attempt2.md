<!-- ai-generated: 100% - Codex recorded the instructor's first-attempt failure and actual Kubernetes validation. -->
# Lab 3 attempt 2: Kubernetes completion

On 2026-10-10 the instructor's grade on
[issue #245](https://github.com/swasik/itsm-2026-submissions/issues/245) reported
Core PASS (6/6), Stretch PASS (2/3) and exactly one failing check:
`L3-STRETCH-3.01: /work/k8s/values.yaml not found`.
The first attempt implemented the two required Stretch tracks, leaving the
optional Kubernetes track absent. This revision completes that third track;
the application, histogram, SLO, alert expressions and previous two Stretch
artifacts remain unchanged. Tag `lab3/v1` remains immutable.

## Actual cluster validation

An isolated kind cluster `lab3-monitoring` was created on 2026-10-10 with kind
0.33.0 and the digest-pinned Kubernetes 1.35.8 image documented in
`k8s/README.md`. Helm 3.22.0 installed kube-prometheus-stack 89.2.2 successfully.
The application and seeded index images were loaded from Docker into kind.
All application, operator and Prometheus pods became Ready without restarts.

The cluster's API accepted all committed workload and monitoring manifests,
including a second server-side dry run. Parsed PrometheusRule groups equal
`prometheus/alerts.yml` exactly, including annotations and interval. Both custom
resources in the cluster export have specs identical to their committed YAML.
The installed Helm values set retention to `2h` and memory limit to `1Gi`.

Ten real `GET /kb/search?q=vpn` calls from inside the application pod returned
the seeded index's hits. Prometheus independently discovered and scraped that
application through ServiceMonitor; the live API responses are retained as:

- `k8s/live-up.json`: `up{job="svcdesk"} = 1`.
- `k8s/live-histogram.json`: `/kb/search` status 200 histogram count = 10.
- `k8s/live-rules.json`: group `svcdesk-slo`, both expected alert rules loaded,
  `health: ok`, state `inactive`, evaluated at 2026-10-10T14:43:30Z. This confirms
  the real rules load and evaluate; firing timing is covered by the existing
  promtool test suite rather than inferred from an idle cluster.

`k8s/evidence.json` is unedited stdout from:

```sh
kubectl get prometheusrules,servicemonitors,pods -A -o json
```

It contains the real PrometheusRule, ServiceMonitor and Running Prometheus pod,
as well as the application's pods and the cluster's system pods. A separate
temporary kubeconfig was used; no credentials or kubeconfig are submitted.
The Kubernetes deployment has no published host ports. The temporary
Prometheus inspection tunnel used localhost port 19091; existing Compose
services and unrelated host containers were not stopped.
