---
lab4_comms:
  awareness: 2026-10-12T06:40:09Z
  detection: 2026-10-12T06:39:19Z
  classification: 2026-10-12T06:41:00Z
  nis2:
    early_warning_due: 2026-10-13T06:40:09Z
    notification_due: 2026-10-15T06:40:09Z
    notification_sent: 2026-10-12T08:00:00Z
    final_report_due: 2026-11-12T08:00:00Z
  ksc:
    early_warning_due: 2026-10-13T06:39:19Z
    notification_due: 2026-10-15T06:39:19Z
    notification_sent: 2026-10-12T08:00:00Z
    final_report_due: 2026-11-12T08:00:00Z
  dora:
    initial_due: 2026-10-12T10:41:00Z
    initial_sent: 2026-10-12T08:00:00Z
    intermediate_due: 2026-10-15T08:00:00Z
    intermediate_sent: 2026-10-14T08:00:00Z
    final_due: 2026-11-14T08:00:00Z
  log:
    - {at: 2026-10-12T06:40:09Z, to: internal incident coordinator, what: Simulated acknowledgement and significance awareness}
    - {at: 2026-10-12T07:00:00Z, to: designated CSIRT, what: Simulated NIS2 and KSC early warning}
    - {at: 2026-10-12T08:00:00Z, to: designated CSIRT, what: Simulated NIS2 and KSC incident notification}
    - {at: 2026-10-12T08:00:00Z, to: financial supervisor, what: Simulated DORA initial notification}
    - {at: 2026-10-14T08:00:00Z, to: financial supervisor, what: Simulated DORA intermediate report}
    - {at: 2026-11-12T08:00:00Z, to: designated CSIRT, what: Simulated NIS2 and KSC final report}
    - {at: 2026-11-14T08:00:00Z, to: financial supervisor, what: Simulated DORA final report}
---
<!-- ai-generated: 100% - Codex computed the course-defined regulatory clocks in UTC and wrote this hypothetical communications log. -->

# Communications exercise for the recorded checkout incident

## The three instants you defend

This is a hypothetical exercise using INCIDENT-SPEC.md I-30. Assume the shop is covered by all three regimes and this incident meets the stipulated significance and major-incident criteria. These entries are planned communications, not messages actually sent, and are not a legal assessment of this demo shop.

Detection is **06:39:19Z on 12 October 2026**, the first firing of the recorded `ShopCheckoutErrors` alert. Awareness is **06:40:09Z**, the recorded acknowledgement, chosen as the point where an on-call has accepted the page and, under the exercise assumption, recognises significance. Classification as a major ICT incident is assumed at **06:41:00Z**, after examining the failed-payment impact. Only detection and acknowledgement are recorded facts; awareness interpretation and classification are declared scenario assumptions.

NIS2 deadlines start at awareness; KSC starts at detection, fifty seconds earlier. DORA's initial deadline is classification plus four hours (**10:41:00Z**), earlier than awareness plus twenty-four hours. Its intermediate deadline follows the assumed initial notification, and its final deadline follows the assumed intermediate report. All calendar-month additions use the same UTC calendar day and time. Weekend relief is omitted as instructed by I-30.

## The log

| Planned UTC | Recipient | Content and clock |
|---|---|---|
| 2026-10-12 06:40:09 | Internal incident coordinator | P1 accepted; significance awareness starts the NIS2 clock |
| 2026-10-12 07:00:00 | Designated CSIRT | NIS2 and KSC early warning, within both twenty-four-hour deadlines |
| 2026-10-12 08:00:00 | Designated CSIRT | NIS2 and KSC notification, within both seventy-two-hour deadlines |
| 2026-10-12 08:00:00 | Financial supervisor | DORA initial notification before 10:41:00Z |
| 2026-10-14 08:00:00 | Financial supervisor | DORA intermediate report before 2026-10-15 08:00:00Z |
| 2026-11-12 08:00:00 | Designated CSIRT | NIS2 and KSC final reports, one calendar month after notification |
| 2026-11-14 08:00:00 | Financial supervisor | DORA final report, one calendar month after intermediate report |

No external communication is performed by this repository or the checker. All deadlines above are arithmetic under the laboratory specification. Times are UTC, so civil-clock changes do not alter elapsed-hour calculations.
