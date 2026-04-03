---
description: Produce numbered specs, synchronized planning artifacts, and execution-ready task registries.
---

Run `ralph-plan` using the canonical Ralph source of truth at `skills/ralph-plan/SKILL.md`.

Read the shared Ralph runtime files first, preserve any existing managed Ralph loader blocks, and follow the canonical contract instead of rewriting it from memory.
Keep the invoking thread thin: launch a dedicated Ralph planning coordinator subagent immediately, let that coordinator delegate `specify`, same-batch `research`, `plan`, `task-gen`, and `plan-check` as needed, then wait and relay its result instead of planning inline on the command thread.
