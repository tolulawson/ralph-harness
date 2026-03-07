# Ralph Runtime Contract

This file is the generic dogfood-runtime doctrine for the Ralph harness source repository.

It mirrors the installed runtime contract closely enough for the source repository to dogfood the same orchestration model while keeping the root constitution as source-repo truth.

## Runtime Priority

Interpret the dogfood runtime in this order:

1. `.ralph/constitution.md`
2. this runtime contract
3. `.ralph/policy/project-policy.md`
4. `.ralph/state/workflow-state.json`
5. `.ralph/state/spec-queue.json`
6. active spec artifacts and latest role reports

## Required Runtime Features

- Official Codex multi-agent support is required.
- The orchestrator must use built-in Codex agent controls such as `spawn_agent` and `wait`.
- Exactly one worker role may be active at a time for normal execution.

## Core Loop

1. read `.ralph/state/workflow-state.json`
2. read `.ralph/policy/project-policy.md`
3. read `.ralph/state/spec-queue.json`
4. determine the active spec or activate the oldest ready spec in FIFO order
5. read the latest report referenced by `last_report_path`
6. read the active spec artifacts, including `task-state.json` when present
7. tail only the recent event window
8. choose the next task in this order:
   - first `in_progress`
   - else first `ready`
   - else first `review_failed`
   - else first `verification_failed`
   - else advance the spec toward PR, merge, or completion
9. decide the next role from spec status, task lifecycle state, PR state, and next action
10. spawn exactly one worker role with bounded inputs and a required report path
11. wait for that worker to finish
12. validate the worker outputs
13. write the orchestrator report
14. append one orchestrator-owned event
15. update shared state and projections
16. continue dispatching until a stop condition occurs

## Stop Conditions

The orchestrator may stop only when one of these is true:

- the queue is empty
- the active spec or task is blocked
- review failed
- verification failed
- release failed
- a credential, approval, or external human decision is required
- the orchestration safety cap is reached

The default orchestration safety cap is `200` role handoffs in one invocation.

## Shared-State Ownership

Only the orchestrator may update:

- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/workflow-state.md`
- `.ralph/logs/events.jsonl`
- `specs/INDEX.md`
- lifecycle transitions inside `specs/<spec-id>-<slug>/task-state.json`

Worker roles must not silently mutate shared queue state or append orchestrator events.

## Task Lifecycle Contract

Each numbered spec should maintain:

- `tasks.md` as the human-readable task projection
- `task-state.json` as the canonical machine-readable task lifecycle registry

Task generation seeds `task-state.json`. After that, the orchestrator owns lifecycle transitions based on worker reports.

Each task record in `task-state.json` should include:

- `task_id`
- `status`
- `last_role`
- `last_report_path`
- `updated_at`
- optional `blocked_reason`
- optional `review_result`
- optional `verification_result`
