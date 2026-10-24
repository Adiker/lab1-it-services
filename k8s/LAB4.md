<!-- ai-generated: 100% - Codex documented the actual isolated Lab 4 chart experiment and its explicit uncertainty. -->
# Laboratory 4 Kubernetes comparison

This experiment is separate from the preserved Lab 3 monitoring track in `k8s/README.md`. It uses the OpenTelemetry Demo chart **0.42.3 / app 3.1.0**, kind **0.33.0**, Helm **4.3.0**, kubectl **1.35.9**, and k8sgpt **0.4.39 (ed1aac4)**. Kind selected Kubernetes **1.37.0**, unlike the handout's client-tested version; the actual node image is pinned in `lab4/kind.yaml` and recorded in `lab4/environment.json`. The binaries were downloaded from official release locations and their published SHA-256 checksums verified.

The original attempt exhausted space on the system partition while pulling the chart's images. Only this task's cluster was removed, freeing about 10 GB. Its replacement used an ext4 filesystem image on the spacious TOSHIBUŚ disk for containerd and kubelet data. Directly using that disk's NTFS directories for containerd did not yield a healthy control plane. No existing Docker project, image cache or Kubernetes context was pruned. The supplied kind config uses generic paths: replace `/tmp/lab4-linux-storage` with empty directories on a Linux filesystem with at least 20 GiB free, and keep the kubeconfig outside the repository.

The two flags supported by the recorded metrics are `paymentFailure` and `loadGeneratorFloodHomepage`. The recording does not confidently identify its resource flag or the exact failing variants. The experiment chooses payment **25%** and the chart's flood **on** variant, with **recommendationCacheFailure=on as a resource hypothesis**. That is a declared candidate configuration, not a claim that the sealed fault was opened or that all variants exactly reproduce the recording. `emailMemoryLeak` remains off. These limitations do not change the two confirmed flag identifications in the postmortem, or the two independently completed Stretch tracks.

Reproduce from the repository root with these tools on `PATH`:

```sh
export KUBECONFIG="$(mktemp /tmp/lab4-kubeconfig.XXXXXX)"
kind create cluster --name lab4-adiker --config k8s/lab4/kind.yaml --kubeconfig "$KUBECONFIG" --wait 3m
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm install demo open-telemetry/opentelemetry-demo --version 0.42.3 -f k8s/lab4/values.yaml
kubectl wait pod --all --for=condition=Ready --timeout=600s
k8sgpt analyze -o json > k8s/k8sgpt-analyze-baseline.json
kubectl get configmap flagd-config -o json | python k8s/lab4/set-scenario.py recommendationCacheFailure > /tmp/lab4-flags-patch.json
kubectl patch configmap flagd-config --type merge --patch-file /tmp/lab4-flags-patch.json
kubectl rollout restart deploy/flagd
kubectl rollout status deploy/flagd --timeout=120s
# Allow five minutes of traffic before the next command.
k8sgpt analyze -o json > k8s/k8sgpt-analyze.json
kubectl get pods -A -o json > k8s/lab4/pods.json
kind delete cluster --name lab4-adiker --kubeconfig "$KUBECONFIG"
```

`set-scenario.py` emits a merge patch without contacting a cluster. It can also select `emailMemoryLeak=100x` for a separate future hypothesis test; that alternative is not represented as an executed experiment here. No `--explain` or model backend is used by k8sgpt, and no API key or kubeconfig is committed. The raw analyzer output and the comparison are the deliverable. The pod evidence files project the live status fields and omit application environment variables; temporary cluster and filesystem data are removed when the experiment ends.
