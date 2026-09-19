# ai-generated: 100% - Codex implemented the SQLite ticket repository and response mapping.
"""Small SQLite persistence layer for tickets."""

import os
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any


COLUMNS = (
    "id", "title", "description", "reporter_name", "reporter_email", "reporter_vip",
    "impact", "urgency", "priority", "state", "created_at", "acknowledged_at",
    "resolved_at", "closed_at", "related_to", "ack_due_at", "resolve_due_at",
)


def database_path() -> str:
    return os.environ.get("SVCDESK_DB", "/data/svcdesk.db")


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(database_path(), timeout=30)
    connection.row_factory = sqlite3.Row
    return connection


def initialize() -> None:
    path = Path(database_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                reporter_name TEXT NOT NULL,
                reporter_email TEXT,
                reporter_vip INTEGER NOT NULL,
                impact INTEGER NOT NULL,
                urgency INTEGER NOT NULL,
                priority TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                acknowledged_at TEXT,
                resolved_at TEXT,
                closed_at TEXT,
                related_to TEXT,
                ack_due_at TEXT NOT NULL,
                resolve_due_at TEXT NOT NULL
            )
            """
        )


def to_ticket(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "reporter": {
            "name": row["reporter_name"],
            "email": row["reporter_email"],
            "vip": bool(row["reporter_vip"]),
        },
        "impact": row["impact"],
        "urgency": row["urgency"],
        "priority": row["priority"],
        "state": row["state"],
        "created_at": row["created_at"],
        "acknowledged_at": row["acknowledged_at"],
        "resolved_at": row["resolved_at"],
        "closed_at": row["closed_at"],
        "related_to": row["related_to"],
        "sla": {
            "ack_due_at": row["ack_due_at"],
            "resolve_due_at": row["resolve_due_at"],
        },
    }


def insert(ticket: dict[str, Any]) -> dict[str, Any]:
    values = tuple(ticket[column] for column in COLUMNS)
    placeholders = ", ".join("?" for _ in COLUMNS)
    with connect() as db:
        db.execute(f"INSERT INTO tickets ({', '.join(COLUMNS)}) VALUES ({placeholders})", values)
    return get(ticket["id"])  # type: ignore[return-value]


def get(ticket_id: str) -> dict[str, Any] | None:
    with connect() as db:
        row = db.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    return to_ticket(row) if row is not None else None


def list_all(state: str | None = None, priority: str | None = None) -> list[dict[str, Any]]:
    clauses: list[str] = []
    values: list[str] = []
    if state is not None:
        clauses.append("state = ?")
        values.append(state)
    if priority is not None:
        clauses.append("priority = ?")
        values.append(priority)
    sql = "SELECT * FROM tickets"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    with connect() as db:
        rows: Iterable[sqlite3.Row] = db.execute(sql, values).fetchall()
    return [to_ticket(row) for row in rows]


def update(ticket_id: str, **changes: Any) -> dict[str, Any] | None:
    if not changes:
        return get(ticket_id)
    assignments = ", ".join(f"{column} = ?" for column in changes)
    values = [*changes.values(), ticket_id]
    with connect() as db:
        db.execute(f"UPDATE tickets SET {assignments} WHERE id = ?", values)
    return get(ticket_id)
