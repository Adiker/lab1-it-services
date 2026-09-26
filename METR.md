---
actual_minutes: 3.62
completed_at: "2026-09-26T17:56:15Z"
---
<!-- ai-generated: 100% - Codex recorded the observed elapsed time and described the completed regression feature. -->

# METR n=1 outcome

The prediction in `PREDICTION.md` was receipted at 2026-09-26T17:52:38Z in issue #176, before any commit or file creation at the declared feature path `src/tests/dora_regressions.py`. I predicted 12 minutes to implement a deterministic DORA regression suite, connect it to the Compose test runner, review it, and obtain one successful local test-profile run. The first successful run ended at 2026-09-26T17:56:15Z. The elapsed 217 seconds are 3.62 minutes when rounded to two decimal places. The actual/predicted ratio is **0.30** (3.62 / 12), a direction-neutral report of the observed result.

I added seven HTTP-level cases covering the half-open deployment window, equivalent UTC and offset windows, first-occurrence duplicate events, malformed cross-references, a revert cycle, touching incident intervals, and redeployment of the same commit. The new cases run with the existing tests under the Compose `tests` profile. Its successful output was `ITSMLAB-TESTS: passed=31 failed=0`.

The first direct Compose invocation never reached the tests because host port 8080 was already occupied by another process. I did not stop or reconfigure that process. I removed only the temporary Compose resources from that failed invocation and ran the same profile in an isolated project with a temporary override that did not publish the service port. The containers still communicated through the project network; that run passed. The time spent diagnosing and rerunning after the port collision is included in the actual duration. AI drafted the code and prose, while the measured time and test result come from the command output and receipt timestamps. This is one observation for one feature, not a general claim about AI productivity.
