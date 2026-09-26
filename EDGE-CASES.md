---
lab2_edge_cases:
  E1: {rule: R-08, count: 3}
  E2: {rule: R-06, count: 2}
  E3: {rule: R-09, count: 4}
  E4: {rule: R-10, count: 4}
  E5: {rule: R-12, count: 1}
  E6: {rule: R-13, count: 11}
---
<!-- ai-generated: 100% - Codex inspected the practice events and wrote the rule explanations and gaming analysis. -->

# Edge cases in the practice event log

## E1 - clock skew produces a negative lead time

- What the log contains: Three commit and deployment pairs have commit instants after their successful production deployment; for example, sha-0040 follows DEP-0012 by almost fourteen minutes.
- What a default definition would have done: Dropping those pairs would hide clock skew and change the median's sample, while retaining their negative durations could make delivery seem faster than physically possible.
- Why the rule is defensible: R-08 keeps all three deliveries but clamps each duration to zero, preserving the delivered-work count and making the timestamp anomaly visible separately.

## E2 - a revert of a revert

- What the log contains: sha-0070 reverts sha-0069, and sha-0071 reverts sha-0070; both revert commits inherit the original change identity transitively.
- What a default definition would have done: Treating every commit as a new change would inflate the number of independent pieces of work and distort the ground-truth change lead time.
- Why the rule is defensible: R-06 follows the entire revert chain to the original change, so two corrective commits are visible without claiming that they created two new changes.

## E3 - a hotfix that never touched `main`

- What the log contains: Four distinct carried commits, including sha-0019 on hotfix/2609, came from branches other than `main` and still reached production in the window.
- What a default definition would have done: A main-only filter would omit those deliveries and falsely suggest that the hotfix work did not reach users.
- Why the rule is defensible: R-09 measures production delivery from deployment evidence; a repository branch name is not evidence that a deployed change was absent.

## E4 - a deployment with zero linked commits

- What the log contains: DEP-0026, DEP-0032, DEP-0043 and DEP-0044 are production deployments in the window with empty commit lists; two succeeded and two failed.
- What a default definition would have done: Removing empty deployments to avoid an empty lead-time calculation would also erase two failures and shrink the denominator of multiple metrics.
- Why the rule is defensible: R-10 lets these deployments contribute no lead-time pairs while retaining their real operational outcomes in frequency, failure rate and rework rate.

## E5 - a deployment that failed and never recovered

- What the log contains: DEP-0015 failed and is covered by INC-0004, which has an opening event but no resolution event in the log.
- What a default definition would have done: Closing the incident at the window boundary would invent a recovery time, while excluding the failure entirely would understate instability.
- Why the rule is defensible: R-12 leaves the failure out of the recovery median, reports one open failure and still includes it in the failure-rate numerator.

## E6 - overlapping incidents

- What the log contains: Incident intervals intersect in eleven unordered pairs; the unresolved INC-0004 overlaps several later incidents, including INC-0005.
- What a default definition would have done: Merging intervals or adding incident wall-clock durations would confuse concurrent response work with the recovery time of each failed deployment.
- Why the rule is defensible: R-13 reports overlap separately and measures recovery per failed deployment using its selected covering incident's resolution instant.

## Gaming demonstration

I exploited R-11, `deployment_frequency_per_day`. I moved the successful production deployments DEP-0028 and DEP-0031 beyond the observation window, delaying eight changes that were already in the base log. I then added thirteen successful production deployments with no linked commits inside the window. These could represent repeated configuration-only or no-op releases counted as deployments under R-10. No original event was deleted, no original deployment moved earlier, and the original commits and incidents remain intact.

The visible frequency rises from 2.0 to 2.52381 deployments per day, an improvement of 26.19%, clearing R-20's 25% margin. Yet the base work delivered within the window falls from 65 to 57 changes, a decline of 12.31%, clearing R-21's harm margin. A team rewarded for deployment count could schedule easy releases and postpone risky feature releases; its throughput dashboard and the people paid against it would look better while users wait longer for the eight real changes.
