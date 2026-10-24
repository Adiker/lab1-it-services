<!-- ai-generated: 100% - Codex recorded actual local validation and its scope for Laboratory 4. -->
# Laboratory 4 validation

Validation uses itsmlab 0.8.6 and the recorded path for login `adiker`, assigned `lab4-rec-4`. Source SHA-256 values are in `lab4-analysis.json`; the snapshot, ticket and primary transcript were compared byte-for-byte with the supplied files. The archive stays packed in the repository.

The incident recomputation exits 0 and supplies all four timestamps without warnings: onset 06:36:23Z, detection 06:39:19Z, acknowledgement 06:40:09Z, recovery 06:44:19Z, on 2026-10-12. MTTD is 176 seconds, MTTA 50 seconds, MTTR 476 seconds.

The two ledgers contain seven testable predictions. `python ai-rca/replay.py` confirms that every prediction is true at 06:41:00Z and false at the prescribed baseline, 06:31:23Z. Every quoted hypothesis was checked against its named transcript. `lab4-ledger-replay.json` records the actual vectors.

`promtool test rules alerts_test.yml demo-alerts_test.yml` passes for both the preserved Lab 3 rules and the new Lab 4 scenarios. The new cases cover healthy SERVER traffic despite noisy load-generator CLIENT errors, failing checkout orders, and slow checkout with no error series. The three prospective shop expressions also return empty across the real ten-minute healthy baseline; their fault-time results are in `lab4-alert-replay.json`.

The Compose own-test runner reports **31 passed, 0 failed**. The isolated monitoring regression suite reports **4 tests, OK**. The preserved Lab 3 checker reports **Core 6/6 and Stretch 3/3, PASS**. No application or old monitoring implementation was changed for Lab 4.

An extra historical Lab 1 diagnostic found API conformance, decision structure/consistency and all three Stretch bundles passing. Its old global no-bind-mount rule rejects the observability mounts introduced and explicitly allowed by Lab 3. That historical compose check is not the current Lab 4 contract; Lab 4 checks binds on svcdesk, which passes. No unrelated observability rewrite was made to satisfy the superseded Lab 1 infrastructure restriction.

The Kubernetes experiment retained raw k8sgpt baseline and candidate output after at least five minutes. Both have the same 7 ConfigMap warnings; 30 application pods remained Ready with zero restarts, while the later sample captured payment and checkout errors. The chosen resource flag is explicitly a hypothesis, not decoded ground truth.

The completed Lab 4 checker reports **Core 5/5 and Stretch 3/3, PASS**, with no fail/error checks. Its AI-disclosure advisory confirms **34 of 34** covered files. The final checker is also run after the commit to verify a clean tree. Its generated `report.json` is ignored. Two sealed-fault checks necessarily remain `skip` locally: 4.06 and 5.06. They require the course grader's key, so local results cannot guarantee their verdicts.

No issue, regulator notification or submission receipt was created. Local action identifiers in the postmortem are references for subsequent laboratory work.
