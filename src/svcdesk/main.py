# ai-generated: 100% - Codex implemented the FastAPI endpoints, lifecycle decisions, validation, and SLA status.
"""HTTP application for the Lab 1 svcdesk contract."""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated, Any
from uuid import uuid4

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import dora, store
from .clock import due_instants, is_business_time, parse_instant, real_now, utc_text
from .models import TicketCreate


MATRIX = {
    (1, 1): "P1", (1, 2): "P2", (1, 3): "P3",
    (2, 1): "P2", (2, 2): "P3", (2, 3): "P4",
    (3, 1): "P3", (3, 2): "P4", (3, 3): "P4",
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    store.initialize()
    yield


app = FastAPI(title="svcdesk", lifespan=lifespan)


def error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError) -> JSONResponse:
    messages = [f"{'.'.join(str(part) for part in item['loc'][1:])}: {item['msg']}" for item in exc.errors()]
    return JSONResponse(status_code=422, content=error_payload("validation", "; ".join(messages)))


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(_, exc: StarletteHTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        detail = exc.detail
    else:
        code = "not_found" if exc.status_code == 404 else "http_error"
        detail = {"code": code, "message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content={"error": detail})


def fail(status: int, code: str, message: str) -> None:
    raise HTTPException(status_code=status, detail={"code": code, "message": message})


def request_now(x_test_clock: Annotated[str | None, Header(alias="X-Test-Clock")] = None) -> datetime:
    enabled = os.environ.get("SVCDESK_TEST_CLOCK", "").lower() in {"1", "true"}
    if not enabled or x_test_clock is None:
        return real_now()
    try:
        return parse_instant(x_test_clock)
    except (TypeError, ValueError):
        fail(422, "invalid_clock", "X-Test-Clock must be an offset-aware RFC 3339 instant")
    raise AssertionError("unreachable")


Now = Annotated[datetime, Depends(request_now)]


def priority_for(impact: int, urgency: int, vip: bool) -> str:
    priority = MATRIX[(impact, urgency)]
    return "P2" if vip and priority in {"P3", "P4"} else priority


def require_ticket(ticket_id: str) -> dict[str, Any]:
    ticket = store.get(ticket_id)
    if ticket is None:
        fail(404, "not_found", f"ticket {ticket_id!r} was not found")
    return ticket


@app.get("/health")
def health(_: Now) -> dict[str, str]:
    return {"status": "ok", "service": "svcdesk"}


@app.post("/dora/metrics")
def dora_metrics(body: Annotated[Any, Body()]) -> dict[str, Any]:
    try:
        return dora.calculate(body)
    except ValueError as exc:
        fail(422, "invalid_event_log", str(exc))
    raise AssertionError("unreachable")


@app.get("/dora/ticket-events")
def ticket_events() -> list[dict[str, str]]:
    phases = (
        ("created", "created_at", "new"),
        ("acknowledged", "acknowledged_at", "acknowledged"),
        ("resolved", "resolved_at", "resolved"),
        ("closed", "closed_at", "closed"),
    )
    events = [
        {"ticket_id": ticket["id"], "at": ticket[field], "phase": phase,
         "priority": ticket["priority"], "state": state}
        for ticket in store.list_all()
        for phase, field, state in phases
        if ticket[field] is not None
    ]
    return sorted(events, key=lambda event: (parse_instant(event["at"]), event["ticket_id"], event["phase"]))


@app.post("/tickets", status_code=201)
def create_ticket(payload: TicketCreate, now: Now) -> dict[str, Any]:
    reporter = payload.reporter
    priority = priority_for(payload.impact, payload.urgency, reporter.vip)
    ack_due, resolve_due = due_instants(now, priority)
    record = {
        "id": str(uuid4()),
        "title": payload.title,
        "description": payload.description,
        "reporter_name": reporter.name,
        "reporter_email": reporter.email,
        "reporter_vip": int(reporter.vip),
        "impact": payload.impact,
        "urgency": payload.urgency,
        "priority": priority,
        "state": "new",
        "created_at": utc_text(now),
        "acknowledged_at": None,
        "resolved_at": None,
        "closed_at": None,
        "related_to": payload.related_to,
        "ack_due_at": utc_text(ack_due),
        "resolve_due_at": utc_text(resolve_due),
    }
    return store.insert(record)


@app.get("/tickets")
def list_tickets(
    _: Now,
    state: Annotated[str | None, Query()] = None,
    priority: Annotated[str | None, Query()] = None,
) -> list[dict[str, Any]]:
    return store.list_all(state=state, priority=priority)


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str, _: Now) -> dict[str, Any]:
    return require_ticket(ticket_id)


@app.get("/tickets/{ticket_id}/sla")
def get_sla(ticket_id: str, now: Now) -> dict[str, Any]:
    ticket = require_ticket(ticket_id)
    ack_due = parse_instant(ticket["sla"]["ack_due_at"])
    resolve_due = parse_instant(ticket["sla"]["resolve_due_at"])
    acknowledged_at = ticket["acknowledged_at"]
    resolved_at = ticket["resolved_at"]
    ack_breached = (
        now > ack_due if acknowledged_at is None else parse_instant(acknowledged_at) > ack_due
    )
    resolve_breached = (
        now > resolve_due if resolved_at is None else parse_instant(resolved_at) > resolve_due
    )
    paused = ticket["state"] not in {"resolved", "closed"} and not is_business_time(now)
    return {
        "priority": ticket["priority"],
        "ack_due_at": ticket["sla"]["ack_due_at"],
        "resolve_due_at": ticket["sla"]["resolve_due_at"],
        "ack_breached": ack_breached,
        "resolve_breached": resolve_breached,
        "paused": paused,
    }


@app.post("/tickets/{ticket_id}/{action}")
def act_on_ticket(ticket_id: str, action: str, now: Now) -> dict[str, Any]:
    ticket = require_ticket(ticket_id)
    state = ticket["state"]
    now_text = utc_text(now)

    if action == "ack" and state == "new":
        return store.update(ticket_id, state="acknowledged", acknowledged_at=now_text)  # type: ignore[return-value]
    if action == "start" and state == "acknowledged":
        return store.update(ticket_id, state="in_progress")  # type: ignore[return-value]
    if action == "resolve" and state == "in_progress":
        return store.update(ticket_id, state="resolved", resolved_at=now_text)  # type: ignore[return-value]
    if action == "close" and state == "resolved":
        return store.update(ticket_id, state="closed", closed_at=now_text)  # type: ignore[return-value]
    if action == "reopen" and state == "resolved":
        resolved_at = parse_instant(ticket["resolved_at"])
        if now <= resolved_at + timedelta(days=7):
            return store.update(
                ticket_id, state="in_progress", resolved_at=None, closed_at=None
            )  # type: ignore[return-value]
        fail(409, "reopen_window_expired", "the seven-day reopen window has expired")
    if action == "reopen" and state == "closed":
        fail(409, "ticket_closed", "closed tickets are immutable")
    fail(409, "invalid_transition", f"cannot {action} a ticket in state {state}")
    raise AssertionError("unreachable")
