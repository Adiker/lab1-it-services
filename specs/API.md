<!-- ai-generated: 90% - Codex drafted the contract from the published checker; the student selected and reviewed the conflict resolutions. -->
# svcdesk API specification

## Purpose and decisions

`svcdesk` is a JSON HTTP service for creating and progressing service-desk tickets. The contract deliberately resolves the three contradictory requirement pairs as follows:

- C1 = `business`: every priority, including P1, consumes SLA time only during Warsaw business hours.
- C2 = `immutable`: a closed ticket is an immutable audit record and cannot be reopened.
- C3 = `vip`: VIP reporters raise a matrix-derived P3 or P4 ticket to P2.

All timestamps are timezone-aware ISO 8601 instants. Responses may use `Z` or an equivalent UTC offset.

## Functional requirements

### Service and ticket resources

- **R-01 Health.** `GET /health` returns HTTP 200 with JSON `{ "status": "ok" }`. An unknown route returns HTTP 404.
- **R-02 Create.** `POST /tickets` accepts `title`, optional `description`, `reporter`, `impact`, and `urgency`; it returns HTTP 201 and the created ticket.
- **R-03 Ticket shape.** A returned ticket contains a non-empty opaque string `id`, `title`, `description`, `reporter.name`, integer `impact` and `urgency`, computed `priority`, `state`, `created_at`, and `sla.ack_due_at` plus `sla.resolve_due_at`.
- **R-04 Validation.** `title` is required and 1-200 characters. `impact` and `urgency` are integers from 1 through 3. Invalid input returns HTTP 400 or 422. A missing title error has a top-level JSON `error` member.
- **R-05 Identity.** Every create operation generates a distinct ID. IDs are opaque and are matched after URL decoding, without assumptions about UUID formatting.
- **R-06 Priority matrix.** Non-VIP priority is `(1,1)=P1`, `(1,2)=P2`, `(1,3)=P3`, `(2,1)=P2`, `(2,2)=P3`, `(2,3)=P4`, `(3,1)=P3`, `(3,2)=P4`, `(3,3)=P4`.
- **R-07 VIP resolution.** When `reporter.vip` is true, a matrix result of P3 or P4 is promoted to P2; P1 and P2 remain unchanged. Missing `vip` is equivalent to false.
- **R-08 Server authority.** Any client-supplied `priority` field is ignored; priority is always computed from impact, urgency, and the selected VIP resolution.
- **R-09 Read.** `GET /tickets/{id}` returns HTTP 200 and the full ticket, or HTTP 404 with a top-level JSON `error` member when the ticket does not exist.
- **R-10 List.** `GET /tickets` returns a JSON array. Optional `state` and `priority` query parameters filter the returned collection and can be used independently or together.

### State machine

- **R-11 States.** The lifecycle states are `new`, `acknowledged`, `in_progress`, `resolved`, and `closed`; every new ticket starts in `new`.
- **R-12 Normal transitions.** `POST /tickets/{id}/ack` changes `new` to `acknowledged` and records `acknowledged_at`; `/start` changes `acknowledged` to `in_progress`; `/resolve` changes `in_progress` to `resolved` and records `resolved_at`; `/close` changes `resolved` to `closed` and records `closed_at`.
- **R-13 Invalid transitions.** An action outside the transition graph returns HTTP 409, including repeated acknowledgement, start on new, resolve on new or acknowledged, close on new, and reopen on new.
- **R-14 Reopen resolved.** `POST /tickets/{id}/reopen` changes a resolved ticket to `in_progress` when the supplied clock is no later than seven calendar days after `resolved_at`; later requests return 409.
- **R-15 Closed-ticket resolution.** Closed tickets are immutable. Reopening a closed ticket always returns HTTP 409, even inside the seven-day resolved-ticket window.

### Clock and SLA

- **R-16 Test clock.** When `SVCDESK_TEST_CLOCK=1`, every endpoint uses a valid ISO 8601 `X-Test-Clock` request header as its current instant. A malformed header on ticket creation returns HTTP 400 or 422. Without the header, real UTC time may be used.
- **R-17 Targets.** SLA acknowledgement/resolution targets are P1: 15 minutes/4 hours; P2: 1 hour/8 hours; P3: 4 hours/24 hours; P4: 8 hours/72 hours.
- **R-18 Business calendar.** Business time is Monday-Friday in the half-open window `[08:00,16:00)` in `Europe/Warsaw`, DST-aware; public holidays remain business days. Creation outside a window aligns to the next opening. A target ending exactly at 16:00 is due at 16:00 that day.
- **R-19 P1 conflict resolution.** P1 uses the business calendar, the same as P2-P4. Thus a P1 created Friday 2026-10-16 at 17:00 Warsaw time is due for acknowledgement Monday 08:15 and resolution Monday 12:00 Warsaw time.
- **R-20 Due instants.** Creation computes acknowledgement and resolution deadlines independently from `created_at` and the ticket's computed priority; returned deadlines are UTC instants.
- **R-21 SLA status.** `GET /tickets/{id}/sla` returns `ack_breached`, `resolve_breached`, and `paused`. A completed milestone is breached only when its recorded completion instant is after its deadline; an incomplete milestone is breached only when current time is after its deadline. `paused` is true when the ticket's applicable SLA clock is outside business time.

### Errors, persistence, and deployment

- **R-22 Error contract.** Domain errors and missing resources return a JSON object with a top-level non-empty `error` string. Unknown framework routes may use the framework's normal 404 body.
- **R-23 Persistence.** Ticket state is stored in SQLite at `SVCDESK_DB` (default `/data/svcdesk.db`) and survives process restarts when `/data` is a named Docker volume.
- **R-24 Compose contract.** Root Compose configuration defines a buildable `svcdesk` service listening on container port 8080, enables the test clock, has a readiness healthcheck, and uses no host bind mounts or bind-like volume driver options.
- **R-25 Reproducible build and tests.** All runtime and test dependencies are installed at image build time. The running service needs no network access. A `tests` profile executes at least ten deterministic checks and ends stdout with `ITSMLAB-TESTS: passed=<n> failed=0` when successful.

## Published conformance vectors

The implementation must satisfy the published T1-T5 and T7 vectors: P1 at `2026-10-14T10:00:00Z` -> `10:15Z`/`14:00Z`; P2 at the same instant -> `11:00Z`/next-day `10:00Z`; P3 at `2026-10-16T13:30:00Z` -> Monday `09:30Z`/Wednesday `13:30Z`; P2 created on Saturday `2026-10-17T10:00:00Z` -> Monday `07:00Z`/`14:00Z`; and P4 at `2027-01-14T14:30:00Z` -> next-day `14:30Z`/`2027-01-27T14:30:00Z`.
