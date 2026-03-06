---
name: state-sync
description: Synchronize the human-readable workflow mirror with the canonical workflow JSON after a role completes or the orchestrator advances the state.
---

# State Sync

## Use When

- `.ralph/state/workflow-state.json` has changed.

## Inputs

- `.ralph/state/workflow-state.json`
- `.ralph/templates/workflow-state-template.md`

## Workflow

1. Read the canonical JSON state.
2. Update `.ralph/state/workflow-state.md` so it matches the JSON semantics.
3. Keep the Markdown concise and directly inspectable.

## Outputs

- updated `.ralph/state/workflow-state.md`

## Stop Condition

Stop after the Markdown mirror matches the JSON state.
