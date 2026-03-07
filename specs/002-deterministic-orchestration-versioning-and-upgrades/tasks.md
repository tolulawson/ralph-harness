# Tasks: 002-deterministic-orchestration-versioning-and-upgrades

## Metadata

- Spec id: `002`
- Epoch id: `E002`
- Status: `done`
- Branch: `codex/002-deterministic-orchestration-versioning-and-upgrades`
- PR number: `null`

## Phase 1: Runtime Contracts

- [x] 002-T001 [US1] Enable official Codex multi-agent support in the shipped control plane and rewrite the orchestrator contract around spawn/wait semantics plus queue-drain stop conditions.
- [x] 002-T002 [US2] Add the runtime-contract split, canonical `task-state.json` template, and worker or orchestrator ownership rules across shipped and dogfood runtime files.

## Phase 2: Release And Upgrade Surface

- [x] 002-T003 [US3] Add `VERSION`, `UPGRADING.md`, `src/upgrade-manifest.txt`, `src/.ralph/harness-version.json`, and the public `ralph-upgrade` skill.
- [x] 002-T004 [US3] Add validation scripts plus GitHub Actions CI and release workflows for tagged scaffold releases.

## Phase 3: Dogfood Proof

- [x] 002-T005 [US2] Update the source repo dogfood runtime, reports, queue state, and lessons so spec `002` proves the new contracts without touching installed target repos.

## Review Notes

- This spec intentionally stops at source-repo dogfooding and fixture-based validation.
- Target-repo retrofits remain separate work even though the upgrade surface is now present.

## Canonical Task State

- `specs/002-deterministic-orchestration-versioning-and-upgrades/task-state.json` is the machine-readable lifecycle source of truth for these tasks.
