<!-- ai-generated: 100% - Codex produced the architecture and implementation plan from the course API contract. -->
# Implementation plan

## Architecture

Use Python 3.13, FastAPI, Pydantic, Uvicorn, SQLite from the standard library, and `zoneinfo.ZoneInfo("Europe/Warsaw")`. Keep the application in `src/svcdesk/`, with separate modules for API models, persistence, business-time arithmetic, and lifecycle operations. All database access is local; no runtime component contacts the network.

## Data flow

1. Middleware or a dependency resolves per-request `now` from `X-Test-Clock` when enabled and converts it to UTC.
2. Pydantic validates client-owned create fields while allowing and ignoring unknown/server-owned fields.
3. The service computes matrix priority, applies C3=`vip`, calculates both C1=`business` SLA due instants, and writes the complete ticket to SQLite.
4. Read endpoints deserialize stored tickets. Action endpoints load a ticket, validate the state/window against request-local `now`, update state/timestamps atomically, and return the full record.
5. The SLA endpoint evaluates breach and pause without mutating the ticket.

## Deployment

Pin Python dependencies in `requirements.txt`. Build one repository Dockerfile, install dependencies at build time, copy `src/`, create `/data`, and start Uvicorn on `0.0.0.0:8080`. Compose uses a named volume, an HTTP healthcheck implemented with Python's standard library, and a profile-gated tests service built from the same repository.

## Verification

Run unit tests for business-time boundaries and state transitions, then run the profile test suite, Compose readiness, and `./itsmlab.sh verify 1 --json report.json`. Confirm observations are C1=`business`, C2=`immutable`, C3=`vip`, Core passes except the expected local L1-CORE-5 skip, all three Stretch items pass, disclosures are complete, and the committed run is not dirty.
