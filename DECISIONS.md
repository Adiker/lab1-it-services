---
svcdesk_decisions:
  C1: business       # wallclock | business
  C2: immutable      # reopen | immutable
  C3: vip            # matrix | vip
---
<!-- ai-generated: 100% - Codex selected the three admissible service policies and drafted their rationale. -->

# Decisions

## C1 - SLA clock for P1

**Decision:** Keep R-13: P1 uses the Europe/Warsaw business-hours clock, exactly as priorities P2 through P4 do.

**Rejected alternative:** Reject only the around-the-clock clause of R-14; its 15-minute acknowledgement and 4-hour resolution targets remain unchanged.

**Reason:** One operational calendar makes deadlines explainable, staffing-aligned, and consistent across dashboards without a special after-hours exception.

**Service owner:** The service-level manager owns this choice because that role defines measurable SLA commitments and ensures support capacity can meet them.

**Customer outcome:** Reporters receive predictable deadlines tied to staffed hours rather than promises that may expire while no support team is available.

## C2 - Closed tickets and reopening

**Decision:** Keep R-09: a closed ticket is immutable; retain R-10's seven-day reopen window only while the ticket remains resolved.

**Rejected alternative:** Reject only R-10's promise to reopen from `closed`; reopening a resolved ticket within seven days remains supported.

**Reason:** Closure is an explicit audit boundary. A new ticket preserves the historical record and makes renewed demand visible instead of rewriting a completed case.

**Service owner:** The process owner for incident management signs off because that role governs lifecycle controls, auditability, and reporting integrity.

**Customer outcome:** Customers retain a trustworthy history; if work is needed after closure, a fresh ticket makes ownership and SLA timing unambiguous.

## C3 - VIP reporters and the priority matrix

**Decision:** Keep R-06: a VIP reporter elevates a matrix-derived P3 or P4 ticket to P2, while P1 and P2 remain unchanged.

**Rejected alternative:** Reject only R-05's "nothing else" clause; retain the R-04 matrix as the base and prohibit client-requested priority.

**Reason:** The capped promotion improves response for important stakeholders without allowing VIP status to manufacture P1 emergencies or override real impact.

**Service owner:** The service owner approves this policy because that role balances business relationship commitments against operational capacity and fairness.

**Customer outcome:** VIP reporters receive faster handling for otherwise low-priority issues, while genuine high-impact incidents still keep the highest precedence.
