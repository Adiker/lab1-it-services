# ai-generated: 100% - Codex implemented request validation from the course ticket model.
"""Validated client-owned fields for ticket creation."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


StrictLevel = Annotated[int, Field(strict=True, ge=1, le=3)]


class ReporterInput(BaseModel):
    """Reporter fields accepted from a client."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1, max_length=100)
    email: str | None = None
    vip: bool = False


class TicketCreate(BaseModel):
    """Create payload; server-owned and unknown fields are deliberately ignored."""

    model_config = ConfigDict(extra="ignore")

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)
    reporter: ReporterInput
    impact: StrictLevel
    urgency: StrictLevel
    related_to: str | None = None
