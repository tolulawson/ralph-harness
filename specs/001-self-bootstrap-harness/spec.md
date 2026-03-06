# Feature Spec: 001-self-bootstrap-harness

## Metadata

- Spec id: `001`
- Epoch id: `E001`
- Status: `done`
- Branch: `codex/001-self-bootstrap-harness`
- PR number: `null`

## Summary

This numbered spec establishes the first working version of the Codex-native Ralph harness inside this repository. The spec must create the Codex loader, harness constitution, queue-aware runtime state contracts, repo-local role skills, and a completed example trail that proves the harness can persist and recover queue state from disk.

## Scope

- In scope: the Codex loader, constitution, role configs, repo-local skills, queue state files, event log, templates, master PRD, numbered spec index, and bootstrap reports.
- Out of scope: a custom MCP server, a separate orchestration daemon, and non-Codex runtime support.

## User Stories

### US-001: Control plane and runtime durability

- Actor: Orchestrating Codex agent
- Goal: Resume work from canonical state, the canonical spec queue, recent reports, and recent events
- Acceptance: Workflow state, spec queue, event log, policy, templates, and role configs all exist and are internally consistent

### US-002: Role-driven delegation

- Actor: Orchestrating Codex agent
- Goal: Delegate focused work to transient roles with narrow skill boundaries
- Acceptance: Every role has a config file, a repo-local skill, a clear output contract, and a defined stop condition

### US-003: Numbered spec queue proof

- Actor: Repo maintainer
- Goal: See one completed numbered spec represented in the harness itself
- Acceptance: The example spec has a PRD, spec, plan, tasks, reports, events, queue entry, and completed workflow state

## Requirements

- R1: The repo must include a thin `AGENTS.md` loader that points Codex to `.ralph/constitution.md`, `.ralph/policy/project-policy.md`, `.ralph/state/workflow-state.json`, `.ralph/state/spec-queue.json`, and the latest report.
- R2: The repo must include `.ralph/constitution.md` that defines the queue-driven orchestration loop, state rules, role boundaries, skill policy, git policy, and verification standard.
- R3: The repo must include `.codex/config.toml` with agent declarations that point to per-role config files.
- R4: Each role config must declare `model`, `model_reasoning_effort`, `sandbox_mode`, and `developer_instructions`.
- R5: Repo-local skills must live in `.agents/skills/` and map one primary workflow to each role.
- R6: The runtime contract must exist under `.ralph/` and include constitution, canonical workflow state, canonical spec queue, event logs, reports, policy, templates, and summaries.
- R7: The example numbered spec artifacts must exist under `tasks/` and `specs/001-self-bootstrap-harness/`.

## Edge Cases

- A fresh run starts without conversational memory and must still reconstruct the active spec and next action from files alone.
- Review or verification can fail; the harness must preserve reports and history even when the queue entry is moved to a failure status later.
- The event log may grow long; normal resume logic must use recent events rather than scanning the full history.

## Delivery Notes

- Keep v1 Codex-native and file-driven.
- Favor stable, inspectable artifacts over automation that hides decisions.
- Leave room for future helper skills and optional tooling without requiring them now.
