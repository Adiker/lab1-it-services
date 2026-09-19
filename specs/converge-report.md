<!-- ai-generated: 100% - Codex selected the service policy and compared the contradictory requirements with the conformance contract. -->
# Convergence report

The specification was checked for internal consistency, observable API behaviour, and alignment with the published Tier A checks. The three conflicts were resolved before implementation so that the service, tests, and `DECISIONS.md` all describe the same behaviour.

## C1 - SLA clock

The conflict is between **R-13**, which pauses every SLA outside Warsaw business hours, and the around-the-clock clause of **R-14** for P1. The converged choice keeps R-13 for every priority and retains R-14's 15-minute and 4-hour durations while rejecting only its wall-clock clause. This avoids mixed-clock operational reporting and matches the admissible `business` vector for a Friday-after-hours P1.

## C2 - ticket finality

The conflict is between immutable closure in **R-09** and the closed-ticket part of the reopen promise in **R-10**. The converged choice keeps R-09, rejects only the word `closed` from R-10, and preserves R-10 plus **R-11** for a ticket that remains resolved. Formal closure is therefore an audit boundary while the seven-day resolved-ticket recovery path remains available.

## C3 - VIP priority

The conflict is between the "nothing else" clause of **R-05** and the VIP floor required by **R-06**. The converged choice retains the **R-04** matrix as the base, rejects only that clause of R-05, and then applies R-06 by promoting VIP P3/P4 results to P2. A caller still cannot request priority directly, a VIP P1 stays P1, and a low-priority VIP ticket becomes P2.

## Boundary review

The remaining requirements are compatible with all three resolutions: **R-08** centralizes transition conflicts, **R-16** defines breach and pause, **R-20** makes invalid input deterministic, **R-21** makes every time-dependent check repeatable, and **R-22** plus **R-24** keep deployment reproducible without runtime network access or host bind mounts.

The converged contract is implementable as a single deterministic service: request validation precedes mutation, priority is computed once on creation, SLA deadlines are stored as instants, and lifecycle actions update only their own timestamps.
