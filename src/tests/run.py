# ai-generated: 100% - Codex implemented deterministic HTTP tests for the Lab 1 Stretch S3 contract.
"""Dependency-free HTTP test runner used by the Compose tests profile."""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
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
