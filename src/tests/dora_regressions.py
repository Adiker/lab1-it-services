# ai-generated: 100% - Codex wrote independent HTTP regression cases for DORA boundary and reference rules.
"""Adversarial DORA cases used by the Compose tests profile."""

from collections.abc import Callable
from typing import Any


WINDOW = {"from": "2026-09-01T00:00:00Z", "to": "2026-09-02T00:00:00Z"}


def commit(event_id: str, sha: str, at: str, *, branch: str = "main", change: str | None = None,
           reverts: str | None = None) -> dict[str, Any]:
    return {
        "event_id": event_id, "type": "commit", "at": at, "sha": sha, "branch": branch,
        "change_id": change, "reverts": reverts,
    }


def deployment(event_id: str, deployment_id: str, at: str, shas: list[str],
               *, environment: str = "production", outcome: str = "success",
               unplanned: bool = False, caused_by: str | None = None) -> dict[str, Any]:
    return {
        "event_id": event_id, "type": "deployment", "at": at,
        "deployment_id": deployment_id, "environment": environment,
        "outcome": outcome, "commits": shas, "unplanned": unplanned,
        "caused_by": caused_by,
    }


def incident(event_id: str, incident_id: str, at: str, phase: str,
             deployments: list[str]) -> dict[str, Any]:
    return {
        "event_id": event_id, "type": "incident", "at": at,
        "incident_id": incident_id, "phase": phase, "deployments": deployments,
    }


def checks(request: Callable[..., tuple[int, Any]]) -> list[tuple[str, Callable[[], None]]]:
    """Return focused checks without depending on the runner's internal test registry."""

    def score(events: list[dict[str, Any]], window: dict[str, str] = WINDOW) -> dict[str, Any]:
        status, data = request("POST", "/dora/metrics", body={"window": window, "events": events})
        assert status == 200, (status, data)
        return data

    def half_open_boundaries() -> None:
        events = [
            commit("c-before", "before", "2026-08-31T23:00:00Z", change="A"),
            commit("c-to", "to", "2026-09-01T23:00:00Z", change="B"),
            deployment("d-from", "FROM", WINDOW["from"], ["before"]),
            deployment("d-to", "TO", WINDOW["to"], ["to"]),
        ]
        result = score(events)
        assert result["counts"]["deployments"] == 1
        assert result["counts"]["lead_time_pairs"] == 1
        assert result["ground_truth"]["changes_delivered"] == 1
        assert result["deployment_frequency_per_day"] == 1
        assert result["change_lead_time_seconds_p50"] == 3600

    def offset_window_equivalence() -> None:
        events = [
            commit("c-offset", "offset", "2026-08-31T23:30:00Z", change="A"),
            deployment("d-offset", "D", "2026-09-01T00:30:00Z", ["offset"]),
        ]
        utc = score(events)
        shifted = score(events, {"from": "2026-09-01T02:00:00+02:00", "to": "2026-09-02T02:00:00+02:00"})
        assert {k: v for k, v in shifted.items() if k != "window"} == {k: v for k, v in utc.items() if k != "window"}

    def first_duplicate_wins() -> None:
        base = [
            commit("c-first", "A", "2026-09-01T01:00:00Z", change="A"),
            deployment("d-first", "D", "2026-09-01T02:00:00Z", ["A"]),
        ]
        duplicate = dict(base[1], outcome="failure", commits=["not-a-sha"])
        assert score(base + [duplicate]) == score(base)

    def malformed_references_rejected() -> None:
        bad_logs = [
            [deployment("d-unknown-sha", "D", "2026-09-01T01:00:00Z", ["missing"])],
            [deployment("d-unknown-incident", "D", "2026-09-01T01:00:00Z", [], unplanned=True, caused_by="missing")],
            [incident("i-no-open", "I", "2026-09-01T02:00:00Z", "resolved", [])],
            [incident("i-unknown-deployment", "I", "2026-09-01T02:00:00Z", "opened", ["missing"])],
        ]
        for events in bad_logs:
            status, data = request("POST", "/dora/metrics", body={"window": WINDOW, "events": events})
            assert status in {400, 422} and isinstance(data.get("error"), dict), (status, data)

    def revert_cycle_rejected() -> None:
        events = [
            commit("c-a", "A", "2026-09-01T01:00:00Z", reverts="B"),
            commit("c-b", "B", "2026-09-01T02:00:00Z", reverts="A"),
        ]
        status, data = request("POST", "/dora/metrics", body={"window": WINDOW, "events": events})
        assert status in {400, 422} and isinstance(data.get("error"), dict), (status, data)

    def touching_incident_intervals_do_not_overlap() -> None:
        events = [
            incident("i-a-open", "A", "2026-09-01T08:00:00Z", "opened", []),
            incident("i-a-close", "A", "2026-09-01T09:00:00Z", "resolved", []),
            incident("i-b-open", "B", "2026-09-01T09:00:00Z", "opened", []),
            incident("i-b-close", "B", "2026-09-01T10:00:00Z", "resolved", []),
        ]
        assert score(events)["anomalies"]["overlapping_incident_pairs"] == 0
        events.extend([
            incident("i-c-open", "C", "2026-09-01T08:30:00Z", "opened", []),
            incident("i-c-close", "C", "2026-09-01T09:30:00Z", "resolved", []),
        ])
        assert score(events)["anomalies"]["overlapping_incident_pairs"] == 2

    def later_redeployment_does_not_add_lead_pair() -> None:
        events = [
            commit("c-one", "A", "2026-09-01T01:00:00Z", change="A"),
            deployment("d-first", "FIRST", "2026-09-01T02:00:00Z", ["A"]),
            deployment("d-second", "SECOND", "2026-09-01T05:00:00Z", ["A"]),
        ]
        result = score(list(reversed(events)))
        assert result["counts"]["deployments"] == 2
        assert result["counts"]["lead_time_pairs"] == 1
        assert result["change_lead_time_seconds_p50"] == 3600

    return [
        ("DORA half-open deployment boundaries", half_open_boundaries),
        ("DORA equivalent offset windows", offset_window_equivalence),
        ("DORA first duplicate event wins", first_duplicate_wins),
        ("DORA malformed cross-references rejected", malformed_references_rejected),
        ("DORA revert cycles rejected", revert_cycle_rejected),
        ("DORA touching incident intervals", touching_incident_intervals_do_not_overlap),
        ("DORA redeployment contributes one lead pair", later_redeployment_does_not_add_lead_pair),
    ]
