<!-- ai-generated: 100% - Codex documented the assigned recorded path, evidence and local verification commands. -->
# Laboratory 4

This work uses **lab4-rec-4**, assigned to GitHub login **adiker** by itsmlab **0.8.6**. The supplied snapshot and ticket are unchanged. The repository remains public at `Adiker/lab1-it-services`; the implemented Lab 3 baseline is retained as `student`. No issue or submission receipt is part of this work.

The incident is described in [postmortem.md](postmortem.md). Its recorded alert is `ShopCheckoutErrors`; the prospective repository rules `CheckoutErrorRate` and `CheckoutLatency` did not run during that recording. The inferred flags are `paymentFailure` and `loadGeneratorFloodHomepage`. The third resource flag remains uncertain; only the grader can open the sealed fault.

The primary [ledger](ai-rca-eval.json) scores the four final claims in the original course-provided Qwen [transcript](ai-rca/transcript.md). The second [ledger](ai-rca-eval-2.json) scores three claims from the saved [Codex investigation](ai-rca/second/transcript.md), with raw MCP calls in its JSONL twin. The [comparison](ai-rca/COMPARISON.md) documents strengths and investigation mistakes. [comms-log.md](comms-log.md) contains hypothetical course-defined regulatory clocks; no communication was sent. Local action IDs `LAB4-A01`–`LAB4-A04` do not refer to published issues. The additional Kubernetes experiment and its resource-flag assumption are documented in [k8s/LAB4.md](k8s/LAB4.md).

## Verification

Local result: **Core 5/5, Stretch 3/3**, with no failing or error checks. The two checks that require the sealed-fault key remain expected local skips.

Run from the repository root:

```sh
docker pull ghcr.io/swasik/itsmlab:2026
./itsmlab.sh --version
./itsmlab.sh recording 4
./itsmlab.sh incident 4
./itsmlab.sh verify 4 --json report.json

docker run --rm -v "$PWD/prometheus:/p:ro" -w /p --entrypoint promtool \
  prom/prometheus:v3.15.0 check rules alerts.yml demo-alerts.yml
docker run --rm -v "$PWD/prometheus:/p:ro" -w /p --entrypoint promtool \
  prom/prometheus:v3.15.0 test rules alerts_test.yml demo-alerts_test.yml

docker compose -p lab4-own-tests --profile tests run --rm --build tests
docker compose -p lab4-own-tests down -v --remove-orphans

docker run --rm --network none -w /app/src --entrypoint python \
  lab1-svcdesk:local -m unittest tests.monitoring_regressions
```

The checker starts fresh Alertmanager instances for the inhibition cases, including the equal-label counterexample. Own alert tests cover healthy SERVER calls with noisy CLIENT calls, failed checkout orders, and latency-only orders. [evidence/lab4-alert-replay.json](evidence/lab4-alert-replay.json) also records the expressions replayed against the real healthy baseline and at fault time. JSON reports are ignored and should be regenerated, then the final checker should name a clean committed tree.

Two checks necessarily show `skip`: `L4-CORE-4.06` and `L4-CORE-5.06` require the grader's sealed-fault key. Local passing tests do not establish the result of those two checks.

## Serve the recording for replay

Use a fresh directory outside the repository. Keep the committed archive unchanged:

```sh
recording_dir="$(mktemp -d /tmp/lab4-recording.XXXXXX)"
tar -xzf incident/tsdb-snapshot.tar.gz -C "$recording_dir"
docker run --rm -d --name lab4-recording -p 127.0.0.1:19090:9090 \
  --user "$(id -u):$(id -g)" -v "$recording_dir:/prometheus" \
  prom/prometheus:v3.15.0 --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/prometheus --storage.tsdb.retention.time=100y
python ai-rca/replay.py --url http://localhost:19090
docker stop lab4-recording
```

`ai-rca/replay.py` uses only the Python standard library and checks all seven predictions at their declared times and at 06:31:23Z, exactly five minutes before onset. To rerun an investigator through the course MCP server, install the package's pinned `agent/requirements.txt` outside this repository, set `PROMETHEUS_URL=http://localhost:19090`, and use the incident window of **2026-10-12 06:22–06:46:47 UTC**. Never use the current evaluation time for the recording. No model credentials or local unpacked TSDB are deliverables.
