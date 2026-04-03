---
description: Resume the Ralph runtime from disk.
---

Run `ralph-execute` using the canonical Ralph source of truth at `skills/ralph-execute/SKILL.md`.

Read the shared Ralph runtime files first, preserve any existing managed Ralph loader blocks, and follow the canonical contract instead of rewriting it from memory.
Keep the invoking thread thin: launch a dedicated Ralph orchestrator subagent immediately, then wait and relay its result instead of orchestrating inline on the command thread.
That orchestrator should fill the admitted-spec execution window with worker subagents up to the bounded thread budget, then reconcile completed worker output itself instead of spawning multiple orchestrators or tolerating inline worker execution.
