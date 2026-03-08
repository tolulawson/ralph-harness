# Changelog

This file is the canonical human-written release history for the Ralph harness.

GitHub releases should publish notes from the matching section in this file instead of relying on generated commit summaries.

## v0.2.0 - 2026-03-07

### Summary

Interrupt specs are now a first-class part of the shipped Ralph harness.

This release adds a canonical queue-preemption workflow for failing out-of-scope bugs, a public `ralph-interrupt` entry point, append-only amendment tracking for earlier specs, and a stricter source-repo rule that keeps harness implementation changes in `src/` so dogfooding can happen later through install or upgrade.

### Highlights

- Added canonical interrupt-spec metadata and queue ordering to the shipped runtime contract, orchestrator config, worker report template, and scaffold state seeds.
- Added `resume_spec_stack`, `paused` task semantics, and LIFO resume behavior so interrupted work can pause and continue cleanly.
- Added append-only `amendments.md` support for recording corrective guidance against older specs without rewriting historical spec artifacts.
- Added the public `ralph-interrupt` source skill for operator-triggered bugfix interrupts in installed repos.
- Added interruption-contract validation so CI checks the new interrupt workflow and source-only implementation rule.

### Install And Upgrade Impact

- Use tag `v0.2.0` as the default public install or upgrade reference.
- Fresh installs from `src/` now include the interrupt-spec workflow in the shipped runtime doctrine and templates.
- Existing installs should upgrade through `UPGRADING.md` or `ralph-upgrade` so interrupt support lands through the managed scaffold surface instead of by copying root dogfood files.
- The source repo now treats `src/` as the only implementation surface for harness changes; root dogfood runtime copies are for later validation and upgrade testing.

### Validation And Release Workflow

- CI now validates the interruption contract in addition to the existing install, upgrade, and fixture smoke checks.
- The interruption validator checks the shipped scaffold, the public `ralph-interrupt` entry point, and the source-only development rule in the source-repo loader and constitution.
- Releases remain intentional and manual through the GitHub Actions release workflow after validation passes.
- Live end-to-end Codex runtime execution remains the final proof beyond fixture validation.

### Artifacts And References

- Install guide: `INSTALLATION.md`
- Upgrade guide: `UPGRADING.md`
- Interrupt entry point: `skills/ralph-interrupt/SKILL.md`
- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Release asset: `ralph-harness-v0.2.0.tar.gz`

## v0.1.0 - 2026-03-07

### Summary

Initial public release of the Codex-native Ralph harness scaffold.

This release turns the source repo into a versioned install and upgrade surface for downstream projects. It ships a deterministic orchestration contract for Codex multi-agent execution, separates installed scaffold content from source-repo dogfood history, and publishes the first semver-tagged release path for installs and upgrades.

### Highlights

- Added a versioned scaffold contract rooted in `VERSION`, tagged GitHub releases, and `.ralph/harness-version.json`.
- Enabled official Codex multi-agent support in the shipped control plane and documented the queue-draining orchestrator contract.
- Split installed runtime doctrine into project-specific `.ralph/constitution.md` plus generic `.ralph/runtime-contract.md`.
- Added canonical per-spec `task-state.json` support for task lifecycle ownership under the orchestrator.
- Added public `ralph-install`, `ralph-upgrade`, `ralph-prd`, `ralph-plan`, and `ralph-execute` source skills.

### Install And Upgrade Impact

- Use tag `v0.1.0` as the default public install or upgrade reference.
- Install only from `src/`, never from the repository root.
- Follow `INSTALLATION.md` for fresh installs and `UPGRADING.md` for existing installs.
- Upgrades now preserve project-owned runtime files by default and refresh only the scaffold-owned surface from `src/upgrade-manifest.txt`.
- Installed repos should record both the human-facing tag and the resolved commit in `.ralph/harness-version.json`.

### Validation And Release Workflow

- CI validates TOML, JSON, and JSONL parsing across the shipped scaffold and root dogfood runtime.
- CI checks install-contract and upgrade-contract alignment, version metadata, and fixture install or upgrade behavior.
- Releases are intentional and manual through the GitHub Actions release workflow after validation passes.
- The orchestrator contract now requires official Codex multi-agent behavior, but live end-to-end Codex runtime execution remains the final runtime proof beyond fixture validation.

### Artifacts And References

- Install guide: `INSTALLATION.md`
- Upgrade guide: `UPGRADING.md`
- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Install contract: `src/install-manifest.txt`
- Upgrade contract: `src/upgrade-manifest.txt`
- Release asset: `ralph-harness-v0.1.0.tar.gz`
