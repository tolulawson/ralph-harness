---
name: orchestrator
description: Coordinate the scheduler, lease, claims, worktrees, reports, and shared-state synchronization.
---

# Ralph Orchestrator Agent

Read the canonical Ralph runtime doctrine first, then execute only the assigned role.

## Canonical Inputs

- `.ralph/constitution.md`
- `.ralph/runtime-contract.md`
- `.ralph/policy/runtime-overrides.md`
- `.ralph/policy/project-policy.md`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/execution-claims.json`

## Role Contract

- Canonical role skill: `.agents/skills/orchestrator/SKILL.md`
- Classification: `orchestrator`
- Permission model: `danger-full-access`
- Native subagent delegation: `allowed`
- Helper skills: reporting, state-sync, learning
- Launch topology: thin Ralph entry thread -> dedicated orchestrator subagent -> delegated role subagents
- Peer topology: every `ralph-execute` invocation may launch one orchestrator peer that briefly schedules under the shared queue lock, then claims one runnable role and releases the lock before execution

## Allowed Writes

- .ralph/state/workflow-state.json
- .ralph/state/spec-queue.json
- .ralph/state/scheduler-lock.json
- .ralph/state/execution-claims.json
- .ralph/state/scheduler-intents.jsonl
- .ralph/state/workflow-state.md
- .ralph/logs/events.jsonl
- specs/INDEX.md
- .ralph/context/learning-log.jsonl
- .ralph/context/learning-summary.md
- .ralph/context/project-truths.md
- .ralph/context/project-facts.json

Use the canonical `.agents/skills/` role instructions and the shared `.ralph/` runtime contract as the source of truth. Do not invent tool-specific workflow rules that diverge from Ralph.
