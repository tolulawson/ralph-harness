# Feature Spec: 002-deterministic-orchestration-versioning-and-upgrades

## Metadata

- Spec id: `002`
- Epoch id: `E002`
- Status: `done`
- Branch: `codex/002-deterministic-orchestration-versioning-and-upgrades`
- PR number: `null`

## Summary

This numbered spec hardens the Ralph harness around deterministic Codex multi-agent orchestration, strict orchestrator ownership of shared runtime state, a canonical per-spec task lifecycle registry, and a semver-based release and upgrade contract for the shipped scaffold.

## Scope

- In scope: official Codex multi-agent configuration, orchestrator and worker role contract updates, task-state scaffolding, runtime-contract split, version metadata, install/upgrade docs, upgrade skill, validation scripts, and GitHub Actions release workflows.
- Out of scope: retrofitting already-installed target repositories, non-Codex runtime support, and target-project-specific migrations.

## User Stories

### US-001: Deterministic worker delegation

- Actor: Orchestrating Codex agent
- Goal: Spawn exactly one worker, wait for it to finish, and keep draining the queue until a true stop condition occurs
- Acceptance: The runtime contract, orchestrator config, public execute skill, and control plane all require official Codex multi-agent behavior and stop conditions

### US-002: Shared-state ownership and task lifecycle

- Actor: Harness maintainer
- Goal: Keep queue state, workflow state, event logs, and task lifecycle transitions under orchestrator control
- Acceptance: Worker skills no longer claim ownership of shared state, task-state exists as a canonical lifecycle file, and the source repo dogfoods the new model

### US-003: Versioned install and upgrade surface

- Actor: Target-repo maintainer
- Goal: Install or upgrade the harness from tagged releases with clear contracts and safe overwrite boundaries
- Acceptance: The repo ships VERSION, upgrade docs, an upgrade manifest, a public upgrade skill, and CI/release workflows that validate the contract

## Requirements

- R1: The shipped scaffold must enable official Codex multi-agent support in `src/.codex/config.toml`.
- R2: The orchestrator contract must require built-in multi-agent spawn/wait semantics and queue draining until a documented stop condition occurs.
- R3: Only the orchestrator may mutate shared queue state, workflow state, event logs, state Markdown, and spec index projections.
- R4: Each spec may use `task-state.json` as the canonical machine-readable lifecycle registry, while `tasks.md` remains the human-readable projection.
- R5: The installed scaffold must split project-specific mission rules from the generic runtime doctrine via `.ralph/constitution.md` and `.ralph/runtime-contract.md`.
- R6: The source repo must expose a canonical version source, tagged release workflow, upgrade manifest, upgrade guide, and public upgrade skill.

## Edge Cases

- Installed target repos may already have a custom `AGENTS.md`, so install and upgrade flows must refresh only a managed Ralph block.
- Legacy installs may not yet have `.ralph/runtime-contract.md`, `.ralph/harness-version.json`, or `task-state.json`.
- The orchestrator must stop safely when credentials, approvals, or runtime blockers require a human instead of looping indefinitely.

## Delivery Notes

- Treat official Codex multi-agent support as required, not optional.
- Keep the source scaffold contract versioned and release-focused rather than tied to root dogfood history.
- Validate install and upgrade behavior in controlled fixture repos only.
