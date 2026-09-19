# Agent policy

The implementation agent is intentionally denied only commands with an external or host-wide blast radius:

- Bash(git push:*): Publishing commits can trigger CI and receipts, so it requires an explicit owner review.
- Bash(git tag:*): Receipt tags are immutable attempts and must be created only after clean verification.
- Bash(docker system prune:*): Host-wide pruning can remove unrelated images and caches outside this laboratory.

Local editing, builds, Compose project operations, and tests remain available so the agent can complete and validate the service.
