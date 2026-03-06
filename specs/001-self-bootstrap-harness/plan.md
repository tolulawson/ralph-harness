# Implementation Plan: 001-self-bootstrap-harness

## Metadata

- Spec id: `001`
- Epoch id: `E001`
- Status: `done`
- Branch: `codex/001-self-bootstrap-harness`
- PR number: `null`

## Summary

Bootstrap the repository as the first numbered spec of the Codex-native Ralph harness. The implementation creates a thin Codex loader, a durable harness constitution, queue-aware runtime contracts, and a complete example trail that future runs can inspect and extend.

## Architecture

- Entry points: `AGENTS.md`, `.ralph/constitution.md`, `.codex/config.toml`, `agents/*.toml`
- Data flow: idea -> project PRD -> epochs -> numbered specs -> tasks -> implementation reports -> review -> verification -> release -> state update
- State changes: role completion appends one event, updates workflow state, updates spec queue state, and regenerates the Markdown projections

## Interfaces

- `AGENTS.md` points Codex to the constitution, project policy, workflow state, spec queue, and latest report.
- `.ralph/constitution.md` defines the shared orchestration and resume rules.
- `.codex/config.toml` maps role names to `agents/*.toml`.
- `.agents/skills/*/SKILL.md` define queue-aware role workflows.
- `.ralph/state/workflow-state.json` defines the canonical runtime state.
- `.ralph/state/spec-queue.json` defines the canonical spec queue.
- `.ralph/logs/events.jsonl` defines the append-only event schema.
- `.ralph/reports/<run-id>/<role>.md` defines the role handoff contract.

## Testing Strategy

- Parse `.codex/config.toml` and all `agents/*.toml` with `python3` and `tomllib`.
- Parse `.ralph/state/workflow-state.json`, `.ralph/state/spec-queue.json`, and every event in `.ralph/logs/events.jsonl` with `python3` and `json`.
- Confirm required scaffold files exist with `test -f` and `test -d`.
- Compare the semantic fields in `workflow-state.json`, `workflow-state.md`, and `specs/INDEX.md`.
- Confirm `.ralph/constitution.md` exists and the root `AGENTS.md` points to it and to the spec queue.

## Rollout Notes

- Treat this repo as a reference source template rather than the primary long-running harness.
- Keep example queue evidence inside versioned files.
- Add more domain skills later by extending role helper-skill policies, not by changing the control loop.
