---
description: Create or update the project PRD.
---

Run `ralph-prd` using the canonical Ralph source of truth at `skills/ralph-prd/SKILL.md`.

Read the shared Ralph runtime files first, preserve any existing managed Ralph loader blocks, and follow the canonical contract instead of rewriting it from memory.
Keep the invoking thread thin: launch a dedicated Ralph `prd` subagent immediately, then wait and relay its result instead of writing the PRD inline on the command thread.
