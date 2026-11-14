<!-- ai-generated: 100% - Codex documented local changes; scanner findings and the canary results remain to be reviewed. -->
# Triage

The image uses a pinned Python base, updates operating system packages at build time and removes pip after installing the application dependencies. On 2026-11-14, local Trivy 0.74.0 scans found no HIGH or CRITICAL dependency vulnerabilities in the repository and no fixable HIGH or CRITICAL vulnerabilities in the built image. The other scanner reports and the GitHub Actions run still need review.

| Tool | Rule | Decision | Reason |
|---|---|---|---|

## Bake-off

The published practice set gives an exact match to its expected matrix, but these practice numbers are not the results for the assigned canary. The canary's SARIF and its withheld labels are needed before drawing conclusions about the detectors or choosing a gate for that set.

The GHCR image digest, SARIF receipt, scanner findings and canary analysis must be added after their corresponding runs and receipt exist.
