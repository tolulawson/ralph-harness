# Changelog

This file is the canonical human-written release history for the Ralph harness.

GitHub releases should publish notes from the matching section in this file instead of relying on generated commit summaries.

## v0.8.4 - 2026-03-24

### Summary

Ralph no longer treats failed review, verification, or release results as terminal stop boundaries. Those states now stay inside the orchestrator remediation loop until the queue completes, lease ownership changes, or a genuinely human-gated blocker is reached.

This patch tightens the shipped runtime contract, orchestrator prompts, public execute entrypoint, and validation suite so the harness keeps resolving fixable issues instead of surfacing a premature stop notice.

### Highlights

- Removed `review failed`, `verification failed`, and `release failed` from the scaffold stop-condition list and reclassified them as remediation signals.
- Updated shipped orchestrator guidance and agent instructions so failed quality gates route back to the next fixing role unless an explicit human blocker is present.
- Tightened public `ralph-execute` guidance so stop summaries are reserved for queue completion, lease transfer, safety-cap review, or other human-gated boundaries.
- Added `scripts/verify-human-stop-boundaries.sh` and wired it into the main validation suite to prevent regressions.
- Synced the source repo's dogfood control-plane mirrors and runtime baseline hashes with the new stop-boundary contract.

### Install And Upgrade Impact

- Use tag `v0.8.4` as the default public install or upgrade reference.
- Fresh installs now inherit the corrected stop-boundary behavior by default.
- Existing installs can upgrade normally to pick up the remediation-loop fix; no schema bump or `upgrade_contract_version` change is required.

### Validation And Release Workflow

- Verified locally with `bash scripts/verify-human-stop-boundaries.sh`.
- Verified the full contract suite and smoke fixtures with `bash scripts/validate-harness.sh`.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Orchestrator skill: `src/.agents/skills/orchestrator/SKILL.md`
- Orchestrator agent config: `src/.codex/agents/orchestrator.toml`
- Public execute entrypoint: `skills/ralph-execute/SKILL.md`
- Runtime validation helper: `scripts/runtime_state_helpers.py`
- Release asset: `ralph-harness-v0.8.4.tar.gz`

## v0.8.3 - 2026-03-24

### Summary

Ralph now enforces a pre-review quality boundary for implementation handoffs, combining a conditional React Effects audit with an always-on lightweight deslopify pass.

This patch adds two shipped helper skills (`react-effects-without-effects` and `deslopify-lite`), requires explicit `Quality Gate` evidence in role reports, and blocks progression past implementation when that evidence is missing or failed.

### Highlights

- Added shipped helper skill `src/.agents/skills/react-effects-without-effects/` with a decision table for replacing unnecessary `useEffect` logic.
- Added shipped helper skill `src/.agents/skills/deslopify-lite/` for a focused anti-slop sweep (type strictness, SRP, fail-fast, DRY, dead code/workarounds).
- Updated implement role policy so React audits are mandatory when React scope changes, and deslopify-lite is mandatory for every implementation handoff.
- Added a required `Quality Gate` section to the shipped role report template with `React Effects Audit` and `Deslopify Lite` status fields.
- Hardened review, orchestrator, and execute preflight contracts so missing or failed quality-gate evidence is treated as a blocking finding.
- Expanded contract verification to assert new quality-gate wiring and helper-skill presence.

### Install And Upgrade Impact

- Use tag `v0.8.3` as the default public install or upgrade reference.
- Fresh installs now include both new helper skills and the `Quality Gate` report contract.
- Existing installs can upgrade normally to pick up the new boundary enforcement and report schema expectations.

### Validation And Release Workflow

- Verified locally with `bash scripts/verify-atomic-commit-contract.sh`.
- Verified full contract suite and smoke fixtures with `bash scripts/validate-harness.sh`.

### Artifacts And References

- Implement role guidance: `src/.agents/skills/implement/SKILL.md`
- Review role guidance: `src/.agents/skills/review/SKILL.md`
- Orchestrator guidance: `src/.agents/skills/orchestrator/SKILL.md`
- Report template: `src/.ralph/templates/role-report-template.md`
- Execute preflight: `skills/ralph-execute/SKILL.md`
- Release asset: `ralph-harness-v0.8.3.tar.gz`

## v0.8.2 - 2026-03-21

### Summary

Ralph now has a preserved project-owned runtime override surface and an upgrade preflight that blocks direct edits to the scaffold-owned base runtime contract before those edits can be lost.

This patch keeps `.ralph/runtime-contract.md` upgrade-managed while introducing `.ralph/policy/runtime-overrides.md` as the supported place for project-specific runtime additions. It also hardens upgrade safety by recording the installed base-contract fingerprint and requiring preflight review when the base contract has drifted.

### Highlights

- Added the preserved runtime override surface at `.ralph/policy/runtime-overrides.md` to the shipped scaffold and dogfood runtime.
- Updated loaders, constitutions, runtime doctrine, project policy, public skills, and shipped orchestrator guidance so runtime overrides are part of the default read order.
- Added `scripts/check-upgrade-surface.py` plus baseline-hash tracking in `.ralph/harness-version.json` to block upgrades when `.ralph/runtime-contract.md` was edited directly.
- Taught migration to create the runtime-overrides file when missing and bumped `upgrade_contract_version` to `7`.
- Expanded smoke coverage to prove runtime overrides survive upgrade and direct base-contract drift is caught before manifest overwrite.

### Install And Upgrade Impact

- Use tag `v0.8.2` as the default public install or upgrade reference.
- Fresh installs now include `.ralph/policy/runtime-overrides.md` and record the scaffold runtime-contract baseline hash in `.ralph/harness-version.json`.
- Upgrades must run the new `scripts/check-upgrade-surface.py` preflight before refreshing scaffold-owned files.
- Existing installs that placed project-specific runtime changes directly in `.ralph/runtime-contract.md` must move those additions into `.ralph/policy/runtime-overrides.md` before upgrading.

### Validation And Release Workflow

- Local and CI validation now include `python3 scripts/check-upgrade-surface.py --repo .` alongside the existing contract suite.
- Smoke tests now cover both runtime-override preservation and blocked upgrade preflight for direct base runtime-contract edits.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Runtime overrides surface: `src/.ralph/policy/runtime-overrides.md`
- Upgrade guide: `UPGRADING.md`
- Upgrade preflight: `scripts/check-upgrade-surface.py`
- Runtime migration helper: `scripts/runtime_state_helpers.py`
- Release asset: `ralph-harness-v0.8.2.tar.gz`

## v0.8.1 - 2026-03-21

### Summary

Aligned Ralph's installable documentation, shipped role skills, and public entry skills with the `v0.8.0` multi-spec runtime so operators get the right guidance for lease-safe coordination, dependency-aware scheduling, spec-scoped worker reports, and interrupt handling.

This patch does not introduce another schema change. It tightens the human-facing contract around the already-shipped multi-spec control plane and makes the public skills match the actual runtime and upgrade behavior more closely.

### Highlights

- Updated `README.md` to describe the dependency-aware multi-spec scheduler, durable intent intake, single-writer lease, per-spec worktree execution, spec-scoped worker reports, and upgrade-safety rules.
- Aligned shipped role skills under `src/.agents/skills/` so `specify`, `plan`, `research`, `task-gen`, and `plan-check` all point at the current spec-scoped worker report convention.
- Tightened public `ralph-plan`, `ralph-interrupt`, and `ralph-execute` guidance so dependency validation, interrupt creation, lease ownership, durable intent flow, and compatibility mirrors reflect the current runtime contract.
- Synced the dogfood runtime copies of the updated policy, runtime contract, and role skills with the shipped source surface for clearer source-repo verification.

### Install And Upgrade Impact

- Use tag `v0.8.1` as the default public install or upgrade reference.
- Fresh installs inherit the corrected documentation and shipped skill wording immediately.
- Existing installs can upgrade normally to pick up the clarified skill and documentation surface; no new migration phase, schema bump, or `upgrade_contract_version` change is required beyond the existing `v0.8.0` upgrade flow.

### Validation And Release Workflow

- Local and CI validation continue to use the existing contract suite from `v0.8.0`.
- Verified this release with `bash scripts/verify-installation-contract.sh`, `bash scripts/verify-upgrade-contract.sh`, and `bash scripts/validate-harness.sh`.

### Artifacts And References

- README: `README.md`
- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Project policy: `src/.ralph/policy/project-policy.md`
- Public execute entrypoint: `skills/ralph-execute/SKILL.md`
- Public interrupt entrypoint: `skills/ralph-interrupt/SKILL.md`
- Release asset: `ralph-harness-v0.8.1.tar.gz`

## v0.8.0 - 2026-03-21

### Summary

Ralph now supports dependency-aware multi-spec execution with bounded concurrency, per-spec worktree isolation, and a lease-safe control plane that can accept new work while other specs are already in flight.

This release refactors the shipped scheduler around `active_spec_ids`, durable operator intents, and spec-scoped worktrees, then hardens the upgrade path so existing installs can migrate into the new runtime safely without trampling live orchestration, legacy report layouts, or ambiguous queue ownership.

### Highlights

- Added dependency-aware multi-spec scheduler state, bounded normal-spec admission windows, and per-spec worktree metadata across the shipped runtime contract, templates, queue state, and orchestration guidance.
- Added durable lease and intent coordination files plus the `scripts/orchestrator-coordination.py` helper for lease, intent, and worktree operations.
- Updated migration and validation to normalize legacy installs into the multi-spec schema, recover stale held leases, enforce unique branch and worktree ownership, and fail fast on ambiguous upgrade states.
- Normalized legacy worker report pointers into spec-scoped `.ralph/reports/<run-id>/<spec-key>/<role>.md` paths when report ownership is clear.
- Added contract coverage for multi-spec scheduling plus expanded smoke fixtures for healthy-lease blocking, stale-lease recovery, collision-safe worktree reassignment, and legacy report-path normalization.

### Install And Upgrade Impact

- Use tag `v0.8.0` as the default public install or upgrade reference.
- Fresh installs inherit the dependency-aware multi-spec scheduler, durable intent intake, per-spec worktree layout, and spec-scoped worker report convention immediately.
- Upgrades still use the manifest-copy plus migration flow, but migration now stops over healthy live leases, recovers stale coordination state, normalizes safely-derivable legacy worktree and report layouts, and keeps `upgrade_contract_version` at `6`.

### Validation And Release Workflow

- CI and local validation now run the multi-spec contract verifier alongside the existing installation, interruption, atomic-commit, parallel-research, subagent-isolation, and upgrade verifiers.
- Smoke tests now cover live-lease upgrade blocking, stale-lease recovery, safe worktree collision normalization, ambiguous shared legacy reports, and duplicate branch ownership failure.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Project policy: `src/.ralph/policy/project-policy.md`
- Runtime migration helper: `scripts/runtime_state_helpers.py`
- Coordination helper: `scripts/orchestrator-coordination.py`
- Release asset: `ralph-harness-v0.8.0.tar.gz`

## v0.7.0 - 2026-03-17

### Summary

Ralph now isolates spawned worker context explicitly while standardizing the shipped control plane around full-permission role execution.

This release adds a formal subagent-isolation contract to the shipped runtime doctrine, teaches install and upgrade flows to enforce forked worker delegation plus bounded depth, and moves every managed role config to `sandbox_mode = "danger-full-access"` so orchestrated work is no longer split across mixed privilege levels.

### Highlights

- Added explicit forked worker-context rules and role-to-agent mapping guidance to the shipped runtime contract and orchestrator instructions.
- Switched all managed role configs under `src/.codex/agents/` to `sandbox_mode = "danger-full-access"`.
- Reduced the managed delegation depth cap to `2` and taught migration to clamp installed configs to that cap.
- Added `scripts/verify-subagent-isolation-contract.sh` and wired it into the full validation suite.
- Expanded install and upgrade docs so the public contract documents full-permission roles, forked delegation, and the strengthened migration checks.

### Install And Upgrade Impact

- Use tag `v0.7.0` as the default public install or upgrade reference.
- Fresh installs inherit the new subagent-isolation contract, full-permission role configs, and bounded depth cap immediately.
- Upgrades continue to merge installed `.codex/config.toml`, but now also normalize managed role sandbox modes and preserve the new depth cap.
- `upgrade_contract_version` remains `5`; existing installs should rerun the normal upgrade flow to pick up the full-permission role configs and isolation checks.

### Validation And Release Workflow

- CI and local validation now run `scripts/verify-subagent-isolation-contract.sh` alongside the existing contract verifiers.
- Smoke tests now assert that migrated installs end up with `danger-full-access` for every managed role while still preserving user-owned `.codex/config.toml` entries that Ralph does not manage.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Orchestrator skill: `src/.agents/skills/orchestrator/SKILL.md`
- Runtime migration helper: `scripts/runtime_state_helpers.py`
- Release asset: `ralph-harness-v0.7.0.tar.gz`

## v0.6.1 - 2026-03-09

### Summary

Upgrades now preserve user-owned `.codex/config.toml` settings instead of overwriting the whole file, while still applying Ralph’s required feature flags and managed role mappings.

This patch removes `.codex/config.toml` from the blind overwrite surface, teaches the migration phase to merge the installed config with the scaffold config, and adds smoke coverage for preserved user settings such as `sandbox_mode = "danger-full-access"`.

### Highlights

- Removed `.codex/config.toml` from the upgrade overwrite manifest.
- Added merge-aware `.codex/config.toml` migration that preserves user-owned settings and custom agent entries.
- Kept Ralph-managed `features.multi_agent` and managed role `config_file` mappings current during upgrade.
- Added smoke coverage proving upgrades preserve custom `sandbox_mode` and thread settings while adding new Ralph roles.

### Install And Upgrade Impact

- Use tag `v0.6.1` as the default public install or upgrade reference.
- Fresh installs still copy the scaffold `.codex/config.toml` directly.
- Upgrades now merge `.codex/config.toml` during migration instead of overwriting it from `src/upgrade-manifest.txt`.

### Validation And Release Workflow

- Upgrade contract validation now requires documentation of the config-merge behavior.
- Smoke tests now include a user-customized config fixture that verifies preserved settings plus refreshed Ralph mappings.

### Artifacts And References

- Upgrade contract: `src/upgrade-manifest.txt`
- Runtime migration helper: `scripts/runtime_state_helpers.py`
- Upgrade guide: `UPGRADING.md`
- Release asset: `ralph-harness-v0.6.1.tar.gz`

## v0.6.0 - 2026-03-09

### Summary

Ralph now supports one narrow form of planning-time parallelism: spec-local `research` can run concurrently for specs created or refreshed in the same planning batch, while planning, task generation, implementation, review, verification, and release remain strictly sequential.

This release also adds a dedicated `plan-check` gate, research-aware planning artifacts, and queue or task-state schema updates so upgrades and fresh installs preserve the sequential execution loop while improving pre-implementation rigor.

### Highlights

- Added shipped `research` and `plan-check` agent configs plus matching runtime skills.
- Inserted a bounded parallel `research` phase between specification and planning in the shipped runtime doctrine.
- Added research metadata to the canonical spec queue and requirement or verification metadata to `task-state.json`.
- Strengthened shipped `spec`, `plan`, `review`, `verify`, and `analyze` guidance so planning consumes `research.md` and verification checks truths, artifacts, and critical links.
- Added validation coverage for the research-only parallelism contract and smoke coverage for planning-batch research readiness.

### Install And Upgrade Impact

- Use tag `v0.6.0` as the default public install or upgrade reference.
- Fresh installs inherit the new `research` and `plan-check` phases, queue metadata, and research-aware templates immediately.
- Upgrades must run the normal manifest-copy plus migration flow so queue entries and task-state files are normalized to the new schema and upgrade contract version `4`.

### Validation And Release Workflow

- CI and local validation now run `scripts/verify-parallel-research-contract.sh` alongside the existing installation, interruption, atomic-commit, and upgrade contract checks.
- Smoke coverage now includes a planning-batch fixture that proves research metadata can exist for multiple specs without relaxing FIFO execution.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Research template: `src/.ralph/templates/research-template.md`
- Task-state template: `src/.ralph/templates/task-state-template.json`
- Release asset: `ralph-harness-v0.6.0.tar.gz`

## v0.5.1 - 2026-03-09

### Summary

Cleaned up the shipped task-generation guidance so it no longer implies unsupported wave-style parallel execution.

This patch release removes stale `[P]`-style parallel-task guidance from the scaffold and aligns task authoring instructions with the current Ralph runtime contract: one active worker at a time, with independence expressed through dependency ordering and phase structure instead of parallel markers.

### Highlights

- Removed stale parallel-marker guidance from the shipped `task-gen` skill.
- Clarified that task independence should be encoded through ordering and phase structure, not wave execution hints.
- Kept the existing atomic-commit handoff contract and single-worker orchestration model unchanged.

### Install And Upgrade Impact

- Use tag `v0.5.1` as the default public install or upgrade reference.
- Fresh installs inherit the cleaned-up task-generation guidance immediately.
- Existing installed repos can upgrade normally; no new migration step, schema change, or runtime-state repair is required for this release.

### Validation And Release Workflow

- The release continues to use the existing validation suite and release workflow from `v0.5.0`.
- No new validators or workflow phases were added for this patch release.

### Artifacts And References

- Task generation skill: `src/.agents/skills/task-gen/SKILL.md`
- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Release asset: `ralph-harness-v0.5.1.tar.gz`

## v0.5.0 - 2026-03-09

### Summary

Completed tasks now require atomic commit checkpoints before handoff, and Ralph enforces that traceability at runtime preflight instead of treating it as a loose convention.

This release adds checkpoint-level `Commit Evidence` to the shipped report contract, tightens the shipped implement, review, verify, release, and orchestrator instructions around clean-worktree handoff, and expands runtime validation so review, verification, and release refuse to advance from a dirty branch or a report that lacks checkpoint traceability.

### Highlights

- Added a required `Commit Evidence` section to the shipped role report template and doctrine.
- Tightened the shipped role skills and Codex agent role configs so implementation must create atomic task checkpoints and review treats missing commit evidence as a finding.
- Extended installed-runtime preflight to validate active branch alignment, clean worktree handoff, and checkpoint commit evidence from the latest relevant worker report.
- Added a dedicated atomic-commit contract verifier plus git-backed smoke fixtures for passing and failing handoff scenarios.

### Install And Upgrade Impact

- Use tag `v0.5.0` as the default public install or upgrade reference.
- Fresh installs inherit the atomic-commit handoff rule through the shipped scaffold doctrine, role skills, and report template.
- Upgrades continue to use the same manifest-copy and migration flow as `v0.4.0`; no new scaffold paths or migration phases were added for this release.
- Existing installed repos that upgrade to `v0.5.0` should expect stricter `ralph-execute` preflight when a completed task lacks checkpoint traceability or the branch is dirty at handoff.

### Validation And Release Workflow

- CI and local validation now run `scripts/verify-atomic-commit-contract.sh` alongside the existing install, interrupt, and upgrade contract checks.
- Smoke tests now include git-backed fixtures that prove atomic checkpoint handoff passes and dirty-worktree, missing-evidence, and branch-mismatch cases fail.
- The GitHub release workflow now makes the new verifier executable before running the full validation suite.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Project policy: `src/.ralph/policy/project-policy.md`
- Report template: `src/.ralph/templates/role-report-template.md`
- Public resume entrypoint: `skills/ralph-execute/SKILL.md`
- Release asset: `ralph-harness-v0.5.0.tar.gz`

## v0.4.0 - 2026-03-08

### Summary

Role config TOMLs now live under `.codex/agents/`, matching how Codex resolves `config_file` entries from `.codex/config.toml`.

This release removes the old repo-root `agents/` control-plane layout from the scaffold contract, adds migration and validation for the new canonical `.codex/agents/` location, and repairs the harness so fresh installs, upgrades, and dogfood runtimes all resolve agent configs correctly.

### Highlights

- Moved shipped and dogfood role config TOMLs under `.codex/agents/` while keeping `.codex/config.toml` as the entrypoint.
- Added migration and preflight checks for legacy repo-root `agents/*.toml` installs.
- Tightened validation so harness checks now resolve every `config_file` target and fail when the referenced TOMLs do not exist.
- Updated install, upgrade, and repository-layout docs to treat `.codex/agents/*.toml` as canonical.

### Install And Upgrade Impact

- Use tag `v0.4.0` as the default public install or upgrade reference.
- Fresh installs now copy `.codex/config.toml` and `.codex/agents/` instead of repo-root `agents/`.
- Upgrades move legacy repo-root `agents/*.toml` into `.codex/agents/` when safe and remove the old directory only after canonical targets exist.
- `upgrade_contract_version` is now `3` for installs that use the canonical `.codex/agents/` layout.

### Validation And Release Workflow

- CI and local validation now resolve `config_file` targets from both the root dogfood config and the shipped scaffold config.
- Smoke tests now prove fresh installs avoid repo-root `agents/`, legacy installs migrate into `.codex/agents/`, and unsafe legacy leftovers fail loudly.

### Artifacts And References

- Install guide: `INSTALLATION.md`
- Upgrade guide: `UPGRADING.md`
- Runtime migration: `scripts/migrate-installed-runtime.py`
- Runtime preflight: `scripts/check-installed-runtime-state.py`
- Release asset: `ralph-harness-v0.4.0.tar.gz`

## v0.3.0 - 2026-03-08

### Summary

Upgrades are now migration-aware, and interrupt-capable execution refuses to continue from mixed-version runtime state.

This release adds a live-state migration path for already-installed repos, current-state preflights for `ralph-execute` and `ralph-interrupt`, and stronger validation that catches drift between canonical JSON state and human-readable projections before the harness can hand off bad state.

### Highlights

- Added `scripts/migrate-installed-runtime.py` to normalize installed workflow state, queue state, projections, and missing `task-state.json` files.
- Added `scripts/check-installed-runtime-state.py` so upgrades, resume entry points, and tests can fail fast on mixed-version or semantically drifted runtime state.
- Tightened `ralph-upgrade`, `ralph-execute`, `ralph-interrupt`, and installed `state-sync` instructions around state-truth hierarchy and synchronized updates.
- Refreshed the shipped seed workflow projection so the scaffold no longer ships a stale `workflow-state.md`.
- Added repair-runbook guidance for the exact mismatch class where `workflow-state.json` points at a task already checked off in `tasks.md`.

### Install And Upgrade Impact

- Use tag `v0.3.0` as the default public install or upgrade reference.
- Upgrades still copy only the scaffold-owned manifest surface, but they must now run the live-state migration phase before the runtime is considered current.
- `upgrade_contract_version` is now `2` for migration-aware installs.
- Existing repos that only performed the older manifest-only `v0.2.0` upgrade need to rerun upgrade with migration before using interrupt creation or strict resume preflights.

### Validation And Release Workflow

- CI now validates migration-aware upgrade docs, installed-runtime preflight checks, and fixture migration behavior.
- Smoke tests now cover positive migration from older state shapes plus fail-fast behavior for ambiguous task-history drift.
- Live end-to-end Codex runtime execution remains the final proof beyond fixture validation.

### Artifacts And References

- Upgrade guide: `UPGRADING.md`
- Runtime migration: `scripts/migrate-installed-runtime.py`
- Runtime preflight: `scripts/check-installed-runtime-state.py`
- Interrupt entry point: `skills/ralph-interrupt/SKILL.md`
- Release asset: `ralph-harness-v0.3.0.tar.gz`

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
