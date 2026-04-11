# Changelog

This file is the canonical human-written release history for the Ralph harness.

GitHub releases should publish notes from the matching section in this file instead of relying on generated commit summaries.

## v0.13.0 - 2026-04-10

### Summary

This release redesigns Ralph's control plane around peer orchestrators instead of a resident single-writer scheduler.

It replaces the long-lived orchestrator lease with a short-lived shared scheduler lock, durable scheduler intents, and spec-scoped execution claims so multiple threads can cooperate against the same canonical control plane without one thread owning the queue for the duration of the run.

### Highlights

- Replaced the old `orchestrator-lease` / `orchestrator-intents` / `worker-claims` naming and semantics with:
  - `.ralph/state/scheduler-lock.json`
  - `.ralph/state/scheduler-intents.jsonl`
  - `.ralph/state/execution-claims.json`
- Updated the shipped runtime contract, project policy, adapters, and role skills to teach the peer-scheduler model:
  - queue mutation is guarded by a short-lived shared scheduler lock
  - many orchestrator peers may participate in one control plane
  - actual execution ownership is carried by spec-scoped claims
  - shared-state reads from worktrees resolve through `.ralph/shared/` or the canonical checkout
- Bumped queue and workflow schema to `7.0.0`, added `queue_revision`, and refreshed migration logic so legacy installs converge on canonical v7 file names and path fields during upgrade and preflight repair.
- Tightened the stop-boundary hook so it reads canonical shared control-plane state from spec worktrees and never auto-continues across an explicit human-gated boundary.
- Added regression and verifier coverage for multi-orchestrator doctrine drift, shared-state stop-hook reads, human-gated stop behavior, and legacy coordination-file migration during preflight.

### Install And Upgrade Impact

- Use tag `v0.13.0` as the default public install or upgrade reference.
- Fresh installs now ship the peer-orchestrator control plane and the renamed scheduler-lock / scheduler-intents / execution-claims runtime state.
- Existing installs must upgrade into the v7 queue/workflow naming and coordination model; `upgrade_contract_version` remains `11` because this release extends the existing migration contract rather than introducing a new upgrade phase.

### Validation And Release Workflow

- Verified focused regressions with:
  - `python3 scripts/test-stop-boundary-hook.py`
  - `python3 scripts/test-control-plane-lifecycle.py`
  - `python3 scripts/test-runtime-preflight-repairs.py`
  - `bash scripts/verify-upgrade-contract.sh`
- Verified full release surface with `scripts/validate-harness.sh`.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Project policy: `src/.ralph/policy/project-policy.md`
- Stop hook: `src/.ralph/hooks/stop-boundary.py`
- Coordination helper: `scripts/orchestrator-coordination.py`
- Runtime helper layer: `scripts/runtime_state_helpers.py`
- Runtime adapters: `src/.codex/agents/orchestrator.toml`, `src/.claude/agents/orchestrator.md`, `src/.cursor/rules/ralph-core.mdc`
- Release asset: `ralph-harness-v0.13.0.tar.gz`

## v0.12.8 - 2026-04-08

### Summary

This release tightens upgrade and install language so project-specific contract or control-plane instructions are explicitly kept out of canonical scaffold-owned files.

### Highlights

- Added an explicit canonical-file guardrail to the upgrade guide that forbids writing project-specific rules into `.ralph/runtime-contract.md` or Ralph-managed runtime skill directories.
- Tightened install and upgrade skills so they route custom runtime and control-plane instructions into extension surfaces:
  - `.ralph/policy/runtime-overrides.md`
  - `.ralph/policy/project-policy.md`
  - `.ralph/context/project-facts.json` (`canonical_control_plane`, `control_plane_versioning`)
- Updated preflight error messaging to point operators at the full set of extension surfaces instead of implying only one destination.
- Extended contract verifiers so these guardrails are enforced by release checks.

### Install And Upgrade Impact

- Use tag `v0.12.8` as the default public install or upgrade reference.
- Fresh installs now explicitly emphasize extension-only customization for runtime contract and control-plane rules.
- Existing installs can upgrade normally to pick up stronger guardrail language and clearer remediation guidance; `upgrade_contract_version` remains `11`.

### Validation And Release Workflow

- Verified focused contract and regression checks with:
  - `bash scripts/verify-installation-contract.sh`
  - `bash scripts/verify-upgrade-contract.sh`
  - `bash scripts/verify-canonical-control-plane-contract.sh`
  - `python3 scripts/test-runtime-preflight-repairs.py`
- Verified full release surface with `bash scripts/validate-harness.sh`.

### Artifacts And References

- Install guide: `INSTALLATION.md`
- Upgrade guide: `UPGRADING.md`
- Install helper: `skills/ralph-install/SKILL.md`
- Upgrade helper: `skills/ralph-upgrade/SKILL.md`
- Runtime helpers: `scripts/runtime_state_helpers.py`
- Contract checks: `scripts/verify-installation-contract.sh`, `scripts/verify-upgrade-contract.sh`
- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Runtime extension policy: `src/.ralph/policy/runtime-overrides.md`
- Release asset: `ralph-harness-v0.12.8.tar.gz`

## v0.12.7 - 2026-04-08

### Summary

This release makes canonical control-plane setup explicit and user-driven during install, while fixing upgrade/runtime validation so custom canonical worktree checkouts are honored instead of being collapsed back to the git common checkout.

### Highlights

- Added canonical control-plane metadata to project facts (`canonical_control_plane` and `control_plane_versioning`) and validation rules for these fields.
- Updated canonical checkout resolution so runtime tooling prefers the active Ralph runtime root and honors explicit custom canonical checkout paths.
- Added regression coverage for custom canonical worktree invocation, explicit configured canonical checkout paths, and spec-worktree-to-canonical resolution behavior.
- Updated install guidance and `ralph-install` workflow to require using the runtime question/input tool for:
  - canonical control-plane selection (current checkout vs custom path or branch)
  - control-plane artifact versioning policy (track vs gitignore vs custom)
- Updated install and upgrade contract verifiers so these interactive setup requirements remain enforced across future releases.

### Install And Upgrade Impact

- Use tag `v0.12.7` as the default public install or upgrade reference.
- Fresh installs now explicitly capture canonical control-plane and control-plane artifact versioning policy at setup time.
- Existing installs can upgrade normally to pick up canonical-root resolution fixes and stronger install contract enforcement; `upgrade_contract_version` remains `11`.

### Validation And Release Workflow

- Verified runtime preflight regressions with `python3 scripts/test-runtime-preflight-repairs.py`.
- Verified release contract surfaces with:
  - `bash scripts/verify-installation-contract.sh`
  - `bash scripts/verify-upgrade-contract.sh`
  - `bash scripts/verify-canonical-control-plane-contract.sh`
- Verified full release surface with `bash scripts/validate-harness.sh`.

### Artifacts And References

- Runtime helpers: `scripts/runtime_state_helpers.py`
- Runtime preflight regressions: `scripts/test-runtime-preflight-repairs.py`
- Install contract checks: `scripts/verify-installation-contract.sh`
- Upgrade contract checks: `scripts/verify-upgrade-contract.sh`
- Install guide: `INSTALLATION.md`
- Upgrade guide: `UPGRADING.md`
- Install helper: `skills/ralph-install/SKILL.md`
- Release asset: `ralph-harness-v0.12.7.tar.gz`

## v0.12.6 - 2026-04-08

### Summary

This release removes the source repository's repo-root Ralph dogfood runtime and makes the repository operate as a source-only workspace.

It keeps `src/` as the shipped scaffold, keeps `skills/` as the public source-entry surface, and eliminates the confusing split where the same repository was both the product source and a live installed runtime.

### Highlights

- Removed the repo-root installed-runtime surfaces, including the dogfood adapter packs, role-skill packs, runtime control plane, reports, logs, worktrees, and example planning history.
- Replaced the root `AGENTS.md` and `CLAUDE.md` with source-repo contributor loaders that point work at `src/`, install/upgrade docs, and the shipped scaffold doctrine.
- Updated the README, installation guide, and public `ralph-*` source skills so they describe the source repo as a packaging and validation workspace rather than a live Ralph-managed project.
- Retargeted release validation so the source repo is checked through `src/` plus fixture installs instead of expecting a repo-root installed runtime to exist.
- Repaired the install/upgrade smoke coverage so legacy fixture seeding pulls adapter configs from `src/.codex/agents/`.

### Install And Upgrade Impact

- Use tag `v0.12.6` as the default public install or upgrade reference.
- Fresh installs and upgrades keep the same shipped runtime scaffold model under `src/`; the main change is that the source repository itself no longer carries repo-root runtime history.
- Existing installed target repositories are still upgraded through the normal manifest and migration flow; `upgrade_contract_version` remains `11`.

### Validation And Release Workflow

- Verified the full release surface, including contract checks and fixture install/upgrade smoke coverage, with `scripts/validate-harness.sh`.

### Artifacts And References

- Source-repo loaders: `AGENTS.md`, `CLAUDE.md`
- Source-repo guides: `README.md`, `INSTALLATION.md`
- Public source skills: `skills/ralph-execute/SKILL.md`, `skills/ralph-interrupt/SKILL.md`, `skills/ralph-plan/SKILL.md`, `skills/ralph-prd/SKILL.md`
- Validation tooling: `scripts/validate-harness.sh`, `scripts/smoke-test-install-upgrade.sh`
- Release asset: `ralph-harness-v0.12.6.tar.gz`

## v0.12.5 - 2026-04-02

### Summary

This release repairs Ralph's upgrade guidance around managed runtime skill drift.

It closes the gap where upgrades correctly blocked direct edits inside Ralph-managed `.agents/skills/` directories but did not clearly explain where project-specific control-plane changes should live or how to repair the drift cleanly before retrying.

### Highlights

- Clarified the shipped runtime doctrine so Ralph-managed runtime skill directories are explicitly scaffold-owned, while project-specific control-plane behavior belongs in `.ralph/policy/runtime-overrides.md`, `.ralph/policy/project-policy.md`, or a project-owned non-managed skill directory.
- Updated the upgrade guide with a dedicated managed-skill drift rule, including a concrete repair path for moving local control-plane customizations out of Ralph-managed skill directories before restoring the recorded baseline.
- Tightened upgrade helper guidance so `ralph-upgrade` now routes managed-skill drift into preserved policy files or non-managed local skills instead of leaving the operator at a generic drift failure.
- Made upgrade preflight errors more actionable by explaining that unknown skill directories are preserved, but edits inside Ralph-managed ones are not.
- Added contract and smoke coverage so future releases must keep the managed-vs-project-owned skill boundary explicit and must mention the correct repair surfaces in preflight output.

### Install And Upgrade Impact

- Use tag `v0.12.5` as the default public install or upgrade reference.
- Fresh installs inherit the clarified doctrine about Ralph-managed skill ownership.
- Existing installs can upgrade normally to pick up the improved guidance and more actionable managed-skill drift errors; `upgrade_contract_version` remains `11`.

### Validation And Release Workflow

- Verified the focused upgrade checks with `bash scripts/verify-upgrade-contract.sh` and `python3 scripts/check-upgrade-surface.py --repo .`.
- Verified the full release surface, including install and upgrade smoke coverage, with `bash scripts/validate-harness.sh`.

### Artifacts And References

- Upgrade guide: `UPGRADING.md`
- Upgrade helper: `skills/ralph-upgrade/SKILL.md`
- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Project policy: `src/.ralph/policy/project-policy.md`
- Upgrade preflight logic: `scripts/runtime_state_helpers.py`
- Release asset: `ralph-harness-v0.12.5.tar.gz`

## v0.12.4 - 2026-04-02

### Summary

This release restores Ralph's intended queue-draining control plane and makes subagent delegation a required part of every shipped adapter.

It closes the lifecycle gap that let execution stop after a single implementation checkpoint, re-centers shared-state reconciliation in the orchestrator, and aligns the planning, execution, review, verification, and release surfaces around one strict `launcher -> coordinator/orchestrator -> delegated workers` model.

### Highlights

- Tightened the shipped runtime contract so Codex, Claude Code, and Cursor are all treated as subagent-capable first-class adapters, and any adapter that cannot delegate the full Ralph topology is now unsupported instead of fallback-capable.
- Replaced partial task-selection wording with deterministic lifecycle routing for `ready`, `in_progress`, `awaiting_review`, `review_failed`, `awaiting_verification`, `verification_failed`, `awaiting_release`, and `release_failed`.
- Added `release_failed` to the canonical lifecycle definitions and made release outcomes explicit across the runtime contract, release skill, helper logic, and adapter surfaces.
- Re-centered reconciliation in the orchestrator so workers write only role-local outputs, release their claims, and exit while the orchestrator alone validates outputs, updates shared state, refreshes projections, and dispatches the next role.
- Updated the public `ralph-prd`, `ralph-plan`, and `ralph-execute` entrypoints plus generated Claude and Cursor surfaces so planning roles are delegated with the same strictness as execution roles.
- Added regression coverage for lifecycle routing, explicit release outcomes, native-subagent-only execution mode enforcement, queue-draining doctrine, and multi-adapter subagent isolation.
- Resynced the source repo's dogfood runtime mirrors with the shipped scaffold so release validation and upgrade-preflight continue to block real doctrine drift instead of silently tolerating it.

### Install And Upgrade Impact

- Use tag `v0.12.4` as the default public install or upgrade reference.
- Fresh installs now inherit the universal subagent-driven control-plane doctrine, the repaired lifecycle routing, and the explicit release-outcome contract.
- Existing installs can upgrade normally to pick up the queue-drain repair and stricter delegation model; `upgrade_contract_version` remains `11`.

### Validation And Release Workflow

- Verified the new lifecycle regression coverage with `python3 scripts/test-control-plane-lifecycle.py`.
- Verified the full release surface, including install and upgrade smoke coverage, with `bash scripts/validate-harness.sh`.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Project policy: `src/.ralph/policy/project-policy.md`
- Orchestrator skill: `src/.agents/skills/orchestrator/SKILL.md`
- Release skill: `src/.agents/skills/release/SKILL.md`
- Runtime helpers: `scripts/runtime_state_helpers.py`
- Release asset: `ralph-harness-v0.12.4.tar.gz`

## v0.12.3 - 2026-04-02

### Summary

This release repairs Ralph's control-plane preflight so execution no longer blocks on state the orchestrator is supposed to create or regenerate itself.

It teaches the runtime to self-heal derived projections and admitted worktrees, routes incomplete task registries back through planning instead of misclassifying them as upgrade failures, and aligns the public planning entrypoint with the actual `specify -> research -> plan -> task-gen -> plan-check` handoff needed to leave a repo execution-ready.

### Highlights

- Reworked installed-runtime preflight classification so `check-installed-runtime-state.py` distinguishes self-healable drift, planning or `task-gen` gaps, genuine upgrade drift, and hard repair conditions.
- Added runtime helpers that regenerate stale `workflow-state.md` and `specs/INDEX.md`, refresh derived workflow mirrors, and materialize missing admitted worktrees plus `.ralph/shared/` overlays when queue ownership is unambiguous.
- Replaced the unconditional `task-state.json` requirement with execution-readiness-aware gating, so planned specs can exist before `task-gen` while admitted or active specs still require canonical task registries.
- Updated public `ralph-execute`, `ralph-interrupt`, and `ralph-plan` doctrine plus generated adapter surfaces so they all describe the same repaired control-plane lifecycle.
- Synced the source repo's dogfood runtime, adapter pack, and managed role docs back to the shipped scaffold so release validation no longer depends on stale local doctrine.
- Added regression coverage for the reproduced failure modes: planned specs without `task-state.json`, admitted specs without worktrees, stale Markdown projections, and real baseline-drift upgrade failures.

### Install And Upgrade Impact

- Use tag `v0.12.3` as the default public install or upgrade reference.
- Fresh installs now inherit the repaired preflight model, the planning-coordinator handoff, and the new regression coverage.
- Existing installs can upgrade normally to pick up the preflight repair and planning-alignment fixes; `upgrade_contract_version` remains `11`.

### Validation And Release Workflow

- Verified the new targeted regression coverage with `python3 scripts/test-runtime-preflight-repairs.py`.
- Verified the installed-runtime preflight behavior locally with `python3 scripts/check-installed-runtime-state.py --repo .`.
- Verified the full release surface with `scripts/validate-harness.sh`.

### Artifacts And References

- Runtime helpers: `scripts/runtime_state_helpers.py`
- Installed-runtime validator: `scripts/check-installed-runtime-state.py`
- Public execute entrypoint: `skills/ralph-execute/SKILL.md`
- Public planning entrypoint: `skills/ralph-plan/SKILL.md`
- Capability registry: `src/.ralph/agent-registry.json`
- Release asset: `ralph-harness-v0.12.3.tar.gz`

## v0.12.2 - 2026-04-02

### Summary

This release restores Ralph's intended parallel execution topology under one orchestrator.

It keeps the public `ralph-execute` entry thread thin, but makes the shipped Codex runtime explicitly fill the admitted-spec execution window with bounded worker fan-out instead of collapsing into one-role-at-a-time local execution.

### Highlights

- Tightened the shipped runtime contract and project policy so each `ralph-execute` invocation owns exactly one orchestrator, and parallelism comes from worker subagents across admitted specs.
- Promoted `bootstrap`, `implement`, `review`, `verify`, and `release` to native-subagent-delegatable roles in the shipped capability registry and regenerated the Claude and Cursor adapter surfaces to match.
- Updated the Codex orchestrator adapter and orchestrator skill so they refill freed worker slots while runnable admitted work remains instead of treating a single completed handoff as a valid stop.
- Clarified the public `ralph-execute` and README surfaces so Codex defaults to one-orchestrator, many-workers behavior, while claim-holder execution remains a compatibility fallback for non-native or cross-runtime cases.
- Added smoke coverage for multi-spec active execution, mixed bootstrap-plus-implement admitted work, and dependency-limited serial behavior.

### Install And Upgrade Impact

- Use tag `v0.12.2` as the default public install or upgrade reference.
- Fresh installs now inherit the corrected one-orchestrator/many-workers execution doctrine and regenerated adapter guidance.
- Existing installs can upgrade normally to pick up the parallel worker fan-out fix; `upgrade_contract_version` remains `11`.

### Validation And Release Workflow

- Verified the focused contract suite with `scripts/verify-subagent-isolation-contract.sh`, `scripts/verify-multi-spec-contract.sh`, `scripts/verify-human-stop-boundaries.sh`, `scripts/verify-canonical-control-plane-contract.sh`, and `scripts/verify-upgrade-contract.sh`.
- Verified the install and upgrade smoke coverage with `scripts/smoke-test-install-upgrade.sh`.
- Verified the full release surface with `scripts/validate-harness.sh`.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Capability registry: `src/.ralph/agent-registry.json`
- Codex orchestrator adapter: `src/.codex/agents/orchestrator.toml`
- Public execute entrypoint: `skills/ralph-execute/SKILL.md`
- Release asset: `ralph-harness-v0.12.2.tar.gz`

## v0.12.1 - 2026-04-01

### Summary

This release hardens the Ralph control plane around a strict launcher-to-orchestrator delegation model.

It keeps public Ralph entry threads thin, moves substantive PRD, planning, and execution work into dedicated subagents, raises the managed Codex depth cap just enough to support that topology, and closes the remaining drift across generated adapters, install and upgrade guidance, and dogfood managed skills.

### Highlights

- Tightened public `ralph-execute`, `ralph-plan`, and `ralph-prd` entrypoints so the invoking thread immediately launches the dedicated Ralph subagent for that entrypoint instead of doing the work inline.
- Updated the shipped runtime contract and project policy so thin launcher threads and dedicated orchestrator or role subagents are part of the control-plane doctrine rather than an optional prompt habit.
- Raised the Ralph-managed Codex delegation topology to `agents.max_depth = 3`, allowing `entry thread -> orchestrator or role subagent -> worker subagents` while still forbidding deeper fan-out.
- Fixed the runtime adapter generator so Claude and Cursor generated surfaces preserve the thin-thread launcher contract during regeneration.
- Synced root dogfood managed skills back to the shipped `src/.agents/skills/` baselines so upgrade-surface validation no longer reports control-plane drift.

### Install And Upgrade Impact

- Use tag `v0.12.1` as the default public install or upgrade reference.
- Fresh installs now inherit the thin-launcher control-plane model, regenerated adapter guidance, and `agents.max_depth = 3`.
- Existing installs can upgrade normally to pick up the launcher-binding and adapter-drift fixes; `upgrade_contract_version` remains `11`.

### Validation And Release Workflow

- Verified the full release surface with `bash scripts/validate-harness.sh`.
- Re-ran the focused install, upgrade, and subagent-isolation checks after regenerating the adapter surfaces and resyncing managed skills.

### Artifacts And References

- Adapter generator: `scripts/generate-runtime-adapters.py`
- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Install guide: `INSTALLATION.md`
- Upgrade guide: `UPGRADING.md`
- Release asset: `ralph-harness-v0.12.1.tar.gz`

## v0.12.0 - 2026-04-01

### Summary

This release removes queue-head semantics from the shipped runtime contract and upgrade path.

It replaces FIFO-head phrasing with explicit-first ready-set scheduling, raises the default parallel admission capacity through runtime-derived limits, and teaches migration plus validation to discard legacy queue-head fields instead of preserving them.

### Highlights

- Removed queue-head wording from shipped workflow templates, TODO templates, runtime doctrine, and execute-facing guidance.
- Switched the scaffold and runtime helpers from `fifo_admission_window` to `explicit_first_ready_set`.
- Made the default `normal_execution_limit` derive from the runtime thread budget, reserving one thread for the orchestrator.
- Updated runtime migration and validation so legacy `queue_head_spec_id` fields are ignored or removed rather than normalized back into current state.
- Added ordered `target_spec_ids` support to durable scheduling intents so explicit user requests survive lease contention.
- Tightened public `ralph-execute`, `ralph-plan`, and `ralph-prd` entrypoints so the invoking thread stays thin and immediately launches the dedicated Ralph subagent for that entrypoint.
- Raised the Ralph-managed Codex delegation depth contract to `agents.max_depth = 3` so entry-thread launchers can hand off to an orchestrator or role subagent, which may still launch worker subagents without allowing deeper nesting.

### Install And Upgrade Impact

- Use tag `v0.12.0` as the default public install or upgrade reference.
- Fresh installs now seed explicit-first ready-set scheduler metadata with a default normal-spec capacity of `3` from the shipped Codex thread budget.
- Existing installs upgrade to `upgrade_contract_version` `11`, which removes queue-head dependence from migrated workflow state and validation.

### Validation And Release Workflow

- Verified helper, template, and doctrine changes through `scripts/validate-harness.sh`.
- Expanded the install and upgrade smoke coverage to keep legacy queue-head fixtures only as migration inputs, not as current-runtime outputs.

### Artifacts And References

- Runtime helpers: `scripts/runtime_state_helpers.py`
- Upgrade guide: `UPGRADING.md`
- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Workflow templates: `src/.ralph/templates/`
- Release asset: `ralph-harness-v0.12.0.tar.gz`

## v0.11.4 - 2026-03-28

### Summary

This release completes a full doctrine-consistency pass across the shipped role skills, adapter references, and dogfood release rules.

It closes the remaining gap where some worker-facing surfaces still used generic `.ralph/state` and report-path wording after the canonical-control-plane model shipped, and it records a stronger dogfood release truth that doctrine drift is itself a release blocker.

### Highlights

- Updated the remaining shipped role skills so shared-state reads and canonical report writes explicitly resolve through the canonical checkout or `.ralph/shared/` when running from a spec worktree.
- Tightened the shipped reporting, state-sync, release, planning, research, and specification guidance so path ownership is explicit instead of generic.
- Updated the adapter registry and generated loader surfaces so `last_report_path` and shared-state guidance stay aligned with canonical-control-plane ownership.
- Expanded the canonical-control-plane verifier to cover the wider shipped skill and reference surface.
- Added dogfood project truth and learning records requiring a full alignment review of skills, doctrine files, adapter references, and control services before every release.

### Install And Upgrade Impact

- Use tag `v0.11.4` as the default public install or upgrade reference.
- Fresh installs and upgrades now point at a release where worker-facing skills, adapter surfaces, and doctrine files all agree on canonical shared-state ownership.
- `upgrade_contract_version` remains `10`; this patch tightens doctrine consistency and release discipline without changing migration schema.

### Validation And Release Workflow

- Verified the expanded doctrine checks with `scripts/verify-canonical-control-plane-contract.sh`.
- Regenerated shipped adapter files with `python3 scripts/generate-runtime-adapters.py`.
- Verified the full release surface with `scripts/validate-harness.sh`.

### Artifacts And References

- Shipped role skills: `src/.agents/skills/`
- Adapter registry: `src/.ralph/agent-registry.json`
- Generated loaders: `src/AGENTS.md`, `src/CLAUDE.md`
- Dogfood release truth: `.ralph/context/project-truths.md`
- Release asset: `ralph-harness-v0.11.4.tar.gz`

## v0.11.3 - 2026-03-28

### Summary

This release finishes the control-plane alignment pass across the public release surface.

It brings the README and doctrine verifier into the same canonical-control-plane model already enforced by the shipped harness, so installation, upgrade, execution, and contributor-facing explanations all describe one authoritative shared-state story.

### Highlights

- Updated the README to explicitly define the canonical shared control plane, generated `.ralph/shared/` overlays, and the non-authoritative status of tracked shared-state copies inside spec worktrees.
- Tightened the doctrine verifier so README plus the public `ralph-install` and `ralph-upgrade` entrypoints are checked alongside the shipped runtime contract and role skills.
- Kept the shipped `src/` runtime behavior unchanged while closing the last public-documentation drift from the canonical control-plane doctrine.

### Install And Upgrade Impact

- Use tag `v0.11.3` as the default public install or upgrade reference.
- Fresh installs and upgrades now point at a release whose public docs, install guide, upgrade guide, public skills, and shipped contract all agree on canonical shared-state ownership.
- `upgrade_contract_version` remains `10`; this patch is release-surface alignment work, not a migration-schema change.

### Validation And Release Workflow

- Verified the doctrine-specific checks with `scripts/verify-canonical-control-plane-contract.sh`.
- Verified the full release surface with `scripts/validate-harness.sh`.

### Artifacts And References

- Public overview: `README.md`
- Install guide: `INSTALLATION.md`
- Upgrade guide: `UPGRADING.md`
- Canonical doctrine verifier: `scripts/verify-canonical-control-plane-contract.sh`
- Release asset: `ralph-harness-v0.11.3.tar.gz`

## v0.11.2 - 2026-03-28

### Summary

This release hardens the shipped harness around a single canonical control plane.

It stops treating worktree-local tracked copies of shared state as meaningful runtime inputs, teaches shipped skills and coordination helpers to resolve shared artifacts back to the canonical checkout, and adds validation plus smoke coverage so multi-agent spec execution sees one authoritative control-plane view.

### Highlights

- Declared the canonical shared control plane explicitly in the shipped runtime contract and project policy, with spec worktrees reserved for branch-owned execution artifacts.
- Added canonical-root resolution and generated `.ralph/shared/` overlays for admitted worktrees so workers can read canonical shared state safely without relying on tracked worktree duplicates.
- Tightened orchestrator reconciliation so it mutates canonical shared state directly instead of copying tracked control-plane files back from worktrees.
- Updated the shipped bootstrap, implement, review, verify, install, upgrade, and execute surfaces so they all expose the same canonical shared-state ownership model.
- Added install, upgrade, and smoke-test safeguards that fail when a spec worktree edits shared-control-plane paths or when the generated overlay is missing or invalid.

### Install And Upgrade Impact

- Use tag `v0.11.2` as the default public install or upgrade reference.
- Fresh installs and upgrades now create or validate `.ralph/shared/` overlays for admitted worktrees and enforce canonical shared-state ownership during execution.
- `upgrade_contract_version` remains `10`; this patch tightens ownership and validation without introducing a new migration schema.

### Validation And Release Workflow

- Verified the new overlay, reconciliation, and dirty-control-plane cases with `scripts/smoke-test-install-upgrade.sh`.
- Verified the full release surface with `scripts/validate-harness.sh`.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Runtime helpers: `scripts/runtime_state_helpers.py`
- Coordination CLI: `scripts/orchestrator-coordination.py`
- Public execute skill: `skills/ralph-execute/SKILL.md`
- Release asset: `ralph-harness-v0.11.2.tar.gz`

## v0.11.1 - 2026-03-28

### Summary

This release tightens Ralph's queue-throughput doctrine so the executor keeps working through every runnable spec instead of slipping back toward one-spec-and-stop behavior.

It makes the queue-draining posture explicit in the shipped runtime contract, project policy, orchestrator prompts, and public execute skill, while also removing queue-head wording from plan-check so spec-level serialization does not get mistaken for whole-queue serialization.

### Highlights

- Declared queue-wide throughput as the default operating principle in the shipped `src/.ralph/runtime-contract.md` and `src/.ralph/policy/project-policy.md`.
- Tightened the shipped orchestrator prompts so they prefer filling every runnable admission slot before considering a stop.
- Removed queue-head framing from plan-check and narrowed its sequentiality requirement to one-task-at-a-time execution within a single spec's task graph.
- Updated the public `ralph-execute` skill so it explicitly keeps advancing runnable specs in series or bounded parallel as dependencies allow.

### Install And Upgrade Impact

- Use tag `v0.11.1` as the default public install or upgrade reference.
- Fresh installs and upgrades now carry the tighter queue-throughput doctrine and stop-boundary wording.
- `upgrade_contract_version` remains `10`; this patch updates doctrine and runtime prompts, not the migration schema.

### Validation And Release Workflow

- Verified the install and upgrade contracts, queue-throughput doctrine, and mixed-ownership preservation scenarios with `scripts/smoke-test-install-upgrade.sh`.
- Verified the full release surface with `scripts/validate-harness.sh`.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Public execute skill: `skills/ralph-execute/SKILL.md`
- Plan-check skill: `src/.agents/skills/plan-check/SKILL.md`
- Upgrade contract: `UPGRADING.md`
- Release asset: `ralph-harness-v0.11.1.tar.gz`

## v0.10.1 - 2026-03-26

### Summary

This patch tightens the release-facing doctrine after the control-plane bootstrap and ephemeral-lease rollout.

It closes the remaining drift between the latest control-plane contract and the supporting docs, public skills, generated guidance, and dogfood learning records, while also turning that audit expectation into an explicit source-repo lesson for future releases.

### Highlights

- Fixed remaining doctrine drift so the shipped runtime contract, README flow, spec-index template, and install or upgrade skills all align with bootstrap-gated, worktree-only execution.
- Added a dogfood release-process lesson: before publishing a tag, run an explicit drift pass across the control plane, supporting docs, public skills, generated sub-agent instructions, and related release surfaces.
- Promoted that lesson into the source repo's learning summary and project truths so future release passes treat doctrine alignment as an operational expectation, not an ad hoc cleanup.

### Install And Upgrade Impact

- Use tag `v0.10.1` as the default public install or upgrade reference.
- Fresh installs and upgrades now point to the corrected current stable tag in docs and examples.
- `upgrade_contract_version` remains `9`; this patch is doctrine and release-surface alignment work, not a new migration contract.

### Validation And Release Workflow

- Verified locally with `python3 scripts/generate-runtime-adapters.py --check`.
- Verified the full contract suite and smoke fixtures with `scripts/validate-harness.sh`.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Public install skill: `skills/ralph-install/SKILL.md`
- Public upgrade skill: `skills/ralph-upgrade/SKILL.md`
- Dogfood learning summary: `.ralph/context/learning-summary.md`
- Dogfood lessons log: `tasks/lessons.md`
- Release asset: `ralph-harness-v0.10.1.tar.gz`

## v0.10.0 - 2026-03-26

### Summary

Ralph now treats worktree bootstrap as a mandatory execution boundary and makes control-plane leasing explicitly ephemeral.

This release hardens the shipped runtime for real multi-app, multi-thread coordination: the canonical checkout remains a shared control plane, spec execution happens only inside per-spec worktrees, and any eligible session may briefly acquire the lease to reconcile validated shared-state updates.

### Highlights

- Added a first-class `bootstrap` role, skill, agent config, registry entry, state fields, and report path contract.
- Made `.ralph/context/project-facts.json.base_branch` the canonical resolved base branch and taught install, upgrade, migration, and worktree creation to discover and persist it.
- Tightened validation so non-bootstrap execution requires a bootstrap-passed, validation-ready claim and fails when work drifts back into the canonical checkout.
- Promoted `active_spec_ids` to the authoritative active-spec model while demoting single-active mirrors to compatibility metadata.
- Added short-lived reconciliation support so a finishing worker session can briefly acquire the lease and write back validated queue, workflow, and bootstrap-summary updates.
- Expanded smoke fixtures and contract checks to cover bootstrap gating, worktree-only execution, cross-runtime claims, and canonical branch enforcement.

### Install And Upgrade Impact

- Use tag `v0.10.0` as the default public install or upgrade reference.
- Fresh installs now seed bootstrap-aware queue and claim state, a bootstrap role, canonical base-branch discovery, and validation bootstrap command support in project facts.
- Upgrades continue to use `upgrade_contract_version` `9`, but now backfill bootstrap lifecycle metadata, bootstrap summaries, and persisted canonical base-branch facts.

### Validation And Release Workflow

- Verified locally with `python3 scripts/generate-runtime-adapters.py --check`.
- Verified the updated contract suite and smoke fixtures with `scripts/smoke-test-install-upgrade.sh`.
- Verified the full release surface with `scripts/validate-harness.sh`.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Runtime helpers: `scripts/runtime_state_helpers.py`
- Coordination CLI: `scripts/orchestrator-coordination.py`
- Bootstrap skill: `src/.agents/skills/bootstrap/SKILL.md`
- Project facts seed: `src/.ralph/context/project-facts.json`
- Release asset: `ralph-harness-v0.10.0.tar.gz`

## v0.9.0 - 2026-03-25

### Summary

Ralph is now scaffolded as an agent-agnostic multi-runtime harness instead of a Codex-only control plane.

This release keeps the shared Ralph doctrine and queue semantics under `.ralph/`, adds first-class Claude Code and Cursor adapter packs alongside the existing Codex pack, and introduces a worker-claims registry so different supported runtimes can claim different admitted spec slots safely while one orchestrator still owns shared-state reconciliation.

### Highlights

- Rewrote the shipped runtime contract, project policy, public docs, and loaders around a runtime-neutral lease-plus-claims execution model.
- Added a canonical agent registry at `src/.ralph/agent-registry.json` plus generated adapter packs for `AGENTS.md`, `CLAUDE.md`, `.claude/agents/`, `.claude/commands/`, and `.cursor/rules/`.
- Added `.ralph/state/execution-claims.json` and the corresponding template and migration logic for cross-runtime slot claiming.
- Switched new scaffold branch defaults from `codex/<spec-key>` to `ralph/<spec-key>` while preserving legacy branch prefixes during upgrade.
- Extended install and upgrade manifests so all supported adapter packs ship together by default.
- Added claim operations to `scripts/orchestrator-coordination.py` and generalized validation to cover the generated runtime adapters.

### Install And Upgrade Impact

- Use tag `v0.9.0` as the default public install or upgrade reference.
- Fresh installs now include synchronized `AGENTS.md` and `CLAUDE.md` loader blocks, the Codex adapter pack, the Claude adapter pack, the Cursor adapter pack, and the shared worker-claims state file.
- Upgrades now migrate installed repos to `upgrade_contract_version` `8`, preserve the effective branch prefix in `.ralph/harness-version.json`, and add the new multi-runtime adapter metadata.

### Validation And Release Workflow

- Verified locally with `python3 scripts/generate-runtime-adapters.py --check`.
- Verified the updated contract suite and smoke fixtures with `bash scripts/validate-harness.sh`.

### Artifacts And References

- Runtime doctrine: `src/.ralph/runtime-contract.md`
- Agent registry: `src/.ralph/agent-registry.json`
- Worker claims state: `src/.ralph/state/execution-claims.json`
- Runtime coordination helper: `scripts/orchestrator-coordination.py`
- Release asset: `ralph-harness-v0.9.0.tar.gz`

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
