# ai-generated: 100% - Codex implemented deterministic HTTP tests for the Lab 1 Stretch S3 contract.
"""Dependency-free HTTP test runner used by the Compose tests profile."""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any


BASE = os.environ.get("SVCDESK_URL", "http://svcdesk:8080").rstrip("/")
T1 = "2026-10-14T10:00:00Z"
T1_5 = "2026-10-14T10:05:00Z"
T1_10 = "2026-10-14T10:10:00Z"
T1_1H = "2026-10-14T11:00:00Z"
T1_2H = "2026-10-14T12:00:00Z"


def request(method: str, path: str, clock: str = T1, body: dict[str, Any] | None = None) -> tuple[int, Any]:
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/json", "X-Test-Clock": clock}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, json.loads(raw) if raw else None


def payload(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "title": "own-test ticket",
        "description": "created by the repository test profile",
        "reporter": {"name": "own tests", "vip": False},
        "impact": 1,
        "urgency": 1,
    }
    body.update(overrides)
    return body


def create(**overrides: Any) -> dict[str, Any]:
    status, ticket = request("POST", "/tickets", body=payload(**overrides))
    assert status == 201 and isinstance(ticket, dict), (status, ticket)
    return ticket


def wait_for_health() -> None:
    for _ in range(30):
        try:
            status, data = request("GET", "/health")
            if status == 200 and data.get("status") == "ok":
                return
        except (OSError, ValueError):
            pass
        time.sleep(1)
    raise RuntimeError("svcdesk did not become healthy")


def main() -> int:
    wait_for_health()
    checks: list[tuple[str, Callable[[], None]]] = []

    def check(name: str):
        def register(function: Callable[[], None]) -> Callable[[], None]:
            checks.append((name, function))
            return function
        return register

    @check("health")
    def _():
        status, data = request("GET", "/health")
        assert status == 200 and data == {"status": "ok", "service": "svcdesk"}

    @check("unknown route")
    def _():
        status, data = request("GET", "/missing-own-test")
        assert status == 404 and isinstance(data, dict)

    @check("create and P1 due instants")
    def _():
        ticket = create()
        assert ticket["state"] == "new" and ticket["priority"] == "P1"
        assert ticket["sla"] == {
            "ack_due_at": "2026-10-14T10:15:00Z",
            "resolve_due_at": "2026-10-14T14:00:00Z",
        }

    @check("VIP promotion")
    def _():
        ticket = create(impact=3, urgency=3, reporter={"name": "VIP", "vip": True})
        assert ticket["priority"] == "P2"

    @check("priority input ignored")
    def _():
        ticket = create(impact=3, urgency=3, reporter={"name": "VIP", "vip": True}, priority="P1")
        assert ticket["priority"] == "P2"

    @check("get by id")
    def _():
        ticket = create(title="own-test get")
        status, found = request("GET", f"/tickets/{ticket['id']}")
        assert status == 200 and found["title"] == "own-test get"

    @check("list state filter")
    def _():
        ticket = create()
        status, items = request("GET", "/tickets?state=new")
        assert status == 200 and ticket["id"] in {item["id"] for item in items}

    @check("acknowledge")
    def _():
        ticket = create()
        status, updated = request("POST", f"/tickets/{ticket['id']}/ack", T1_5)
        assert status == 200 and updated["state"] == "acknowledged"
        assert updated["acknowledged_at"] == T1_5

    @check("acknowledge twice rejected")
    def _():
        ticket = create()
        request("POST", f"/tickets/{ticket['id']}/ack", T1_5)
        status, data = request("POST", f"/tickets/{ticket['id']}/ack", T1_10)
        assert status == 409 and "error" in data

    @check("normal state path")
    def _():
        ticket = create()
        request("POST", f"/tickets/{ticket['id']}/ack", T1_5)
        status, started = request("POST", f"/tickets/{ticket['id']}/start", T1_10)
        assert status == 200 and started["state"] == "in_progress"
        status, resolved = request("POST", f"/tickets/{ticket['id']}/resolve", T1_1H)
        assert status == 200 and resolved["state"] == "resolved"
        status, closed = request("POST", f"/tickets/{ticket['id']}/close", T1_2H)
        assert status == 200 and closed["state"] == "closed"

    @check("resolved reopen within window")
    def _():
        ticket = create()
        request("POST", f"/tickets/{ticket['id']}/ack", T1_5)
        request("POST", f"/tickets/{ticket['id']}/start", T1_10)
        request("POST", f"/tickets/{ticket['id']}/resolve", T1_1H)
        status, reopened = request("POST", f"/tickets/{ticket['id']}/reopen", "2026-10-20T11:00:00Z")
        assert status == 200 and reopened["state"] == "in_progress"
        assert reopened["resolved_at"] is None

    @check("closed is immutable")
    def _():
        ticket = create()
        request("POST", f"/tickets/{ticket['id']}/ack", T1_5)
        request("POST", f"/tickets/{ticket['id']}/start", T1_10)
        request("POST", f"/tickets/{ticket['id']}/resolve", T1_1H)
        request("POST", f"/tickets/{ticket['id']}/close", T1_2H)
        status, _data = request("POST", f"/tickets/{ticket['id']}/reopen", "2026-10-15T12:00:00Z")
        assert status == 409

    @check("SLA breach and pause")
    def _():
        ticket = create(impact=1, urgency=3)
        status, sla = request("GET", f"/tickets/{ticket['id']}/sla", "2026-10-17T10:00:00Z")
        assert status == 200 and sla["paused"] is True

    @check("missing title validation object")
    def _():
        body = payload()
        del body["title"]
        status, data = request("POST", "/tickets", body=body)
        assert status in {400, 422} and isinstance(data.get("error"), dict)

    @check("malformed clock")
    def _():
        status, _data = request("POST", "/tickets", "yesterday", payload())
        assert status in {400, 422}

    window = {"from": "2026-09-01T00:00:00Z", "to": "2026-09-22T00:00:00Z"}
    practice_events = [json.loads(line) for line in Path("/app/fixtures/events-practice.jsonl").read_text().splitlines() if line]
    practice_expected = json.loads(Path("/app/fixtures/metrics-practice.json").read_text())

    @check("DORA practice answer exactly matches published values")
    def _():
        status, data = request("POST", "/dora/metrics", body={"window": window, "events": practice_events})
        assert status == 200 and data == practice_expected, (status, data)

    @check("DORA ordering and exact duplicates")
    def _():
        status, data = request("POST", "/dora/metrics", body={"window": window, "events": list(reversed(practice_events * 2))})
        assert status == 200 and data == practice_expected, (status, data)

    @check("DORA empty log has null ratios and medians")
    def _():
        status, data = request("POST", "/dora/metrics", body={"window": window, "events": []})
        assert status == 200 and data["deployment_frequency_per_day"] == 0
        assert all(data[key] is None for key in ("change_lead_time_seconds_p50", "failed_deployment_recovery_time_seconds_p50", "change_fail_rate", "deployment_rework_rate"))
        assert all(value == 0 for value in data["counts"].values())

    @check("DORA rejects malformed references")
    def _():
        malformed = [{"event_id": "bad-commit", "type": "commit", "at": "2026-09-01T01:00:00Z", "sha": "bad", "branch": "main", "change_id": None, "reverts": "missing"}]
        status, data = request("POST", "/dora/metrics", body={"window": window, "events": malformed})
        assert status in {400, 422} and isinstance(data.get("error"), dict)

    @check("DORA rejects reversed window")
    def _():
        status, data = request("POST", "/dora/metrics", body={"window": {"from": window["to"], "to": window["from"]}, "events": []})
        assert status in {400, 422} and isinstance(data.get("error"), dict)

    @check("DORA synthetic revert, clock skew, recovery and ground truth")
    def _():
        synthetic = [
            {"event_id": "c1", "type": "commit", "at": "2026-09-01T01:00:00Z", "sha": "a", "branch": "main", "change_id": "CH-A", "reverts": None},
            {"event_id": "c2", "type": "commit", "at": "2026-09-01T04:00:00Z", "sha": "b", "branch": "hotfix", "change_id": None, "reverts": "a"},
            {"event_id": "c3", "type": "commit", "at": "2026-09-01T06:00:00Z", "sha": "c", "branch": "main", "change_id": None, "reverts": "b"},
            {"event_id": "d1", "type": "deployment", "at": "2026-09-01T03:00:00Z", "deployment_id": "D1", "environment": "production", "outcome": "success", "commits": ["a", "b"], "unplanned": False, "caused_by": None},
            {"event_id": "d2", "type": "deployment", "at": "2026-09-01T05:00:00Z", "deployment_id": "D2", "environment": "production", "outcome": "success", "commits": ["b", "c"], "unplanned": False, "caused_by": None},
            {"event_id": "d3", "type": "deployment", "at": "2026-09-01T07:00:00Z", "deployment_id": "D3", "environment": "production", "outcome": "failure", "commits": [], "unplanned": True, "caused_by": "I1"},
            {"event_id": "i1-open", "type": "incident", "at": "2026-09-01T07:05:00Z", "incident_id": "I1", "phase": "opened", "deployments": ["D3"]},
            {"event_id": "i1-resolved", "type": "incident", "at": "2026-09-02T01:00:00Z", "incident_id": "I1", "phase": "resolved", "deployments": ["D3"]},
        ]
        status, data = request("POST", "/dora/metrics", body={"window": {"from": "2026-09-01T00:00:00Z", "to": "2026-09-02T00:00:00Z"}, "events": synthetic})
        assert status == 200, (status, data)
        assert data["deployment_frequency_per_day"] == 3
        assert data["change_lead_time_seconds_p50"] == 0
        assert data["failed_deployment_recovery_time_seconds_p50"] == 64800
        assert data["change_fail_rate"] == data["deployment_rework_rate"] == 0.333333
        assert data["counts"]["lead_time_pairs"] == 3 and data["counts"]["changes"] == 1
        assert data["anomalies"]["negative_lead_time_pairs"] == 2
        assert data["anomalies"]["revert_chains_collapsed"] == 2
        assert data["anomalies"]["commits_never_on_main"] == 1
        assert data["ground_truth"] == {"changes_delivered": 1, "true_change_lead_time_seconds_p50": 7200}

    @check("DORA selects earliest covering incident even when unresolved")
    def _():
        failed = {"event_id": "failure", "type": "deployment", "at": "2026-09-01T09:00:00Z", "deployment_id": "D", "environment": "production", "outcome": "failure", "commits": [], "unplanned": False, "caused_by": None}
        events = [
            failed,
            {"event_id": "open-early", "type": "incident", "at": "2026-09-01T09:05:00Z", "incident_id": "EARLY", "phase": "opened", "deployments": ["D"]},
            {"event_id": "open-late", "type": "incident", "at": "2026-09-01T09:10:00Z", "incident_id": "LATE", "phase": "opened", "deployments": ["D"]},
            {"event_id": "resolve-late", "type": "incident", "at": "2026-09-01T10:00:00Z", "incident_id": "LATE", "phase": "resolved", "deployments": ["D"]},
        ]
        status, data = request("POST", "/dora/metrics", body={"window": window, "events": events})
        assert status == 200 and data["failed_deployment_recovery_time_seconds_p50"] is None
        assert data["counts"]["open_failures"] == 1 and data["counts"]["recovered_failures"] == 0
        assert data["anomalies"]["overlapping_incident_pairs"] == 1

    @check("DORA offset window denotes the same UTC instants")
    def _():
        shifted = {"from": "2026-09-01T02:00:00+02:00", "to": "2026-09-22T02:00:00+02:00"}
        status, data = request("POST", "/dora/metrics", body={"window": shifted, "events": practice_events})
        assert status == 200 and data["window"] == shifted
        assert {key: value for key, value in data.items() if key != "window"} == {key: value for key, value in practice_expected.items() if key != "window"}

    @check("ticket event stream follows lifecycle and sort order")
    def _():
        ticket = create(title="stream test")
        request("POST", f"/tickets/{ticket['id']}/ack", T1_5)
        request("POST", f"/tickets/{ticket['id']}/start", T1_10)
        request("POST", f"/tickets/{ticket['id']}/resolve", T1_1H)
        status, events = request("GET", "/dora/ticket-events")
        assert status == 200 and isinstance(events, list)
        own = [event for event in events if event["ticket_id"] == ticket["id"]]
        assert [(event["phase"], event["state"]) for event in own] == [("created", "new"), ("acknowledged", "acknowledged"), ("resolved", "resolved")]
        assert all(event["priority"] == ticket["priority"] for event in own)
        assert [(event["at"], event["ticket_id"]) for event in events] == sorted((event["at"], event["ticket_id"]) for event in events)

    passed = 0
    failures: list[str] = []
    for name, function in checks:
        try:
            function()
            passed += 1
        except Exception as exc:  # noqa: BLE001 - report every own-test failure before exiting
            failures.append(f"{name}: {type(exc).__name__}: {exc}")

    for failure in failures:
        print(f"FAIL {failure}")
    print(f"ITSMLAB-TESTS: passed={passed} failed={len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
