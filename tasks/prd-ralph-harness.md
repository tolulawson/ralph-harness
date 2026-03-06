# PRD: Ralph Harness

## Introduction

Create a Codex-native repository pattern that lets a fresh Codex run resume work from disk, decompose work into epochs and numbered specs, and advance each spec through tasks, branch work, GitHub PR lifecycle, review, verification, and release without relying on long-lived chat context or a Bash control loop.

## Goals

- Make the repo itself the durable source of truth for queue state, logs, reports, and task progress.
- Give Codex enough structure to continue work from a fresh run with bounded context.
- Keep the harness Codex-native by using `AGENTS.md`, repo-local skills, role configs, GitHub PR metadata, and file artifacts.

## Epoch Map

### E001: Foundation Bootstrap

- Theme: Establish the Codex loader, constitution, queue contracts, runtime skills, and one completed example spec.
- Intended specs:
  - `001-self-bootstrap-harness`

### E002: Queue And PR Execution

- Theme: Extend installed target projects with deeper queue automation, PR synchronization, and downstream execution hardening.
- Intended specs:
  - `002-spec-queue-runtime`
  - `003-github-pr-release-loop`

## User Stories

### US-001: Resume the harness from disk

**Description:** As an orchestrating Codex agent, I want durable runtime state and recent evidence on disk so I can continue the loop from any fresh run.

**Acceptance Criteria:**

- [x] Canonical workflow state exists in JSON.
- [x] A canonical spec queue exists in JSON.
- [x] A human-readable Markdown mirror exists.
- [x] An append-only event ledger exists.
- [x] Recent reports provide enough context to resume work.

### US-002: Delegate focused role work

**Description:** As an orchestrating Codex agent, I want role-specific workers with dedicated skills so the loop stays organized and resumable.

**Acceptance Criteria:**

- [x] Each role has a dedicated config file.
- [x] Each role has one primary repo-local skill.
- [x] Each role has a clear stop condition and report contract.
- [x] Queue and PR responsibilities are explicit in the orchestrator and release roles.

### US-003: Process numbered specs sequentially

**Description:** As a maintainer, I want the harness to treat numbered specs as the unit of execution so each feature can complete review and verification before the next spec starts.

**Acceptance Criteria:**

- [x] The harness stores numbered spec IDs and spec statuses.
- [x] The orchestrator can determine the next ready spec from queue state.
- [x] Each spec owns its own task list, branch context, and PR metadata.
- [x] The example artifacts show one completed numbered spec.

## Functional Requirements

- FR-1: The harness must store canonical runtime state in `.ralph/state/workflow-state.json`.
- FR-2: The harness must store canonical spec queue state in `.ralph/state/spec-queue.json`.
- FR-3: The harness must mirror workflow state into `.ralph/state/workflow-state.md`.
- FR-4: The harness must store append-only events in `.ralph/logs/events.jsonl`.
- FR-5: The harness must declare role configs in `.codex/config.toml` and `agents/*.toml`.
- FR-6: The harness must provide repo-local skills in `.agents/skills/*`.
- FR-7: The harness must generate and track numbered specs under `specs/<spec-id>-<slug>/`.
- FR-8: The harness must record GitHub PR metadata for installed target projects.

## Non-Goals

- No standalone orchestrator service in v1.
- No custom MCP server in v1.
- No requirement to support non-Codex runtimes in v1.

## Success Metrics

- A fresh Codex run can identify the current spec, next task, and queue head in under one minute by reading the canonical files.
- Each role has a single clear artifact contract and a matching report contract.
- The reference repository leaves a complete, inspectable trail of state, logs, reports, spec index, and review notes.

## Open Questions

- Which additional domain skills should be attached to the implement or verify roles over time?
- Whether a future helper tool should synchronize GitHub PR metadata automatically instead of relying on agent-driven file updates.
