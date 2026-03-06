---
name: orchestrator
description: Coordinate the Codex-native Ralph harness loop by reading runtime state, managing the FIFO spec queue, selecting the next task, validating outputs, appending one event, and synchronizing state files.
---

# Orchestrator

## Use When

- A fresh run needs to resume the harness.
- A role has finished and the next role must be chosen.
- Shared state, reports, the spec queue, and event history must be synchronized.

## Inputs

- `.ralph/constitution.md`
- `.ralph/policy/project-policy.md`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- latest report from `last_report_path`
- active spec artifacts in `specs/<spec-id>-<slug>/`
- `specs/INDEX.md`
- `tasks/todo.md`
- recent lines from `.ralph/logs/events.jsonl`

## Workflow

1. Read the harness constitution first.
2. Read project policy second.
3. Read the canonical workflow state.
4. Read the canonical spec queue.
5. Activate the oldest ready spec if no active spec is already in progress.
6. Load only the active spec artifacts and the latest report.
7. Tail the recent event window instead of loading the full event log.
8. Choose the next task in this order:
   - first `in_progress`
   - else first `ready`
   - else first `review_failed`
   - else first `verification_failed`
   - else advance the spec toward PR, merge, or completion
9. Decide the next role from spec status, task status, PR state, and next action.
10. Spawn exactly one sub-agent with bounded inputs, a required report path, and a clear stop condition.
11. Validate that the sub-agent wrote the required artifacts.
12. Append one event to `.ralph/logs/events.jsonl`.
13. Update `.ralph/state/workflow-state.json`.
14. Update `.ralph/state/spec-queue.json`.
15. Regenerate `.ralph/state/workflow-state.md`.
16. Regenerate `specs/INDEX.md` when queue-visible metadata changes.

## Outputs

- updated workflow state JSON
- updated spec queue JSON
- updated workflow state Markdown
- updated spec register when needed
- one event log entry
- orchestrator report

## Stop Condition

Stop once the next role is assigned or the workflow has been moved to `blocked` or `complete`.
