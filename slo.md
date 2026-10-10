---
lab3_slo:
  service: svcdesk
  route: /kb/search
  window: 30d
  slis:
    availability:
      objective: 0.99
      good: sum(rate(http_server_request_duration_seconds_count{job="svcdesk", http_route="/kb/search", http_response_status_code!~"5.."}[5m]))
      valid: sum(rate(http_server_request_duration_seconds_count{job="svcdesk", http_route="/kb/search"}[5m]))
      error_budget:
        fraction: 0.01
        minutes: 432
    latency:
      objective: 0.99
      threshold_seconds: 0.46
      good: sum(rate(http_server_request_duration_seconds_bucket{job="svcdesk", http_route="/kb/search", le="0.46"}[5m]))
      valid: sum(rate(http_server_request_duration_seconds_count{job="svcdesk", http_route="/kb/search"}[5m]))
      error_budget:
        fraction: 0.01
        minutes: 432
  alerts:
  - alert: KbSearchErrorsBurnFast
    sli: availability
    burn_rate: 14.4
    long_window: 1h
    short_window: 5m
  - alert: KbSearchErrorsBurnSlow
    sli: availability
    burn_rate: 6
    long_window: 6h
    short_window: 30m
---
<!-- ai-generated: 100% - Codex selected and defended objectives, buckets, budgets and alert routing from measured data. -->
# Knowledge-base search SLO

The user needs a search result while diagnosing a ticket. The initial open-loop run for Adiker received 2,399 responses in 60 seconds, with three 502s: measured availability was 2,396 / 2,399 = 99.875%. A 99% objective allows for the index's own unavoidable failures and some service degradation, while a 99.9% objective would already be missed in this sample. One minute does not establish a thirty-day success rate; this is a defensible starting target to revisit with production history. Valid events are every response on /kb/search, including rejected input; good availability events have a non-5xx status. Client errors count as available because rejecting invalid input is correct service behaviour; a malformed-input flood can dilute this SLI, which is a known limitation of a route-level definition.

The latency objective is 99% of responses within 0.46 seconds, independently of success. Availability covers a fast 502; latency covers a slow 200. This threshold is an exposed bucket boundary, so the numerator counts actual observations rather than interpolating a percentile. It is above the measured client p99 of 0.3534 s, p99.9 of 0.4222 s and maximum reported 0.4384 s, leaving some room for the tail without promising that all requests finish within the fast mode's p95 of 0.0579 s. A threshold near 60 ms would punish the dependency's ordinary slow mode. The 0.46 s target remains below the 1 s ceiling used by the later Lab 6 gate. Later measurements can invalidate this target; the local run is evidence, not a guarantee.

Each objective allows a bad-event fraction of 1 - 0.99 = 0.01. A 30-day window has 30 * 24 * 60 = 43,200 minutes, so each equivalent time budget is 0.01 * 43,200 = 432 minutes. These are request-based budgets: 432 minutes is the equivalent at a uniform request rate, not a licence for a seven-hour outage during peak traffic. The two budgets apply separately and are not added together.

The final histogram has 26 finite boundaries. At the measured q, its bucket is (0.34, 0.36], width 0.02 / 0.3534 = 5.66%, comfortably below 20%. For q above 0.28 s and through 0.46 s, the buckets have 20 ms steps: their relative width is at most 0.02 / 0.28 = 7.14%. At exactly 0.28 s, the preceding (0.25, 0.28] bucket is 10.71% wide and also resolves q. It covers the required +/-10% band [0.31806, 0.38874] with substantial margin for another random sample or machine. Boundaries below 100 ms describe the common fast requests; 0.46 is the latency decision boundary; coarser buckets above 0.5 s distinguish severe degradation and timeouts without spending the entire series budget on rare extremes. Every request uses this same ladder. Route templates and one unmatched label keep random ticket IDs and queries out of the labels.

The P1 alert pages only when both the 1h and 5m availability error fractions exceed 14.4 * 0.01 = 14.4%, continuously for 5 minutes. Sustained at 14.4x, the whole 30-day budget lasts 30 / 14.4 = 2.083 days, and one hour spends 14.4 / 720 = 2% of it. This is severe current failure affecting roughly one search in seven, worth waking an operator to investigate the dependency or roll back a change. Waiting eight hours would spend about 16% of the budget and leave users without search results throughout that period.

The P2 alert goes to chat when both the 6h and 30m fractions exceed 6 * 0.01 = 6%, with the same 5m pending period. Six hours at 6x spends 6 * 6 / 720 = 5% of the budget. It catches sustained degradation that the fast page might miss, without paging for every short failure spike. The short windows end both alerts promptly after recovery. Quiet, onset, reset and mutation tests protect those behaviours. There is no automatic repair here: an operator first checks upstream health and service changes, and never hides failures with retries or a cache in this laboratory.
