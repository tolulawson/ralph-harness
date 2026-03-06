# Tasks: 001-self-bootstrap-harness

## Metadata

- Spec id: `001`
- Epoch id: `E001`
- Status: `done`
- Branch: `codex/001-self-bootstrap-harness`
- PR number: `null`

## Phase 1: Control Plane

- [x] 001-T001 [US1] Scaffold the Codex loader, constitution, control plane directories, and runtime folders in `AGENTS.md`, `.codex/`, `agents/`, `.agents/skills/`, `.ralph/`, `tasks/`, and `specs/`.
- [x] 001-T002 [US1] Define the orchestration contract across `AGENTS.md`, `.ralph/constitution.md`, `.codex/config.toml`, and `agents/*.toml`.
- [x] 001-T003 [US2] Create repo-local role skills in `.agents/skills/*/SKILL.md`.

## Phase 2: Queue And Runtime Contracts

- [x] 001-T004 [US1] Seed canonical workflow state, canonical spec queue, policy, logs, summaries, and templates under `.ralph/`.
- [x] 001-T005 [US3] Write `tasks/prd-ralph-harness.md`.
- [x] 001-T006 [US3] Write `specs/001-self-bootstrap-harness/spec.md` and `specs/001-self-bootstrap-harness/plan.md`.
- [x] 001-T007 [US3] Write `specs/INDEX.md`, `specs/001-self-bootstrap-harness/tasks.md`, and `specs/001-self-bootstrap-harness/review.md`.

## Phase 3: Verification And Release

- [x] 001-T008 [US1] Capture queue-aware verification evidence in `specs/001-self-bootstrap-harness/verification.md` and `.ralph/reports/bootstrap-20260305/verify.md`.
- [x] 001-T009 [US3] Record the bootstrap handoff in `.ralph/reports/bootstrap-20260305/release.md` and advance both `.ralph/state/workflow-state.json` and `.ralph/state/spec-queue.json`.

## Review Notes

- The reference bootstrap deliberately stops short of a live GitHub PR, so PR metadata remains null in the example queue entry.
- Installed target projects should treat numbered specs and real PR state as required.
