<!-- ai-generated: 100% - Codex derived the ordered task list and traceability from the course requirements. -->
# Implementation tasks

- [ ] T01 Create the FastAPI package, health endpoint, JSON error handlers, pinned dependencies, Dockerfile, and Compose healthcheck (R-01, R-02, R-22, R-24, R-25).
- [ ] T02 Define strict create models and full ticket output, including defaults, ignored server fields, UUIDs, reporter e-mail/VIP, and `related_to` (R-03, R-17, R-18, R-20).
- [ ] T03 Add SQLite schema/repository and named-volume persistence at `SVCDESK_DB` (R-23).
- [ ] T04 Implement the priority matrix and C3=`vip`; verify client priority cannot override it (R-04, R-05, R-06).
- [ ] T05 Implement list/get endpoints and exact state/priority filters (R-19, R-25).
- [ ] T06 Implement the request-local RFC 3339 clock, malformed/naive rejection, disabled mode, and deliberately non-monotonic request support (R-21).
- [ ] T07 Implement lifecycle actions, 409/404 errors, C2=`immutable`, resolved reopen boundary, timestamp clearing, and unchanged SLA deadlines (R-07, R-08, R-09, R-10, R-11).
- [ ] T08 Implement Warsaw business-time arithmetic, C1=`business`, exact closing tie, DST-safe T1-T8 vectors, and UTC output (R-12, R-13, R-14, R-17).
- [ ] T09 Implement `/sla` milestone breach and open-ticket pause behaviour, including reopened resolution status (R-15, R-16).
- [ ] T10 Add at least ten deterministic HTTP tests under the Compose `tests` profile, using only `SVCDESK_URL` and printing the required final summary line.
- [ ] T11 Run local static/unit checks, Compose profile tests, and the complete published checker; fix until Core and all three Stretch items satisfy their contracts.
- [ ] T12 After an accepted specs receipt, commit/push implementation, re-run from the clean commit, create immutable annotated `lab1/v1`, push it, and request the submission receipt.
