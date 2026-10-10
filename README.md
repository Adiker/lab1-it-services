<!-- ai-generated: 45% - Course introduction retained; Codex documented Lab 3 and local verification. -->
# svcdesk - ITSM 2026/27 course repository

This repository was created from the course template. It holds your `svcdesk` service for the whole semester:
built in Lab 1, extended in the later labs. Keep it public, and keep personal data out of it.

## Laboratory 3: run and verify locally

```sh
docker compose --profile observability up -d --build
./itsmlab.sh verify 3 --json report.json
```

This starts the service, seeded index, Prometheus and provisioned Grafana dashboard. The current checker is itsmlab 0.8.0; update it with `docker pull ghcr.io/swasik/itsmlab:2026`. Checker runs are local and never create a receipt or a submission issue. It uses login `adiker`, from `itsmlab.yaml`, for the measured profile. The seeded index has no healthcheck because its image has no shell.

| Local URL | Purpose |
|---|---|
| http://127.0.0.1:18080/health | Service health |
| http://127.0.0.1:18080/kb/search?q=vpn | Knowledge-base search |
| http://127.0.0.1:18080/metrics | Prometheus text histogram |
| http://127.0.0.1:19090 | Prometheus, scraping every 5 seconds |
| http://127.0.0.1:13000/d/svcdesk-lab3 | Provisioned Grafana dashboard, anonymous Viewer |

Published ports bind only to localhost and avoid the host's existing services. The service still listens on port 8080 inside Docker. No startup command installs dependencies. The checker starts its own isolated Compose project, Prometheus and measurement tools; the dashboard services are for local inspection.

`GET /kb/search` accepts a query of 1–200 characters, makes exactly one upstream request with a 3-second timeout, returns the upstream hits unchanged, and maps non-200 responses or transport failures to 502. A single ASGI timer observes every response except /metrics, including validation errors and unmatched routes. Labels contain route templates, never ticket IDs or query text.

Measured initial p99 was 353.4 ms. The final 26-boundary histogram uses 20 ms steps around the slow mode; `slo.md` explains the 99% availability and 99%-within-460-ms objectives, 30-day budgets, and P1/P2 multiwindow alerts. `ai-first-draft.md` preserves the original proposal and refutes both coarse ladders with arithmetic. The published course contract and checks are retained in `specs/MONITORING.md` and `specs/LAB3-CHECKS.md`.

```sh
# Alert syntax, exact firing edges, reset and threshold tests
docker run --rm -v "$PWD/prometheus:/p" -w /p --entrypoint promtool prom/prometheus:v3.15.0 check rules alerts.yml
docker run --rm -v "$PWD/prometheus:/p" -w /p --entrypoint promtool prom/prometheus:v3.15.0 test rules alerts_test.yml
# Existing ticket lifecycle and DORA regressions
docker compose --profile tests run --rm --build tests
# Query forwarding, faults, bounded labels and one observation per response
docker compose run --rm --no-deps tests python -m unittest tests.monitoring_regressions
```

The two Stretch tracks are actual local GenAI inference (`genai/DIFF.md`, spans and reproduction script) and a client/server gap measured through Toxiproxy (`gap/README.md`, `gap.json` and raw oha result). Kubernetes is not implemented; two of three Stretch tracks are required. To remeasure the gap:

```sh
docker compose --profile gap up -d svcdesk kb-index toxiproxy
docker run --rm --network lab1-svcdesk_default -v "$PWD:/work" --entrypoint python ghcr.io/swasik/itsmlab:2026 /work/gap/measure.py
```

The gap script configures the named proxy, warms up for 5 seconds and measures for 60 seconds at 40 requests/second with 64 connections and latency correction. It uses the checker's oha and histogram-delta calculation. The grader independently remeasures for 30 seconds. Retention, alerts and dashboard queries are committed as files; no manual Grafana import is needed.

## Layout

| path | what it is |
|---|---|
| `docker-compose.yml` | the compose contract: service `svcdesk` on 8080, `SVCDESK_TEST_CLOCK`, a named volume; `tests`, `observability` and `gap` profiles |
| `Dockerfile.example` | a Python 3.13 image skeleton; copy to `Dockerfile` or replace for your language |
| `DECISIONS.md` | your reasoning artifact: front matter with the three decisions, three sections, five labels each |
| `itsmlab.yaml` | lab number, baselines, your repository, the submissions repository, the checker image |
| `itsmlab.sh`, `itsmlab.ps1` | wrappers that run the checker container |
| `specs/` | your specifications, published and receipted before any code |
| `src/` | your implementation |
| `.github/workflows/tier-a.yml` | runs the checker on every push and publishes `report.json` as an artifact with a step summary |
| `.gitignore` | keeps `report.json`, virtual environments and local data out of git |
| `.gitattributes` | LF line endings on every system, so the checker's git sees a clean tree on Windows too; keep it |

## Every push runs the checker

The workflow `tier-a` runs on every push and on demand (Actions tab, "Run workflow"). It needs no secrets. The
job is red when a Core spec fails; the step summary shows which checks, and `report.json` is attached as an
artifact.
