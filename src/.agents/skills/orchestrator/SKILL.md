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
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- recent lines from `.ralph/context/learning-log.jsonl` when needed
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
3. Read project truths, project facts, and promoted learning summary.
4. Read the canonical workflow state.
5. Read the canonical spec queue.
6. Activate the oldest ready spec if no active spec is already in progress.
7. Load only the active spec artifacts and the latest report.
8. Tail the recent event window instead of loading the full event log.
9. Read only the recent learning log window when diagnosing or promoting learnings.
10. Choose the next task in this order:
   - first `in_progress`
   - else first `ready`
   - else first `review_failed`
   - else first `verification_failed`
   - else advance the spec toward PR, merge, or completion
11. Decide the next role from spec status, task status, PR state, and next action.
12. Spawn exactly one sub-agent with bounded inputs, a required report path, and a clear stop condition.
13. Validate that the sub-agent wrote the required artifacts.
14. Append one event to `.ralph/logs/events.jsonl`.
15. Append candidate learnings from the role report to `.ralph/context/learning-log.jsonl`.
16. Use the `learning` helper skill to classify and promote validated truths or facts when justified.
17. Update `.ralph/state/workflow-state.json`.
18. Update `.ralph/state/spec-queue.json`.
19. Regenerate `.ralph/state/workflow-state.md`.
20. Regenerate `specs/INDEX.md` when queue-visible metadata changes.

## Outputs

- updated workflow state JSON
- updated spec queue JSON
- updated workflow state Markdown
- updated spec register when needed
- updated learning log, summary, truths, or facts when needed
- one event log entry
- orchestrator report

## Stop Condition

Stop once the next role is assigned or the workflow has been moved to `blocked` or `complete`.
