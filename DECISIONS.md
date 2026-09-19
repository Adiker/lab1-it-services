---
svcdesk_decisions:
  C1: business       # wallclock | business
  C2: immutable      # reopen | immutable
  C3: vip            # matrix | vip
---
<!-- ai-generated: 90% - Codex drafted the rationale after the student selected the three service-policy resolutions. -->

# Decisions

## C1 - SLA clock for P1

**Decision:** P1 uses the Europe/Warsaw business-hours clock, exactly as priorities P2 through P4 do.

**Rejected alternative:** A continuously running wall clock for P1 was rejected, although it would produce shorter after-hours deadlines.

**Reason:** One operational calendar makes deadlines explainable, staffing-aligned, and consistent across dashboards without a special after-hours exception.

**Service owner:** The service-level manager owns this choice because that role defines measurable SLA commitments and ensures support capacity can meet them.

**Customer outcome:** Reporters receive predictable deadlines tied to staffed hours rather than promises that may expire while no support team is available.

## C2 - Closed tickets and reopening

**Decision:** A closed ticket is immutable and cannot be reopened; only a ticket still in resolved state has the seven-day reopen window.

**Rejected alternative:** Reopening a closed ticket within the same seven-day window was rejected because it weakens the meaning of formal closure.

**Reason:** Closure is an explicit audit boundary. A new ticket preserves the historical record and makes renewed demand visible instead of rewriting a completed case.

**Service owner:** The process owner for incident management signs off because that role governs lifecycle controls, auditability, and reporting integrity.

**Customer outcome:** Customers retain a trustworthy history; if work is needed after closure, a fresh ticket makes ownership and SLA timing unambiguous.

## C3 - VIP reporters and the priority matrix

**Decision:** A VIP reporter elevates a matrix-derived P3 or P4 ticket to P2, while P1 and P2 remain at their existing priority.

**Rejected alternative:** Applying the impact-and-urgency matrix without any VIP adjustment was rejected because it ignores explicitly agreed stakeholder criticality.

**Reason:** The capped promotion improves response for important stakeholders without allowing VIP status to manufacture P1 emergencies or override real impact.

**Service owner:** The service owner approves this policy because that role balances business relationship commitments against operational capacity and fairness.

**Customer outcome:** VIP reporters receive faster handling for otherwise low-priority issues, while genuine high-impact incidents still keep the highest precedence.
