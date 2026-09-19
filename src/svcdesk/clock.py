# ai-generated: 100% - Codex implemented RFC 3339 parsing and DST-aware Warsaw business-time arithmetic.
"""Per-request time and SLA due-instant helpers."""

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


UTC = timezone.utc
WARSAW = ZoneInfo("Europe/Warsaw")
OPENING = time(8, 0)
CLOSING = time(16, 0)

TARGETS: dict[str, tuple[timedelta, timedelta]] = {
    "P1": (timedelta(minutes=15), timedelta(hours=4)),
    "P2": (timedelta(hours=1), timedelta(hours=8)),
    "P3": (timedelta(hours=4), timedelta(hours=24)),
    "P4": (timedelta(hours=8), timedelta(hours=72)),
}


def parse_instant(value: str) -> datetime:
    """Parse an offset-aware RFC 3339-like instant and normalize it to UTC."""

    normalized = value.strip()
    if normalized.endswith(("Z", "z")):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include an offset")
    return parsed.astimezone(UTC)


def utc_text(value: datetime) -> str:
    """Serialize an instant as whole-second UTC with a Z suffix."""

    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def real_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def is_business_day(day: date) -> bool:
    return day.weekday() < 5


def _local_at(day: date, at: time) -> datetime:
    return datetime.combine(day, at, tzinfo=WARSAW)


def _next_business_day(day: date) -> date:
    while not is_business_day(day):
        day += timedelta(days=1)
    return day


def align_to_business(value: datetime) -> datetime:
    """Move a Warsaw-local instant forward to the next open business window."""

    local = value.astimezone(WARSAW)
    day = local.date()
    if not is_business_day(day) or local.time() >= CLOSING:
        return _local_at(_next_business_day(day + timedelta(days=1)), OPENING)
    if local.time() < OPENING:
        return _local_at(day, OPENING)
    return local


def business_due(created_at: datetime, target: timedelta) -> datetime:
    """Consume a duration in local weekday windows, preserving the exact-closing tie."""

    cursor = align_to_business(created_at)
    remaining = target
    while True:
        closing = _local_at(cursor.date(), CLOSING)
        available = closing - cursor
        if remaining <= available:
            return (cursor + remaining).astimezone(UTC)
        remaining -= available
        cursor = _local_at(_next_business_day(cursor.date() + timedelta(days=1)), OPENING)


def due_instants(created_at: datetime, priority: str) -> tuple[datetime, datetime]:
    """C1=business: every priority consumes both targets in business time."""

    ack_target, resolve_target = TARGETS[priority]
    return business_due(created_at, ack_target), business_due(created_at, resolve_target)


def is_business_time(value: datetime) -> bool:
    local = value.astimezone(WARSAW)
    return is_business_day(local.date()) and OPENING <= local.time() < CLOSING
