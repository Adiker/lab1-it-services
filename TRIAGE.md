---
lab5_triage:
  image: ghcr.io/adiker/lab1-it-services@sha256:31aac0e0b51fb5482a2d5b56e44ed575f698aa3b097da4b03375c093c9b6ed42
  sarif_receipt: 0
---
<!-- ai-generated: 100% - Codex reviewed scanner results and recorded the decisions; the canary receipt and analysis remain pending. -->
# Triage

The image uses a pinned Python base, updates OS packages and removes pip after installation. The 2026-11-14 main run reported no dependency findings in Trivy, Grype or OSV-Scanner and no gitleaks findings. The image gate passed. Both the provenance and SBOM attestations for the digest above were verified with `gh attestation verify`. The receipt number is zero until an issue is explicitly authorized and receipted.

| Tool | Rule | Decision | Reason |
|---|---|---|---|
| semgrep | dockerfile.security.missing-user.missing-user | accept | Dockerfile runs as root; this lab image writes to /data. A non-root user and volume ownership need a coordinated deployment change. |
| semgrep | python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected | accept | ai-rca/replay.py takes an operator-provided base URL, while gap/measure.py constructs the local Toxiproxy URL. Run these diagnostic scripts only with trusted inputs. |
| semgrep | python.lang.security.audit.insecure-transport.urllib.insecure-request-object.insecure-request-object | accept | gap/measure.py uses HTTP to the lab's Toxiproxy service over the isolated Compose network; it is measurement traffic, not an external endpoint. |
| semgrep | python.lang.security.audit.insecure-transport.urllib.insecure-urlopen.insecure-urlopen | accept | gap/measure.py scrapes the lab metrics endpoint over HTTP on the Compose network; transport is not encrypted. |
| semgrep | yaml.kubernetes.security.run-as-non-root.run-as-non-root | accept | k8s/workloads.yaml is an isolated lab deployment and does not enforce a non-root UID; hardening requires checking both images and writable paths. |
| semgrep | yaml.kubernetes.security.allow-privilege-escalation-no-securitycontext.allow-privilege-escalation-no-securitycontext | accept | k8s/workloads.yaml lacks an explicit privilege escalation restriction for both containers; retain as a lab limitation pending deployment hardening. |
| semgrep | python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query | false-positive | In store.py insert uses constant column names and parameterized values; update callers supply fixed keyword names and parameterized values. semgrep/rules.py is a deliberately vulnerable test example, not application code. |

## Bake-off

The published practice set gives the expected matrix, but its numbers are not the results for the assigned canary. The canary's SARIF and withheld labels are needed before comparing the detectors or choosing gates for that set. Seeded defects make measured recall optimistic relative to real-world defects. This section will be completed once the course has receipted the SARIF and revealed the labels.
