# Implementation Plan: 002-deterministic-orchestration-versioning-and-upgrades

## Metadata

- Spec id: `002`
- Epoch id: `E002`
- Status: `done`
- Branch: `codex/002-deterministic-orchestration-versioning-and-upgrades`
- PR number: `null`

## Summary

Refactor the Ralph harness into a deterministic Codex multi-agent queue runner, add a canonical task lifecycle file, split the runtime doctrine for upgrade safety, and publish a semver-based release and upgrade contract around the shipped scaffold.

## Architecture

- Entry points: `AGENTS.md`, `.ralph/constitution.md`, `.ralph/runtime-contract.md`, `.codex/config.toml`, `agents/*.toml`, `skills/ralph-*`
- Data flow: versioned scaffold tag -> install or upgrade contract -> target runtime doctrine -> orchestrator spawn/wait loop -> worker reports -> orchestrator-owned shared-state transitions
- State changes: task generation seeds `task-state.json`; orchestrator applies lifecycle transitions after validating worker reports; release and upgrade metadata live in `VERSION`, `.ralph/harness-version.json`, and tagged GitHub releases

## Interfaces

- `VERSION` is the canonical scaffold semver source.
- `src/.ralph/runtime-contract.md` defines the installed runtime doctrine.
- `src/.ralph/harness-version.json` seeds installed-version metadata.
- `src/upgrade-manifest.txt` defines the safe overwrite surface for already-installed repos.
- `skills/ralph-upgrade/SKILL.md` is the public upgrade entry point.
- `.github/workflows/ci.yml` and `.github/workflows/release.yml` validate and publish tagged releases.
- `specs/<spec-key>/task-state.json` is the canonical machine-readable task lifecycle registry.

## Testing Strategy

- Parse root and shipped TOML, JSON, and JSONL files.
- Verify the install contract and upgrade contract stay aligned with docs, manifests, managed AGENTS markers, version metadata, and public skills.
- Run a fixture install and fixture upgrade smoke test from `src/`.
- Confirm the shipped config enables Codex multi-agent and the current tag appears in install and upgrade docs.
- Dogfood the root runtime by recording spec `002`, adding `task-state.json`, and updating the source repo state trail.

## Rollout Notes

- Keep the first versioned release manual and intentional.
- Treat target-repo retrofits as separate work outside this spec.
- Use the root dogfood runtime plus temp fixture repos as proof before cutting the first tag.
