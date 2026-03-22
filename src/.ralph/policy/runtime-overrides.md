# Runtime Overrides

This file is the project-owned extension surface for runtime-specific rules that go beyond the scaffold's base `.ralph/runtime-contract.md`.

Use this file for project-specific runtime additions such as:

- local toolchain expectations that affect orchestration behavior
- extra runtime guardrails or escalation rules
- project-specific execution constraints that should apply across roles

Guardrails:

- keep the base `.ralph/runtime-contract.md` scaffold-owned and unchanged
- prefer additive rules here rather than restating the full base contract
- do not contradict the base runtime contract unless the project explicitly accepts the divergence and understands the maintenance cost
- upgrades preserve this file; direct edits to `.ralph/runtime-contract.md` may block upgrade preflight

## Current Overrides

- None.
