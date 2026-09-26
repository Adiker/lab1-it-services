# ai-generated: 100% - Codex implemented the Lab 2 event validation and DORA rules from METRIC-SPEC.md.
"""Pure delivery-metric calculation over a validated event log."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$")
SIX_PLACES = Decimal("0.000001")


def instant(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not RFC3339.fullmatch(value):
        raise ValueError(f"{field} must be an RFC 3339 instant with an offset")
    try:
        result = datetime.fromisoformat(value.replace("t", "T").replace("z", "Z").replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid RFC 3339 instant") from exc
    if result.utcoffset() is None:
        raise ValueError(f"{field} must include an offset")
    return result.astimezone(timezone.utc)


def text(value: Any, field: str, maximum: int | None = None) -> str:
    if not isinstance(value, str) or not value or (maximum is not None and len(value) > maximum):
        raise ValueError(f"{field} must be a nonempty string" + (f" of at most {maximum} characters" if maximum else ""))
    return value


def optional_text(value: Any, field: str) -> str | None:
    return None if value is None else text(value, field)


def names(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    return [text(name, field) for name in value]


def seconds(later: datetime, earlier: datetime) -> Decimal:
    span = later - earlier
    return Decimal(span.days * 86400 + span.seconds) + Decimal(span.microseconds) / 1000000


def rounded_seconds(value: Decimal) -> int:
    return int(max(value, Decimal(0)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def median(values: list[Decimal]) -> int | None:
    if not values:
        return None
    values.sort()
    middle = len(values) // 2
    selected = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2
    return rounded_seconds(selected)


def ratio(numerator: int, denominator: int | Decimal) -> float | None:
    if not denominator:
        return None
    return float((Decimal(numerator) / Decimal(denominator)).quantize(SIX_PLACES, rounding=ROUND_HALF_UP))


def validate(events: Any) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if not isinstance(events, list):
        raise ValueError("events must be an array")
    deduplicated: dict[str, dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("each event must be an object")
        event_id = text(event.get("event_id"), "event_id", 64)
        if event_id in deduplicated:
            continue  # R-05: only the first occurrence has any effect.
        kind = event.get("type")
        if kind not in {"commit", "deployment", "incident"}:
            raise ValueError("event.type must be commit, deployment or incident")
        item = dict(event)
        item["_instant"] = instant(event.get("at"), "event.at")
        if kind == "commit":
            text(event.get("sha"), "commit.sha")
            text(event.get("branch"), "commit.branch")
            revert = optional_text(event.get("reverts"), "commit.reverts")
            change = optional_text(event.get("change_id"), "commit.change_id")
            if (revert is None) == (change is None):
                raise ValueError("commit.change_id must be present exactly when reverts is null")
        elif kind == "deployment":
            text(event.get("deployment_id"), "deployment.deployment_id")
            text(event.get("environment"), "deployment.environment")
            if event.get("outcome") not in {"success", "failure"}:
                raise ValueError("deployment.outcome must be success or failure")
            names(event.get("commits"), "deployment.commits")
            if not isinstance(event.get("unplanned"), bool):
                raise ValueError("deployment.unplanned must be boolean")
            optional_text(event.get("caused_by"), "deployment.caused_by")
        else:
            text(event.get("incident_id"), "incident.incident_id")
            if event.get("phase") not in {"opened", "resolved"}:
                raise ValueError("incident.phase must be opened or resolved")
            names(event.get("deployments"), "incident.deployments")
        deduplicated[event_id] = item

    commits: dict[str, dict[str, Any]] = {}
    deployments: dict[str, dict[str, Any]] = {}
    incidents: dict[str, dict[str, Any]] = {}
    for item in deduplicated.values():
        if item["type"] == "commit":
            if item["sha"] in commits:
                raise ValueError("commit.sha must be unique")
            commits[item["sha"]] = item
        elif item["type"] == "deployment":
            if item["deployment_id"] in deployments:
                raise ValueError("deployment.deployment_id must be unique")
            deployments[item["deployment_id"]] = item
        else:
            incident = incidents.setdefault(item["incident_id"], {})
            if item["phase"] in incident:
                raise ValueError("incident has a duplicate phase")
            incident[item["phase"]] = item

    for commit in commits.values():
        if commit["reverts"] is not None and commit["reverts"] not in commits:
            raise ValueError("commit.reverts names an unknown sha")
    for deployment in deployments.values():
        if any(sha not in commits for sha in deployment["commits"]):
            raise ValueError("deployment.commits names an unknown sha")
        if deployment["caused_by"] is not None and deployment["caused_by"] not in incidents:
            raise ValueError("deployment.caused_by names an unknown incident")
    for incident in incidents.values():
        if "opened" not in incident:
            raise ValueError("resolved incident has no opened event")
        for phase in incident.values():
            if any(dep not in deployments for dep in phase["deployments"]):
                raise ValueError("incident.deployments names an unknown deployment")
            if any(
                deployments[dep]["environment"] != "production" or deployments[dep]["outcome"] != "failure"
                for dep in phase["deployments"]
            ):
                raise ValueError("incident.deployments must name failed production deployments")
    return commits, deployments, incidents


def calculate(body: Any) -> dict[str, Any]:
    if not isinstance(body, dict):
        raise ValueError("body must be an object")
    window = body.get("window")
    if not isinstance(window, dict):
        raise ValueError("window must be an object")
    start = instant(window.get("from"), "window.from")
    end = instant(window.get("to"), "window.to")
    if end <= start:
        raise ValueError("window.to must be after window.from")
    commits, deployments, incidents = validate(body.get("events"))

    change_cache: dict[str, str] = {}
    resolving: set[str] = set()

    def change_of(sha: str) -> str:
        if sha in change_cache:
            return change_cache[sha]
        if sha in resolving:
            raise ValueError("commit.reverts contains a cycle")
        resolving.add(sha)
        commit = commits[sha]
        result = commit["change_id"] if commit["reverts"] is None else change_of(commit["reverts"])
        resolving.remove(sha)
        change_cache[sha] = result
        return result

    first_commit: dict[str, datetime] = {}
    for sha, commit in commits.items():
        change = change_of(sha)
        first_commit[change] = min(first_commit.get(change, commit["_instant"]), commit["_instant"])

    scoped = [d for d in deployments.values() if d["environment"] == "production" and start <= d["_instant"] < end]
    successful = [d for d in scoped if d["outcome"] == "success"]
    failed = [d for d in scoped if d["outcome"] == "failure"]
    rework = sum(d["unplanned"] and d["caused_by"] is not None for d in scoped)
    carried = {sha for d in scoped for sha in d["commits"]}

    # R-08: each commit contributes at its first successful deployment, irrespective of input order.
    first_ship: dict[str, datetime] = {}
    first_change_ship: dict[str, datetime] = {}
    for deployment in successful:
        when = deployment["_instant"]
        for sha in deployment["commits"]:
            first_ship[sha] = min(first_ship.get(sha, when), when)
            change = change_of(sha)
            first_change_ship[change] = min(first_change_ship.get(change, when), when)
    lead_values = [seconds(ship, commits[sha]["_instant"]) for sha, ship in first_ship.items()]
    negative_leads = sum(value < 0 for value in lead_values)
    true_leads = [seconds(ship, first_commit[change]) for change, ship in first_change_ship.items()]

    # R-12: use the earliest covering opening; an unresolved covering incident stays open.
    recovered_values: list[Decimal] = []
    for deployment in failed:
        covering = [
            (incident["opened"]["_instant"], incident_id, incident)
            for incident_id, incident in incidents.items()
            if any(deployment["deployment_id"] in phase["deployments"] for phase in incident.values())
        ]
        if covering:
            chosen = min(covering, key=lambda entry: (entry[0], entry[1]))[2]
            if "resolved" in chosen:
                recovered_values.append(seconds(chosen["resolved"]["_instant"], deployment["_instant"]))

    # R-13: incidents are never window-filtered; the interval of an open one ends at window.to.
    intervals = [
        (incident["opened"]["_instant"], incident.get("resolved", {}).get("_instant", end))
        for incident in incidents.values()
    ]
    overlaps = sum(
        left_start < right_end and right_start < left_end
        for index, (left_start, left_end) in enumerate(intervals)
        for right_start, right_end in intervals[index + 1:]
    )
    days = seconds(end, start) / Decimal(86400)
    return {
        "spec_version": "1.0.0",
        "window": {"from": window["from"], "to": window["to"]},
        "deployment_frequency_per_day": ratio(len(scoped), days),
        "change_lead_time_seconds_p50": median([max(value, Decimal(0)) for value in lead_values]),
        "failed_deployment_recovery_time_seconds_p50": median([max(value, Decimal(0)) for value in recovered_values]),
        "change_fail_rate": ratio(len(failed), len(scoped)),
        "deployment_rework_rate": ratio(rework, len(scoped)),
        "counts": {
            "deployments": len(scoped), "successful_deployments": len(successful),
            "failed_deployments": len(failed), "recovered_failures": len(recovered_values),
            "open_failures": len(failed) - len(recovered_values),
            "rework_deployments": rework, "lead_time_pairs": len(first_ship),
            "changes": len(first_commit),
        },
        "anomalies": {
            "negative_lead_time_pairs": negative_leads,
            "deployments_without_commits": sum(not d["commits"] for d in scoped),
            "commits_never_on_main": sum(commits[sha]["branch"] != "main" for sha in carried),
            "revert_chains_collapsed": sum(c["reverts"] is not None for c in commits.values()),
            "overlapping_incident_pairs": overlaps,
        },
        "ground_truth": {
            "changes_delivered": len(first_change_ship),
            "true_change_lead_time_seconds_p50": median([max(value, Decimal(0)) for value in true_leads]),
        },
    }
