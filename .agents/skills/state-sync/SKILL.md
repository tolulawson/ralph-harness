---
name: state-sync
description: Synchronize the human-readable workflow mirror with the canonical workflow JSON after a role completes or the orchestrator advances the state.
---

# State Sync

## Use When

- `.ralph/state/workflow-state.json` has changed.

## Inputs

- `.ralph/shared/state/workflow-state.json` or the resolved canonical `.ralph/state/workflow-state.json`
- `.ralph/templates/workflow-state-template.md`

## Workflow

1. Read the canonical JSON state, resolving shared-state paths to the canonical checkout directly or through `.ralph/shared/` when the role runs from a worktree.
2. Treat the canonical `.ralph/state/workflow-state.json` as the source of truth and `.ralph/state/workflow-state.md` as a projection only.
3. Render the canonical `.ralph/state/workflow-state.md` from the canonical JSON semantics instead of hand-editing individual lines.
4. Preserve the current interrupt-aware projection rows for resume stack depth, current interrupt spec, and resume pending state.
5. Keep the Markdown concise and directly inspectable.

## Outputs

- updated `.ralph/state/workflow-state.md`

## Stop Condition

Stop after the Markdown mirror matches the JSON state.
