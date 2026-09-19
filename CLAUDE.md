# svcdesk agent instructions

Implement and review the service against `specs/API.md`. Keep all three declared conflict resolutions synchronized with `DECISIONS.md`, source code, and tests. Run the local checker before proposing a release tag. Do not move an existing receipt tag.

The scoped implementation agent is defined in `.claude/agents/svcdesk-implementer.md`; its denylist prevents publishing or destructive Docker cleanup during code generation.
