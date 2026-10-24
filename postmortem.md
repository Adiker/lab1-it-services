---
lab4_postmortem:
  ticket: "50ceffde-fa49-40b3-b4ca-957734d74bf7"
  detecting_alert: ShopCheckoutErrors
  onset: 2026-10-12T06:36:23Z
  detection: 2026-10-12T06:39:19Z
  acknowledgement: 2026-10-12T06:40:09Z
  recovery: 2026-10-12T06:44:19Z
  mttd_seconds: 176
  mtta_seconds: 50
  mttr_seconds: 476
  identified_flags: [paymentFailure, loadGeneratorFloodHomepage]
---
<!-- ai-generated: 100% - Codex analysed the assigned unchanged recording, checked PromQL and drafted this evidence-based report. -->

# Postmortem: failed checkout payments and a homepage traffic surge

## Date

The recorded incident occurred on 12 October 2026. This retrospective was prepared on 24 October 2026; all incident clocks below are UTC.

## Authors

Adiker is the laboratory repository owner. Codex assisted with retrospective analysis of the lecturer's recording, query verification and this report; the recorded on-call actions belong to the lecturer, not to this analysis session.

## Status

The recorded detecting alert has resolved. The problem record and the local action items remain open. No issue, submission receipt or regulator notification has been created. The original ticket remains acknowledged in the supplied export; it has not been edited to imply closure.

## Summary

Checkout began failing after the injector onset at 06:36:23Z. `ShopCheckoutErrors` detected the symptom 176 seconds later, and its first firing run ended at 06:44:19Z: an incident MTTR of 476 seconds. The evidence supports payment failures and a separate homepage traffic flood. This is the assigned recorded path, `lab4-rec-4`, rather than a newly operated live incident.

## Impact

At 06:41:00Z, five-minute checkout SERVER failures were **26.2675%**, or **0.0296879 failed calls/s**; the payment SERVER failure ratio and error rate matched. Frontend SERVER traffic was **58.1097465 calls/s**, compared with **3.8083333 calls/s** at 06:31:23Z, a **15.26-fold** increase. Frontend-proxy traffic rose from **1.975/s** to **30.0416667/s**. These are recorded spans, not a count of unique customers or lost revenue.

The checkout error counter reached **8** by 06:46:00Z. A ten-minute `increase` gives **8.8170167**, an extrapolated rate estimate, so it must not be described as nine actual orders. The error series is absent on the healthy baseline and has no observed counter reset in this window. Eight is the recorded cumulative failed SERVER span count, subject to sampling and the snapshot boundary. The 476-second MTTR is the alert's defined recovery clock, not a claim that every user was affected continuously or that every resource fault ended then.

Queries and instants for these numbers are retained in `evidence/lab4-analysis.json`. The ratios use `sum(rate(traces_span_metrics_calls_total{service_name="checkout",span_kind="SPAN_KIND_SERVER",status_code="STATUS_CODE_ERROR"}[5m])) / sum(rate(traces_span_metrics_calls_total{service_name="checkout",span_kind="SPAN_KIND_SERVER"}[5m]))`, with `payment` substituted for payment. Traffic uses `sum(rate(traces_span_metrics_calls_total{service_name="frontend",span_kind="SPAN_KIND_SERVER"}[5m]))`. The cumulative failure query is `sum(traces_span_metrics_calls_total{service_name="checkout",span_kind="SPAN_KIND_SERVER",status_code="STATUS_CODE_ERROR"})` at 06:46:00Z.

## Root Causes

`paymentFailure` is the strongest symptom-based identification of the errors-class flag: payment's internal `charge`, its SERVER `oteldemo.PaymentService/Charge`, and checkout's CLIENT call to that endpoint show matching errors. This fits failure propagation from payment to checkout. It does not establish a production code defect independently of the exercise's flag pool.

`loadGeneratorFloodHomepage` is the strongest identification of the latency/load flag. Frontend and frontend-proxy traffic rose together by about fifteenfold, while checkout and catalog traffic did not show the same multiplier. This fits homepage flooding rather than a catalog-wide stall or a shipping delay. Checkout p99 was about **49.54 ms**, and shipping p99 about **3.812 ms**, at 06:41:00Z; those observations do not support a multi-second shipping slowdown at that instant.

The resource-class flag is unresolved. Email container memory stayed around 58–61 MB and uptime increased without a reset. Recommendation memory also lacked a clear onset-aligned rise during this short recording. The report identifies two supported flags, as I-22 permits, instead of claiming that an OOM kill or a cache failure was observed. Only Tier B can compare these identifications with the sealed fault.

## Trigger

The first `seeded_fault_active` sample at **2026-10-12T06:36:23Z** defines onset. The lecturer armed one run, `c1daa7d0f4acf990`, after a healthy baseline. Injector telemetry is used only for the prescribed incident clocks, never as an alert expression or a ledger prediction. Feature flag state and traces are unavailable on the recorded path.

## Resolution

The lecturer's recording contains the rollback and the alert recovery. The supplied ticket and metrics do not establish the exact per-flag off instants or rollback order, so this retrospective does not invent them. Payment and checkout errors stop accumulating, and the detecting alert's firing run ends at **06:44:19Z** after its rolling window clears. Frontend's rolling traffic rate remains elevated at 06:46:00Z, reinforcing that the defined recovery belongs to the detecting alert.

For a future live run, the workaround is to switch off the failing `paymentFailure` flag first to restore orders, then `loadGeneratorFloodHomepage` to remove unnecessary load, checking errors and traffic after each action. Inspect and mitigate the resource flag separately once identified. This is a proposed procedure, not an action claimed in the recording or performed in this retrospective.

## Detection

The recorded P1 `ShopCheckoutErrors` first fired at **06:39:19Z**, giving **MTTD 176 s**. The pager's firing-notification counter increased after onset. Ticket creation was at **06:39:44Z**, and acknowledgement at **06:40:09Z**, giving **MTTA 50 s** from detection. Successful ticket creation and acknowledgement requests are present in svcdesk telemetry, as checked by `itsmlab incident 4` and `verify 4`.

The repository's new `CheckoutErrorRate` and `CheckoutLatency` are prospective rules. They did not produce the recorded alert or ticket. Both watch SERVER spans in five-minute windows; latency is interpreted in milliseconds. They would cover checkout errors as well as the pool's latency-only draws. Without paging, a user or a dashboard observer could have noticed failed orders, with no guaranteed response time.

## Action Items

The Bug identifiers below are local tracking references for later laboratories; no GitHub issues were opened.

| Action Item | Type | Owner | Bug |
|---|---|---|---|
| Add a payment-error rollback checklist with a separate verification after each flag change | mitigate | Adiker / on-call | LAB4-A01 |
| Gate failing payment variants and homepage flood changes on checkout error and latency canaries | prevent | Adiker / service owner | LAB4-A02 |
| Reject AI investigation queries outside the incident window and validate discovered label values | process | Adiker / observability | LAB4-A03 |
| Retain per-flag change events and resource histories long enough to distinguish rollback from alert recovery | process | Adiker / observability | LAB4-A04 |

## Lessons Learned

### What went well

The pager, P1 ticket and acknowledgement leave independent evidence in one immutable snapshot. SERVER filtering separates user-facing symptoms from noisy CLIENT spans. Re-executing ledger predictions against both fault and baseline makes the positive conclusions testable.

### What went wrong

The recorded Qwen investigator queried the unrelated date 2024-04-14 after initially using the correct window, then interpreted empty results as possible absence of errors. It also abbreviated checkout's payment span incorrectly and repeated the same payment finding instead of investigating the traffic surge. A correct final symptom claim does not make those investigation steps reliable.

### Where we got lucky

Payment errors were visible within a short fault and the response was prompt. The traffic multiplier was large enough to distinguish flooding despite one-minute span samples. The exercise accepts two supported flag identifications; a real incident would still need longer resource evidence before declaring the underlying problem closed.

## Timeline

All times below are on 2026-10-12 in UTC. AI analysis was performed retrospectively on 2026-10-24; it did not cause the lecturer's rollback. No AI hypothesis was acted on during the recorded response.

| UTC | Recorded event or retrospective evidence |
|---|---|
| 06:31:23 | Healthy comparison instant, five minutes before onset. Second-ledger H1–H3 predictions all return empty. |
| 06:36:22 | `max_over_time(ALERTS{severity="P1",alertstate="firing"}[10m])` is empty immediately before onset. |
| **06:36:23** | Injector onset for the single armed run. |
| **06:39:19** | Recorded `ShopCheckoutErrors` begins firing; MTTD 176 s. |
| 06:39:44 | Recorded on-call creates P1 ticket `50ceffde-fa49-40b3-b4ca-957734d74bf7`. |
| **06:40:09** | Recorded on-call acknowledges the ticket; MTTA 50 s. |
| 06:41:00 | Retrospective primary ledger H1/H2: `sum(rate(traces_span_metrics_calls_total{service_name="payment",span_name="charge",span_kind="SPAN_KIND_INTERNAL",status_code="STATUS_CODE_ERROR"}[5m])) > 0.01` returns 0.0296879/s. |
| 06:41:00 | Primary H3 combines that payment comparison with the checkout payment CLIENT comparison using `and on()`; primary H4 uses `sum(rate(traces_span_metrics_calls_total{service_name="checkout",span_name="oteldemo.PaymentService/Charge",span_kind="SPAN_KIND_CLIENT",status_code="STATUS_CODE_ERROR"}[5m])) > 0.01`. Both hold. |
| 06:41:00 | Second ledger H1/H2 use the payment/checkout SERVER error ratios above, each `> 0.05`, returning 0.2626755. Second ledger H3 uses `sum(rate(traces_span_metrics_calls_total{service_name="frontend",span_kind="SPAN_KIND_SERVER"}[5m])) > 20`, returning 58.1097465/s. These supported retrospective flag identification, not a live intervention. |
| **06:44:19** | First firing run of the detecting alert ends; defined MTTR 476 s. |
| 06:46:00 | Checkout cumulative error counter is 8. Snapshot still contains post-recovery data. Exact flag rollback times and sequence remain unavailable. |

## Supporting information

The immutable source is `incident/tsdb-snapshot.tar.gz` plus `incident/ticket.json`, copied byte-for-byte from login `adiker`'s assigned `lab4-rec-4`. Hashes and `itsmlab incident 4` output are in `evidence/lab4-analysis.json` and `evidence/lab4-incident.txt`. The recording's ticket and alert names are preserved. There are no live Jaeger traces or flag-state documents to cite.

`ai-rca/transcript.md` is the lecturer-provided Qwen transcript, unchanged. `ai-rca-eval.json` scores its four final claims, translating symptoms into evaluable predictions rather than trusting the model's literal query strings. The fourth claim's abbreviated label is explicitly corrected in the ledger's evidence. Its empty queries in 2024 do not disprove errors in October 2026.

`ai-rca/second/transcript.md` and its JSONL twin retain this Codex investigation, actual calls to the course `prom_mcp.py` server, conclusions and an explicit numeric correction. `ai-rca-eval-2.json` scores its three separate claims; `ai-rca/COMPARISON.md` compares the investigators. Own rule replay evidence distinguishes prospective alert behavior from recorded `ALERTS`. No private key, API key or kubeconfig belongs in the deliverable.

## Problem record

Incident record: P1 ticket 50ceffde-fa49-40b3-b4ca-957734d74bf7, acknowledged in the supplied recording; the detecting alert resolved at 06:44:19Z.
Root cause: Evidence supports injected payment transaction failures and a homepage traffic flood; the resource-class mechanism remains unconfirmed from this short recording.
Known error: Failure-capable payment variants can propagate errors to checkout, and homepage flooding can multiply frontend load without a matching increase in completed orders.
Workaround: In a live recurrence, disable the failing payment flag and homepage flood separately, verify checkout recovery, and investigate resource effects before closing the problem.
