# Installation Guide

This guide explains how an LLM or human operator should install the Ralph multi-agent runtime into a target repository.

`INSTALLATION.md` is the canonical install source of truth for this repository.

## Source Of Truth

The installable scaffold source is:

- `src/` in [tolulawson/ralph-harness](https://github.com/tolulawson/ralph-harness) at tag `v0.13.1`

The canonical copy contract is:

- [src/install-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.13.1/src/install-manifest.txt)

The canonical generated-runtime contract is:

- [src/generated-runtime-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.13.1/src/generated-runtime-manifest.txt)

The current harness version source is:

- [`VERSION`](https://github.com/tolulawson/ralph-harness/blob/v0.13.1/VERSION)

The install authority order is:

1. [INSTALLATION.md](https://github.com/tolulawson/ralph-harness/blob/v0.13.1/INSTALLATION.md)
2. [src/install-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.13.1/src/install-manifest.txt)
3. [src/generated-runtime-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.13.1/src/generated-runtime-manifest.txt)
4. [VERSION](https://github.com/tolulawson/ralph-harness/blob/v0.13.1/VERSION)

Do not install from the repository root. The root contains source-repo docs, public source-entry skills, validation scripts, and release tooling that are not part of the installable scaffold.

## Goal

After installation, the target repository should contain:

- synchronized Ralph loader blocks in `AGENTS.md` and `CLAUDE.md`
- the harness constitution
- the runtime contract
- the Codex adapter pack
- the Claude adapter pack
- the Cursor adapter pack
- repo-local hook configs for Codex, Claude Code, and Cursor
- repo-local role skills
- the shipped `research` and `plan-check` roles
- the shared Ralph stop-boundary hook under `.ralph/hooks/`
- neutral seed runtime state and templates
- generated runtime tracking files, logs, and report directories
- the canonical shared control plane in the selected canonical checkout (current checkout by default)
- generated `.ralph/shared/` overlays inside admitted spec worktrees for shared reads and canonical report writes
- project-specific policy
- a starter spec register

## Optional Helper Skill

No skill is required to install the harness. This document is sufficient on its own.

If a user prefers a named helper entrypoint, this repository also exposes `ralph-install` under `skills/`. That skill is optional and must follow this guide.

Other public `ralph-*` skills are outside the install contract and are not needed to install the harness. Use `ralph-upgrade` or `ralph-interrupt` only after the harness is already installed.

## Installation Modes

### Option 1: Ask your coding agent to install the harness

This is the intended workflow.

From inside the target repository, ask your coding agent to use `src/` as the source template:

```text
Use https://github.com/tolulawson/ralph-harness as the scaffold source repository.
Use tag v0.13.1 from that repository unless the user explicitly requests another release.
Use the scaffold under src/ in that repository.
Install the Ralph multi-agent runtime into this repository using src/install-manifest.txt as the copy contract.
Preserve the existing AGENTS.md and CLAUDE.md if they already exist and replace only the managed Ralph blocks between <!-- RALPH-HARNESS:START --> and <!-- RALPH-HARNESS:END -->.
The managed Ralph blocks must tell the active coding agent to read .ralph/constitution.md, .ralph/runtime-contract.md, .ralph/policy/runtime-overrides.md, .ralph/policy/project-policy.md, .ralph/context/project-truths.md, .ralph/context/project-facts.json, .ralph/context/learning-summary.md, .ralph/state/workflow-state.json, .ralph/state/spec-queue.json, .ralph/state/scheduler-lock.json, .ralph/state/execution-claims.json, only a recent tail of .ralph/state/scheduler-intents.jsonl, the latest report, and only a recent tail of .ralph/context/learning-log.jsonl when diagnosing or promoting learnings.
Copy only the manifest-listed runtime adapter files, repo-local role skills, neutral seed state files, and templates.
Then create the generated runtime files listed in src/generated-runtime-manifest.txt.
Do not copy repo-root source-repo docs, scripts, public source-entry skills, or other files outside `src/`.
Adapt the constitution, project policy, runtime overrides, and copied knowledge files for this repo, preserve existing code, keep the base `.ralph/runtime-contract.md` scaffold-owned, discover and persist the canonical base branch in `.ralph/context/project-facts.json`, seed any `validation_bootstrap_commands` that are already known, create the project PRD, decompose it into epochs and numbered specs, seed the initial explicit-first ready-set queue plus `depends_on_spec_ids` only for true execution prerequisites between specs, keep any planning-time parallelism limited to same-batch research only, seed the scheduler lock, execution claims, and durable intents files, create the `.ralph/worktrees/` directory, reserve the canonical shared control plane for the selected canonical checkout, generate `.ralph/shared/` overlays when admitted spec worktrees are created or refreshed, and update .ralph/harness-version.json with the selected tag, the resolved commit, the scaffold runtime-contract baseline hash, the installed adapter packs, and the default branch prefix.
Seed `.ralph/context/project-facts.json` with the conservative stop-hook policy plus bootstrap hydration fields: `orchestrator_stop_hook`, `worktree_bootstrap_commands`, `bootstrap_env_files`, and `bootstrap_copy_exclude_globs`.
Before finalizing `.ralph/context/project-facts.json`, use the runtime's question/input tool to ask the user whether the current checkout should remain the canonical control plane (`canonical_control_plane.mode = "current_checkout"`) or whether they want a custom control-plane checkout path or branch (`canonical_control_plane.mode = "custom"` with `canonical_control_plane.checkout_path` and optional `canonical_control_plane.base_branch`).
Use the runtime's question/input tool to ask whether control-plane artifacts should stay tracked in git (`control_plane_versioning.mode = "track"`), be kept out of version control with `.gitignore` patterns (`control_plane_versioning.mode = "gitignore"` with `control_plane_versioning.gitignore_patterns`), or use a custom policy (`control_plane_versioning.mode = "custom"`).
Install repo-local `.codex/hooks.json`, `.claude/settings.json`, `.cursor/hooks.json`, and `.ralph/hooks/stop-boundary.py`.
Keep `bootstrap_env_files` allowlisted and leave `bootstrap_copy_exclude_globs` on the default no-copy policy for dependency, cache, and build artifacts unless the project explicitly needs something narrower.
Do not put project-specific runtime contract or control-plane customizations into `.ralph/runtime-contract.md` or Ralph-managed runtime skill directories; write those into `.ralph/policy/runtime-overrides.md`, `.ralph/policy/project-policy.md`, and `.ralph/context/project-facts.json` extension fields.
```

### Option 2: Copy the scaffold manually

From the parent directory of the target repository:

```bash
SOURCE_REPO_URL=https://github.com/tolulawson/ralph-harness
SOURCE_REF=v0.13.1
TARGET_REPO=/path/to/target-repo
WORK_DIR="$(mktemp -d)"

git clone --depth=1 --branch "$SOURCE_REF" "$SOURCE_REPO_URL" "$WORK_DIR/ralph-harness"
SOURCE_REPO="$WORK_DIR/ralph-harness"

while IFS= read -r path; do
  [[ -z "$path" || "$path" == \#* ]] && continue
  mkdir -p "$TARGET_REPO/$(dirname "$path")"
  rsync -a "$SOURCE_REPO/src/$path" "$TARGET_REPO/$path"
done < "$SOURCE_REPO/src/install-manifest.txt"

rm -rf "$WORK_DIR"
```

Then create the runtime files listed in [src/generated-runtime-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.13.1/src/generated-runtime-manifest.txt), refresh the managed Ralph block in `AGENTS.md`, update `.ralph/harness-version.json`, discover and persist the canonical base branch in `.ralph/context/project-facts.json`, and adapt the target repository before first use.

## Optional Skill-Driven Entry

If `ralph-install` is available, you may invoke it as a convenience entrypoint.

That skill is not required for installation and does not replace this guide. It must execute the workflow defined here.

## What Gets Copied

Copy only the manifest-listed scaffold paths from `src/`:

- `AGENTS.md`
- `CLAUDE.md`
- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/agents/`
- `.claude/settings.json`
- `.claude/agents/`
- `.claude/commands/`
- `.cursor/hooks.json`
- `.cursor/rules/`
- `.agents/skills/analyze/`
- `.agents/skills/bootstrap/`
- `.agents/skills/deslopify-lite/`
- `.agents/skills/implement/`
- `.agents/skills/learning/`
- `.agents/skills/orchestrator/`
- `.agents/skills/plan/`
- `.agents/skills/plan-check/`
- `.agents/skills/prd/`
- `.agents/skills/react-effects-without-effects/`
- `.agents/skills/release/`
- `.agents/skills/reporting/`
- `.agents/skills/research/`
- `.agents/skills/review/`
- `.agents/skills/specify/`
- `.agents/skills/state-sync/`
- `.agents/skills/task-gen/`
- `.agents/skills/verify/`
- `.ralph/constitution.md`
- `.ralph/runtime-contract.md`
- `.ralph/harness-version.json`
- `.ralph/context/`
- `.ralph/hooks/`
- `.ralph/policy/`
- `.ralph/state/`
- `.ralph/templates/`
- `specs/INDEX.md`

## What Gets Generated After Copy

After copying the scaffold, create the runtime records listed in [src/generated-runtime-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.13.1/src/generated-runtime-manifest.txt):

- `tasks/todo.md`
- `tasks/lessons.md`
- `.ralph/logs/events.jsonl`
- `.ralph/reports/`
- `.ralph/summaries/`
- `.ralph/worktrees/`

When Ralph later creates or refreshes an admitted spec worktree, it must also generate `.ralph/shared/` inside that worktree as an untracked overlay back to the canonical shared control plane in the selected canonical checkout.

## What Must Not Be Copied

Do not copy repo-root source-repo files into target repos. Installation should copy only the manifest-listed scaffold under `src/`.

In particular, do not copy:

- `/README.md`
- `/INSTALLATION.md`
- `/UPGRADING.md`
- `/CHANGELOG.md`
- `/VERSION`
- `/LICENSE`
- `/scripts/`
- `/skills/`
- any other repo-root path that is not listed in `src/install-manifest.txt`

## Existing Loader Handling

If the target repository already has an `AGENTS.md` or `CLAUDE.md`, do not replace either file wholesale.

## Canonical AGENTS Loader Snippet

The Ralph-owned block in the installed `AGENTS.md` and `CLAUDE.md` must live between these markers:

```md
<!-- RALPH-HARNESS:START -->
... Ralph loader block ...
<!-- RALPH-HARNESS:END -->
```

That managed block should say, in substance:

- this repo uses the Ralph harness
- the active coding agent should read `.ralph/constitution.md`
- then read `.ralph/runtime-contract.md`
- then read `.ralph/policy/runtime-overrides.md`
- then read `.ralph/policy/project-policy.md`
- then read `.ralph/context/project-truths.md`
- then read `.ralph/context/project-facts.json`
- then read `.ralph/context/learning-summary.md`
- then read `.ralph/state/workflow-state.json`
- then read `.ralph/state/spec-queue.json`
- then read `.ralph/state/scheduler-lock.json`
- then read `.ralph/state/execution-claims.json`
- then tail only a recent window of `.ralph/state/scheduler-intents.jsonl`
- then read the latest report referenced by `last_report_path`
- then read only a recent tail of `.ralph/context/learning-log.jsonl` when diagnosing or promoting learnings
- when operating from a spec worktree, resolve shared-state reads and writes to the canonical checkout directly or through the generated `.ralph/shared/` overlay instead of using tracked worktree copies

The root `AGENTS.md` and `CLAUDE.md` in the target repo should remain loaders, not the full harness doctrine.

## What To Reset For The Target Repository

After copying from `src/`, rewrite:

- `.ralph/harness-version.json`
- `.ralph/policy/runtime-overrides.md`
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- `.ralph/context/learning-log.jsonl`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/workflow-state.md`
- `specs/INDEX.md`
- generated `tasks/todo.md`
- generated `tasks/lessons.md`

Set at minimum:

- installed harness version tag
- resolved source commit
- scaffold runtime-contract baseline hash
- target project name
- explicit project truths that are already known
- any applicable structured project facts that can be verified at install time
- canonical `base_branch` when it can be discovered safely at install time
- canonical control-plane selection under `canonical_control_plane` (`mode`, `checkout_path`, and optional `base_branch`)
- control-plane version-control policy under `control_plane_versioning` (`mode` and optional `.gitignore` patterns)
- `orchestrator_stop_hook` with the default conservative stop-boundary policy
- `worktree_bootstrap_commands` only for explicit worktree hydration setup commands
- `bootstrap_env_files` only for allowlisted env or config files that are safe to copy into a fresh worktree
- `bootstrap_copy_exclude_globs` with the default no-copy excludes for dependency, cache, and build artifacts
- the canonical shared-control-plane ownership rule and `.ralph/shared/` worktree overlay behavior
- `validation_bootstrap_commands` when the project already has known environment-prep commands
- an empty or target-initialized learning summary and learning log
- active epoch
- active spec
- current phase
- current task
- next action
- queue policy assumptions when the project needs overrides
- git, PR, and verification expectations

## What The Installing Agent Should Do During Setup

When an LLM installs this harness into a new or existing project, it should:

1. copy the manifest-listed scaffold from `src/`
2. preserve the canonical shared control plane in the selected canonical checkout and never turn tracked worktree files into symlink replacements
2. create the generated runtime files from `src/generated-runtime-manifest.txt`
3. merge or replace only the managed Ralph blocks if the project already has an `AGENTS.md` or `CLAUDE.md`
4. preserve the target repo’s existing product code
5. adapt `.ralph/constitution.md`, `.ralph/policy/runtime-overrides.md`, `.ralph/policy/project-policy.md`, and the copied `.ralph/context/` files for the target project
6. rewrite the workflow state and spec queue files for the target project
7. update `.ralph/harness-version.json` with tag `v0.13.1`, the resolved source commit, and the scaffold runtime-contract baseline hash
8. seed explicit truths in `.ralph/context/project-truths.md`
9. ask the user through the runtime's question/input tool whether to keep the current checkout as the canonical control plane or use a custom checkout path or branch, then record that in `.ralph/context/project-facts.json` under `canonical_control_plane`
10. ask the user through the runtime's question/input tool whether control-plane artifacts should be tracked or ignored, then record that policy in `.ralph/context/project-facts.json` under `control_plane_versioning` and apply `.gitignore` updates only when requested
11. seed any known structured facts in `.ralph/context/project-facts.json`, including the canonical `base_branch`, and leave unknown or irrelevant facts absent or null
12. install the repo-local hook surfaces and the shared `.ralph/hooks/stop-boundary.py` handler so supported agents can auto-continue only at safe stop boundaries
13. initialize `.ralph/context/learning-summary.md` and `.ralph/context/learning-log.jsonl` for the target project
14. create the project PRD
15. create the epoch map and numbered spec queue
16. create the first numbered spec, spec-local `research.md`, plan, task list, and `task-state.json`
17. append the initial events and reports

## Canonical Install Checklist

An install is correct only if it does all of the following:

1. copies only the scaffold paths listed in `src/install-manifest.txt`
2. creates the generated runtime records listed in `src/generated-runtime-manifest.txt`
3. preserves existing `AGENTS.md` and `CLAUDE.md` files and replaces only the managed Ralph blocks from this guide instead of replacing whole files
4. adapts `.ralph/constitution.md`, `.ralph/policy/runtime-overrides.md`, `.ralph/policy/project-policy.md`, and copied `.ralph/context/` files for the target project
5. rewrites scaffold seed state into target-project state
6. records tag `v0.13.1` plus the resolved source commit in `.ralph/harness-version.json`
7. persists the canonical `base_branch` in `.ralph/context/project-facts.json`
8. asks the user whether the current checkout remains canonical or a custom checkout path or branch should be used, then records that in `.ralph/context/project-facts.json` `canonical_control_plane`
9. asks the user whether control-plane artifacts should be tracked or ignored and records the decision in `.ralph/context/project-facts.json` `control_plane_versioning`
10. seeds the conservative `orchestrator_stop_hook`, `worktree_bootstrap_commands`, `bootstrap_env_files`, and `bootstrap_copy_exclude_globs` facts in `.ralph/context/project-facts.json`
11. installs repo-local `.codex/hooks.json`, `.claude/settings.json`, `.cursor/hooks.json`, and `.ralph/hooks/stop-boundary.py`
12. creates the first real project PRD, epoch map, spec queue, and first numbered spec artifacts
13. avoids copying this repository's repo-root source files into the target repo

## Verification After Installation

At the end of setup, verify:

- every manifest-listed `src/` path exists in the target repo
- `.codex/config.toml` exists, parses, and enables Codex multi-agent
- `.codex/config.toml` exists, parses, and enables Codex hooks
- `.codex/config.toml` enforces `agents.max_depth = 3` so a thin Ralph entry thread can launch one orchestrator peer or role subagent, which may launch worker subagents without allowing deeper fan-out
- `.codex/hooks.json` exists and points `Stop` at `.ralph/hooks/stop-boundary.py`
- `.codex/agents/*.toml` exist and parse
- `.codex/agents/*.toml` all use `sandbox_mode = "danger-full-access"`
- `.claude/settings.json` exists and carries the managed `Stop` hook without requiring user-global hook config
- `.claude/agents/` exists
- `.claude/commands/` exists
- `.cursor/hooks.json` exists and carries the managed `stop` hook
- `.cursor/rules/` exists
- `.ralph/hooks/stop-boundary.py` exists and is shared by all supported adapters
- `.ralph/constitution.md` exists and matches the intended harness doctrine for the target project
- `.ralph/runtime-contract.md` exists and matches the installed runtime doctrine
- `.ralph/policy/runtime-overrides.md` exists and is the project-owned extension surface for runtime-specific additions
- `.ralph/state/execution-claims.json` exists and parses
- `.ralph/runtime-contract.md` includes the queue-lock-plus-claims execution model and the multi-runtime adapter-pack contract
- `.ralph/runtime-contract.md` forbids keeping PRD or planning coordination on the main thread and makes orchestrator peers the only queue-wide control-plane coordinators while they hold the shared scheduler lock
- `.ralph/runtime-contract.md` makes `bootstrap` a required step before implementation begins in a claimed session
- `.ralph/runtime-contract.md` requires spec execution to happen from assigned spec worktrees rather than the canonical checkout
- `.ralph/harness-version.json` exists, parses, and records the selected tag, the resolved source commit, the scaffold runtime-contract baseline hash, the canonical runtime-overrides path, the installed adapter packs, and the default branch prefix
- `.ralph/context/project-truths.md` exists and contains the target project's initial explicit truths or placeholders adapted for that repo
- `.ralph/context/project-facts.json` exists, parses, contains only relevant structured facts for the target repo, and records the canonical `base_branch` when it can be discovered safely
- `.ralph/context/project-facts.json` records explicit canonical control-plane setup in `canonical_control_plane` from the user-facing install question/input step
- `.ralph/context/project-facts.json` records explicit control-plane version-control policy in `control_plane_versioning` from the user-facing install question/input step
- `.ralph/context/project-facts.json` records `orchestrator_stop_hook`, `worktree_bootstrap_commands`, `bootstrap_env_files`, and `bootstrap_copy_exclude_globs`
- `.ralph/context/project-facts.json` uses `validation_bootstrap_commands` only for real environment-prep commands, not speculative placeholders
- `.ralph/context/project-facts.json` keeps `bootstrap_env_files` allowlisted and keeps dependency or build directories out of copied bootstrap inputs by default
- `.ralph/context/learning-summary.md` exists and is initialized for the target repo
- `.ralph/context/learning-log.jsonl` exists and is valid JSONL
- `.ralph/state/workflow-state.json` exists and matches the target project
- `.ralph/state/spec-queue.json` exists and matches the target project
- `.ralph/state/workflow-state.md` matches the JSON state
- `specs/INDEX.md` matches the queue semantically
- `specs/<spec-key>/research.md` exists for any spec whose queue entry marks research complete
- `specs/<spec-key>/task-state.json` exists for seeded specs and matches `tasks.md` semantically
- the target repo did not receive repo-root source-repo docs, validation scripts, or other non-`src/` files by mistake

## Final Result

After installation, the target repository should be ready for Codex, Claude Code, or Cursor to:

- resume from disk
- choose explicit targets first, then fill the remaining ready-set admission window
- let multiple orchestrator peers cooperate through the same control plane while each claimed role stays spec-scoped
- preserve state, queue, logs, and reports
- develop features and bug fixes through the same structured loop
- advance specs only after review, verification, and PR completion
