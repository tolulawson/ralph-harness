# PRD: Ralph Harness

## Introduction

Create a Codex-native repository pattern that lets a fresh Codex run resume work from disk, decompose work into epochs and numbered specs, and advance each spec through tasks, branch work, GitHub PR lifecycle, review, verification, and release without relying on long-lived chat context or a Bash control loop.

## Goals

- Make the repo itself the durable source of truth for queue state, logs, reports, and task progress.
- Give Codex enough structure to continue work from a fresh run with bounded context.
- Keep the harness Codex-native by using `AGENTS.md`, repo-local skills, GitHub Actions, semver tags, GitHub PR metadata, and file artifacts.

## Epoch Map

### E001: Foundation Bootstrap

- Theme: Establish the Codex loader, constitution, queue contracts, runtime skills, and one completed example spec.
- Intended specs:
  - `001-self-bootstrap-harness`

### E002: Deterministic Runtime And Release Surface

- Theme: Make orchestration deterministic with official Codex multi-agent controls, add canonical task lifecycle state, and add a versioned install, release, and upgrade contract.
- Intended specs:
  - `002-deterministic-orchestration-versioning-and-upgrades`

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

### US-004: Version and upgrade the scaffold safely

**Description:** As a maintainer, I want to cut tagged scaffold releases and upgrade installed repos without overwriting project-owned runtime records.

**Acceptance Criteria:**

- [x] The harness has a canonical semver source and tagged release workflow.
- [x] The harness publishes an upgrade manifest and upgrade guide.
- [x] The harness records installed version metadata in the target repo.
- [x] The harness preserves project-owned runtime files during upgrade by default.

## Functional Requirements

- FR-1: The harness must store canonical runtime state in `.ralph/state/workflow-state.json`.
- FR-2: The harness must store canonical spec queue state in `.ralph/state/spec-queue.json`.
- FR-3: The harness must mirror workflow state into `.ralph/state/workflow-state.md`.
- FR-4: The harness must store append-only events in `.ralph/logs/events.jsonl`.
- FR-5: The harness must declare role configs in `.codex/config.toml` and `agents/*.toml`.
- FR-6: The harness must provide repo-local skills in `.agents/skills/*`.
- FR-7: The harness must generate and track numbered specs under `specs/<spec-id>-<slug>/`.
- FR-8: The harness must record GitHub PR metadata for installed target projects.
- FR-9: The harness must use official Codex multi-agent features for deterministic worker delegation and waiting.
- FR-10: The harness must publish tagged scaffold releases with a canonical version source and safe upgrade contract.

## Non-Goals

- No standalone orchestrator service in v1.
- No custom MCP server in v1.
- No requirement to support non-Codex runtimes in v1.
- No source-repo task to retrofit already-installed target repos automatically.

## Success Metrics

- A fresh Codex run can identify the current spec, next task, and queue head in under one minute by reading the canonical files.
- Each role has a single clear artifact contract and a matching report contract.
- The reference repository leaves a complete, inspectable trail of state, logs, reports, spec index, review notes, and release metadata.

## Open Questions

- Which additional domain skills should be attached to the implement or verify roles over time?
- Whether a future helper tool should synchronize GitHub PR metadata automatically instead of relying on agent-driven file updates.
