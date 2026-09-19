<!-- ai-generated: 90% - Codex compared the contradictory requirements with the published conformance contract; the student chose the service policy. -->
# Convergence report

The specification was checked for internal consistency, observable API behaviour, and alignment with the published Tier A checks. The three conflicts were resolved before implementation so that the service, tests, and `DECISIONS.md` all describe the same behaviour.

## C1 - SLA clock

The conflict between a continuously running P1 clock and a common business calendar converges on the latter. **R-17** retains the published durations, **R-18** defines the DST-aware Warsaw calendar precisely, and **R-19** applies it to P1. This choice avoids mixed-clock operational reporting and matches the admissible `business` vector for a Friday-after-hours P1.

## C2 - ticket finality

The conflict between closed-ticket reopening and audit immutability converges on immutable closure. **R-12** preserves the ordinary lifecycle, **R-14** keeps a seven-day reopen window for tickets that remain resolved, and **R-15** rejects reopening once closure has been explicitly recorded. No transition has two possible results after this choice.

## C3 - VIP priority

The conflict between a strict impact/urgency matrix and VIP elevation converges on controlled elevation. **R-06** computes the base priority, **R-07** promotes only P3/P4 VIP results to P2, and **R-08** prevents a caller from bypassing policy through a supplied priority. A VIP P1 therefore stays P1 and a low-priority VIP ticket becomes P2.

## Boundary review

The remaining requirements are compatible with all three resolutions: **R-04** makes invalid input deterministic, **R-13** centralizes transition conflicts, **R-16** makes every time-dependent check repeatable, **R-21** separates deadline calculation from breach observation, and **R-24** plus **R-25** keep deployment reproducible without runtime network access or host bind mounts.

The converged contract is implementable as a single deterministic service: request validation precedes mutation, priority is computed once on creation, SLA deadlines are stored as instants, and lifecycle actions update only their own timestamps.
