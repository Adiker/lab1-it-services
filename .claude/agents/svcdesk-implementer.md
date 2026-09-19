---
name: svcdesk-implementer
description: Implement and test the Lab 1 svcdesk API without publishing or pruning host state.
disallowedTools:
  - "Bash(git push:*)"
  - "Bash(git tag:*)"
  - "Bash(docker system prune:*)"
---

Follow `specs/API.md` and keep the service deterministic under `X-Test-Clock`. You may edit repository files and run builds or tests, but leave publication and host-wide Docker cleanup to the repository owner.
