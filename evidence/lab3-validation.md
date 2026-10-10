<!-- ai-generated: 100% - Codex recorded local validation commands and observed results. -->
# Local Laboratory 3 validation, 10 October 2026

This is local Tier A evidence, not a submission receipt or a hosted grade. No submission issue or receipt tag was created. The work is on branch codex/lab3-monitoring.

The first AI proposal was committed as 4ae0ba4 before any measurement. `evidence/lab3-load-initial.txt` preserves the initial published load result for login adiker. Its measured p99 was 0.3534 seconds, and both coarse ladders failed resolution. The final 26-boundary ladder is in `src/svcdesk/monitoring.py`.

`./itsmlab.sh verify 3 --json report.json` with itsmlab 0.8.0 passed all six Core specifications and both selected Stretch specifications (GenAI diff and latency gap). Kubernetes is absent by choice; the required Stretch threshold is any two of three. The complete pre-commit validation measured q = 0.353849015 s, q_kb = 0.362319104 s and histogram p99 = 0.356633 s, with 2,399 responses. The cardinality probe added zero series. All eight alert mutants were killed; both alerts passed fire, quiet and reset probes. AI disclosure covered 30 of 30 checked files. The proxy gap independently remeasured by the checker was 0.1079 s, consistent with the recorded local gap of 0.103667483 s.

The checker image used was ghcr.io/swasik/itsmlab:2026, digest sha256:25423ab2fadd64463a0f4c219062dbaf6ea72d6281bca8b3e9cf79752eb72224. The report written by the latest run is `report.json`, intentionally ignored by git. A verification after the implementation commit is the final clean-tree check; its commit field identifies exactly what was tested.

Additional checks:

- `docker compose --profile tests run --rm --build tests`: ITSMLAB-TESTS: passed=31 failed=0, preserving ticket and DORA behaviour.
- `docker compose run --rm --no-deps tests python -m unittest tests.monitoring_regressions`: four tests passed, including URL encoding, unchanged hits, no cache/retries, validation, timeout/connection errors, response counts and route templates.
- `promtool check rules alerts.yml` and `promtool test rules alerts_test.yml` in prom/prometheus:v3.15.0: passed. Synthetic inputs exercise exact firing edges, recovery and both sides of each threshold, with ticket-route noise.
- Local Prometheus target svcdesk reports up with no scrape error; Grafana 13.2.3 loads the provisioned four-panel dashboard with real time series. Percent panels use a fixed fraction range 0..1.

The local stack remains available at service port 18080, Prometheus port 19090 and Grafana port 13000, bound to localhost. Toxiproxy uses 18474/18666. The temporary local Ollama helper lab3-genai-ollama is stopped; its exported real inference span remains in genai/spans.json. No other host service was stopped or reconfigured.
