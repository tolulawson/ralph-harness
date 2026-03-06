# Harness Bootstrap TODO

## Plan

- [x] Inspect the empty repo and confirm local Codex config and skill conventions.
- [x] Scaffold the Codex-native control plane: `AGENTS.md`, `.codex/config.toml`, role configs, runtime directories, and task tracking files.
- [x] Define runtime state, logging, policy, and template contracts under `.ralph/`.
- [x] Create repo-local role skills under `.agents/skills/`.
- [x] Seed the example project PRD and numbered spec artifacts for the reference repo.
- [x] Record bootstrap reports and event log entries so the harness can resume from disk alone.
- [x] Run structure and schema verification, then record results in the review section below.
- [x] Add a top-level `README.md` that explains the repository objective, control flow, installation, and operator scenarios for new projects, existing projects, features, and bug fixes.
- [x] Split the long installation instructions into a separate installation guide and update the README to point to it.
- [x] Adapt the local PRD and Speckit-derived role skills more closely to their source workflows and add an artifact-analysis helper skill.
- [x] Refactor the harness so `AGENTS.md` is a thin loader, move the doctrine into `.ralph/constitution.md`, and update installation docs to preserve or append to existing project `AGENTS.md` files.
- [x] Add four distributable source skills under `skills/` for installing, shaping PRDs, planning, and executing the Ralph harness, and document the distinction from `.agents/skills/`.
- [x] Refactor the runtime control plane from a single active-feature model to an epoch-driven spec queue with numbered spec IDs and canonical spec state.
- [x] Add queue-first state artifacts and templates: `.ralph/state/spec-queue.json`, `specs/INDEX.md`, and numbered spec directory templates.
- [x] Update the orchestrator, planning, release, review, verify, and public `ralph-*` skills to operate on spec queue entries, active PR context, and FIFO execution.
- [x] Migrate the example bootstrap artifacts to the new numbered-spec structure and refresh the sample workflow/event state to match.
- [x] Refresh README and installation guidance so downstream projects install and operate the numbered spec queue and real PR loop correctly.
- [x] Run structural verification for the updated TOML, JSON, queue, and reference artifacts, then record the results below.
- [x] Split the repository into `src/` as the canonical installable scaffold and the repo root as the live dogfood runtime.
- [x] Add `src/install-manifest.txt`, seed scaffold state, and starter runtime files that can be copied into target projects without copying this repo's dogfood history.
- [x] Retarget the installer skill and installation guide to install from `src/` only, and document the separation between root dogfood runtime and `src/` scaffold.
- [x] Run source-vs-dogfood verification to prove the install manifest copies scaffold files but excludes root runtime history.
- [x] Refactor `src/` into a clean shipped scaffold that excludes authored TODOs, lessons, event logs, and other procedural development records.
- [x] Update install contracts so `ralph-install` copies only scaffold files from `src/` and generates runtime tracking files in the target repo after install.
- [x] Add a generated-runtime manifest so install-time file creation is an explicit contract instead of an implicit behavior.

## Review

- `python3` on this machine is `3.9.6`, so TOML verification used `pip._vendor.tomli` instead of `tomllib`.
- Verified `.codex/config.toml` and all `agents/*.toml` parse successfully.
- Verified `.ralph/state/workflow-state.json` and all 8 entries in `.ralph/logs/events.jsonl` parse successfully.
- Verified `.ralph/state/workflow-state.md` matches the key JSON fields for active spec, task, phase, event id, and last report path.
- Verified the scaffolded skill and report directories exist with 12 repo-local skills and 8 bootstrap reports.
- Added `README.md` with setup instructions, usage scenarios, and role/skill invocation guidance for Codex-driven adoption in downstream repos.
- Verified `README.md` includes the requested setup section plus all four scenarios: bootstrapping a new project, installing the harness into an existing project, developing a new feature, and performing bug fixes.
- Added `INSTALLATION.md` and reduced the README installation section to a guide pointer plus summary.
- Reworked the local PRD, specify, plan, task-gen, and implement skills to follow the referenced source skills more closely, while preserving this harness's report and state contracts.
- Added an `analyze` helper skill so review-side artifact analysis can follow the Speckit-style consistency workflow more closely.
- Refactored the harness so `AGENTS.md` is now a thin Codex loader and `.ralph/constitution.md` holds the durable harness doctrine.
- Updated installation guidance so an existing project `AGENTS.md` is preserved and gets a short Ralph loader section appended instead of being replaced.
- Reframed the top-level docs and constitution so this repository is clearly a reference template for other projects rather than a self-hosted Ralph deployment target.
- Replaced the old long-form public skill names with `skills/ralph-install` and `skills/ralph-execute`, and added `skills/ralph-prd` and `skills/ralph-plan` as direct-access public entry points.
- Documented the distinction between top-level distributable source skills and installed runtime `.agents/skills`.
- Verified there are exactly 4 distributable source skill directories, 4 `SKILL.md` files, and 4 `agents/openai.yaml` files under `skills/`.
- Verified the installer skill names the canonical GitHub source, preserves and appends to an existing `AGENTS.md`, the PRD and plan skills expose direct shaping and planning entry points, and the execute skill reads constitution, policy, state, latest report, and recent events before resuming.
- Refactored the runtime model from one active feature to a queue-driven `PRD -> epochs -> numbered specs -> tasks -> branch/PR` workflow.
- Added `.ralph/state/spec-queue.json`, `specs/INDEX.md`, and numbered spec templates so the queue has both machine-readable and human-readable projections.
- Migrated the example artifacts to `tasks/prd-ralph-harness.md` plus `specs/001-self-bootstrap-harness/` and refreshed the sample event log and bootstrap reports to match the numbered spec model.
- Updated the runtime and public skill surfaces so `orchestrator`, `plan`, `release`, `ralph-prd`, `ralph-plan`, and `ralph-execute` all understand epochs, numbered specs, FIFO queue selection, and PR context.
- Verified `.ralph/state/workflow-state.json`, `.ralph/state/spec-queue.json`, and all 8 entries in `.ralph/logs/events.jsonl` parse successfully.
- Verified `.ralph/state/workflow-state.md` matches the active spec and last report, and `specs/INDEX.md` matches the queue head spec and status semantically.
- Verified the scaffold now contains 12 repo-local skills and 8 bootstrap reports.
- Added a Mermaid flow diagram to `README.md` that shows how the harness loop moves from project PRD through epochs, numbered specs, task execution, review, verification, release, and queue advancement.
- Split the repository into a canonical scaffold under `src/` and a live dogfood runtime at the repo root.
- Added `src/install-manifest.txt`, seed state files, starter task files, an empty spec register, and empty runtime directories so installed target repos receive clean scaffold state instead of dogfood history.
- Verified all 14 manifest-listed `src/` paths exist.
- Verified a temp install copied clean scaffold files from `src/` and did not leak `tasks/prd-ralph-harness.md`, `specs/001-self-bootstrap-harness/`, or `.ralph/reports/bootstrap-20260305/`.
- Refined the repository contract so root is the workshop and dogfood runtime, while `src/` is the clean shipped scaffold output for downstream repos.
- Removed authored procedural files from `src/`, including scaffold TODOs, lessons, and seed event history, while keeping neutral state and template artifacts.
- Added `src/generated-runtime-manifest.txt` so install-time file creation is an explicit contract instead of an implicit behavior.
- Updated `README.md`, `INSTALLATION.md`, `AGENTS.md`, both constitutions, and the public `ralph-install` and `ralph-execute` skills to explain that target runtime records are generated after scaffold copy instead of being copied from `src/`.
- Verified `src/` no longer contains `tasks/todo.md`, `tasks/lessons.md`, or `.ralph/logs/events.jsonl`.
- Verified the new install manifest omits procedural runtime records and the generated-runtime manifest names the files and directories that `ralph-install` must create after copying the scaffold.
- Refined the doctrine split after review: root `AGENTS.md` and root `.ralph/constitution.md` now describe this repository's fixed source-repo ground truth, while the `src/` copies are generic installed-harness documents.
- Removed the old automatic source-to-root update concept so `src/` remains pure and root changes happen only when explicitly requested.
- Remaining runtime caveat: the declared multi-agent config still needs to be exercised in a live Codex session to prove exact runtime acceptance.
