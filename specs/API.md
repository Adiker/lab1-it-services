<!-- ai-generated: 100% - Codex selected the admissible resolutions and structured the course requirements and interface contract. -->
# svcdesk implementation specification

## Scope and chosen resolutions

`svcdesk` is a JSON-only HTTP service on port 8080. This specification preserves the identifiers and meanings from the course `REQUIREMENTS.md`; the course `API.md` is authoritative where it gives more precise interface behaviour.

The selected conflict resolutions are:

- C1 = `business`: keep R-13; reject only the around-the-clock clause of R-14 while keeping its P1 durations.
- C2 = `immutable`: keep R-09; reject only reopening from `closed` in R-10 while retaining reopening from `resolved`.
- C3 = `vip`: keep R-06; in R-05 retain the matrix as the base but reject its "nothing else" clause for VIP reporters.

## Requirements traceability

- **R-01 HTTP/JSON.** The service listens on container port 8080. Every response, including errors and unknown paths, is JSON with `application/json`; request bodies are JSON.
- **R-02 Health.** `GET /health` returns HTTP 200 with at least `{"status":"ok","service":"svcdesk"}`.
- **R-03 Ticket input/model.** `title` is required with 1-200 characters; `description` defaults to `""` and has at most 4000 characters. `reporter.name` is required with 1-100 characters; `reporter.email` defaults to null and `reporter.vip` to false. `impact` and `urgency` are required integers in 1..3. `related_to` is optional/null and is not existence-validated in Lab 1.
- **R-04 Priority matrix.** The base priority is `(1,1)=P1`, `(1,2)=P2`, `(1,3)=P3`, `(2,1)=P2`, `(2,2)=P3`, `(2,3)=P4`, `(3,1)=P3`, `(3,2)=P4`, `(3,3)=P4`.
- **R-05 Server-owned priority.** The matrix is always the starting point. A client-supplied `priority`, like every other server-owned or unknown field, is silently ignored.
- **R-06 VIP resolution.** With C3=`vip`, a VIP matrix result of P3 or P4 is promoted to P2; P1 and P2 remain unchanged. The VIP flag is stored in the returned reporter.
- **R-07 Lifecycle.** States are `new`, `acknowledged`, `in_progress`, `resolved`, and `closed`. New tickets start in `new`. `/ack`, `/start`, `/resolve`, and `/close` advance exactly one step and successful actions return the full ticket. Acknowledge, resolve, and close record their corresponding event timestamps.
- **R-08 Invalid transitions.** Actions outside the graph return HTTP 409 with a top-level `error` object. Actions on an unknown ticket return HTTP 404 with a top-level `error` object.
- **R-09 Immutable closure.** With C2=`immutable`, a closed ticket cannot be reopened. Further work is represented by a new ticket whose `related_to` points to the closed ticket.
- **R-10 Reopen resolution.** A resolved ticket may be reopened while `now <= resolved_at + 7 days`; it returns to `in_progress`. The C2 choice removes only reopening from `closed`.
- **R-11 Reopen effects.** Reopen outside the applicable seven-day window returns 409. A successful reopen clears `resolved_at` and `closed_at`, preserves the original SLA deadlines, and does not restart either target.
- **R-12 SLA targets.** From ticket creation, acknowledgement/resolution targets are P1 15 minutes/4 hours, P2 1 hour/8 hours, P3 4 hours/24 hours, and P4 8 hours/72 hours.
- **R-13 Business clock.** Business time is Monday-Friday in the half-open window `[08:00,16:00)` in `Europe/Warsaw`, DST-aware, with public holidays treated as ordinary business days. Outside time aligns forward to the next opening; an exact tie at 16:00 remains due at 16:00 that day.
- **R-14 P1 resolution.** P1 retains its 15-minute and 4-hour targets, but C1=`business` applies the R-13 business clock to both rather than the rejected around-the-clock clause. P2-P4 also use the business clock.
- **R-15 SLA endpoint.** `GET /tickets/{id}/sla` returns `priority`, `ack_due_at`, `resolve_due_at`, `ack_breached`, `resolve_breached`, and `paused`; unknown IDs return 404.
- **R-16 Breach/pause.** A completed milestone is breached only when its recorded event instant is later than the deadline; an incomplete milestone is breached only when `now` is later. Equality is not a breach. `paused` is true only while the ticket is neither resolved nor closed, its resolution target uses business time, and `now` is outside a business window. A reopened ticket is unresolved again against its original deadline.
- **R-17 Timestamps.** All API timestamps are RFC 3339 instants and are emitted in UTC with a `Z` suffix. Comparisons use instants rather than timestamp strings.
- **R-18 Identity.** Every create generates an opaque, unique, non-empty server-owned string ID; no client-supplied ID is accepted.
- **R-19 Listing.** `GET /tickets` returns all matching tickets in one JSON array, any order, with optional exact-match `state` and `priority` filters and no pagination.
- **R-20 Validation and ignored fields.** Invalid input returns HTTP 400 or 422 with a top-level `error` object. Server-owned fields (`id`, `priority`, `state`, timestamps, `sla`) and unknown fields are ignored, not rejected.
- **R-21 Per-request test clock.** If `SVCDESK_TEST_CLOCK` is `1` or `true`, a valid offset-aware RFC 3339 `X-Test-Clock` supplies `now` for that request only; malformed or naive values return 400/422. Without it, real UTC is used. If the feature is disabled, the header is ignored. Clocks are not required to be monotonic and are never compared between requests.
- **R-22 Compose/runtime.** Root Compose defines a service named `svcdesk` with a repository `build:` context, port 8080, `SVCDESK_TEST_CLOCK: "1"`, no host bind mounts (including bind-like named-volume options), and no runtime egress dependency. All dependencies are installed at build time.
- **R-23 Persistence.** SQLite data is stored at `SVCDESK_DB` (default `/data/svcdesk.db`) on a named Compose volume so tickets survive service-container restarts.
- **R-24 Readiness.** `docker compose up --wait svcdesk` succeeds and `GET /health` answers 200 within the shared 120-second window. A healthcheck performs the readiness probe.
- **R-25 Not found.** Unknown paths return 404 with a JSON body; unknown ticket IDs return 404 with a JSON body containing a top-level `error` object.

## Exact HTTP model

Creation uses `POST /tickets` and returns HTTP 201. Read endpoints are `GET /tickets`, `GET /tickets/{id}`, and `GET /tickets/{id}/sla`. Actions are `POST /tickets/{id}/ack`, `/start`, `/resolve`, `/close`, and `/reopen`, returning HTTP 200 with the full ticket when successful. A wrong method on a known path may return 404 or 405.

A returned ticket contains `id`, `title`, `description`, `reporter` (`name`, `email`, `vip`), `impact`, `urgency`, computed `priority`, `state`, `created_at`, nullable `acknowledged_at`, `resolved_at`, and `closed_at`, nullable `related_to`, and `sla` (`ack_due_at`, `resolve_due_at`).

Domain and validation errors use a top-level object, for example `{"error":{"code":"validation","message":"title is required"}}`. Specific error-code strings are recommended but are not graded in Lab 1.

## SLA conformance vectors

The business-clock implementation must reproduce all eight course vectors, including those not individually asserted by Tier A:

| vector | priority | created | business ack due | business resolve due |
|---|---|---|---|---|
| T1 | P1 | 2026-10-14T10:00:00Z | 2026-10-14T10:15:00Z | 2026-10-14T14:00:00Z |
| T2 | P3 | 2026-10-16T13:30:00Z | 2026-10-19T09:30:00Z | 2026-10-21T13:30:00Z |
| T3 | P1 | 2026-10-16T15:00:00Z | 2026-10-19T06:15:00Z | 2026-10-19T10:00:00Z |
| T4 | P2 | 2026-10-17T10:00:00Z | 2026-10-19T07:00:00Z | 2026-10-19T14:00:00Z |
| T5 | P4 | 2027-01-14T14:30:00Z | 2027-01-15T14:30:00Z | 2027-01-27T14:30:00Z |
| T6 | P1 | 2027-01-15T15:50:00Z | 2027-01-18T07:15:00Z | 2027-01-18T11:00:00Z |
| T7 | P2 | 2026-10-14T10:00:00Z | 2026-10-14T11:00:00Z | 2026-10-15T10:00:00Z |
| T8 | P3 | 2026-10-23T13:00:00Z | 2026-10-26T10:00:00Z | 2026-10-28T14:00:00Z |

T8 crosses the weekend in which Warsaw leaves daylight-saving time; business hours are consumed in local wall-clock windows and converted back to UTC. The image therefore must include the IANA `Europe/Warsaw` time-zone database.

## Own-test contract

The optional Compose `tests` service is enabled only by `profiles: ["tests"]`, reads the service address from `SVCDESK_URL` (default `http://svcdesk:8080`), depends on a healthy service, and exercises at least ten deterministic cases. Its final stdout line is exactly `ITSMLAB-TESTS: passed=<n> failed=0`. The test image is built before egress is blocked and contacts no host other than `SVCDESK_URL` at runtime.
