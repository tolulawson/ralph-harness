# Upgrade Guide

This guide explains how to upgrade an already-installed Ralph harness in a target repository.

`UPGRADING.md` is the canonical upgrade source of truth for this repository.

## Source Of Truth

The upgrade-safe scaffold source is:

- `src/` in [tolulawson/ralph-harness](https://github.com/tolulawson/ralph-harness) at tag `v0.5.0`

The canonical upgrade overwrite contract is:

- [src/upgrade-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.5.0/src/upgrade-manifest.txt)

The current harness version source is:

- [`VERSION`](https://github.com/tolulawson/ralph-harness/blob/v0.5.0/VERSION)

The installed harness metadata file is:

- [src/.ralph/harness-version.json](https://github.com/tolulawson/ralph-harness/blob/v0.5.0/src/.ralph/harness-version.json)

The upgrade authority order is:

1. [UPGRADING.md](https://github.com/tolulawson/ralph-harness/blob/v0.5.0/UPGRADING.md)
2. [src/upgrade-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.5.0/src/upgrade-manifest.txt)
3. [VERSION](https://github.com/tolulawson/ralph-harness/blob/v0.5.0/VERSION)
4. [src/.ralph/harness-version.json](https://github.com/tolulawson/ralph-harness/blob/v0.5.0/src/.ralph/harness-version.json)

## Goal

An upgrade now has two required phases:

1. refresh the scaffold-owned surface from `src/upgrade-manifest.txt`
2. migrate live runtime state into the current interrupt-safe shape

After upgrade, the target repository should:

- keep its project-specific policy, context, reports, logs, and spec prose
- gain the latest scaffold-owned role configs, runtime skills, templates, and runtime contract
- carry current live-state files for workflow, queue, projections, and per-spec task lifecycle
- record the installed Ralph version tag, resolved commit, and migration-aware upgrade contract in `.ralph/harness-version.json`
- preserve or refresh the managed Ralph block in `AGENTS.md`

## Default Reference

Use the latest stable semver tag by default. The current stable example in this guide is `v0.5.0`.

If exact reproducibility matters more than readability, pin to a specific commit SHA instead and still record the human-facing tag when known.

## Optional Helper Skill

No skill is required to upgrade the harness. This document is sufficient on its own.

If a user prefers a named helper entrypoint, this repository also exposes `ralph-upgrade` under `skills/`. That skill is optional and must follow this guide.

Other public `ralph-*` skills such as `ralph-interrupt` are outside the upgrade contract and are used only after the harness is already installed.

## Upgrade Modes

### Option 1: Ask Codex to upgrade the harness

From inside the target repository, ask Codex to upgrade from a tagged release:

```text
Use https://github.com/tolulawson/ralph-harness as the source repository.
Upgrade this repository's installed Ralph harness to tag v0.5.0 using UPGRADING.md as the authoritative guide.
Only overwrite the scaffold-owned paths listed in src/upgrade-manifest.txt.
Preserve project-owned files under .ralph/policy/, .ralph/context/, .ralph/reports/, and .ralph/logs/, and preserve spec prose unless a named migration step below says otherwise.
Refresh the managed Ralph block inside AGENTS.md instead of replacing the whole file.
Run the live-runtime migration phase from UPGRADING.md so workflow-state, spec-queue, task-state, and projection files are upgraded together.
If migration cannot infer historic task lifecycle safely, stop and report the ambiguous spec instead of guessing.
Update .ralph/harness-version.json so it records version 0.5.0, tag v0.5.0, the source repo, the resolved commit used for this upgrade, and upgrade_contract_version 3.
Run the upgrade verification checklist from UPGRADING.md before finishing.
```

### Option 2: Copy the upgrade surface manually

From the parent directory of the target repository:

```bash
SOURCE_REPO_URL=https://github.com/tolulawson/ralph-harness
SOURCE_REF=v0.5.0
TARGET_REPO=/path/to/target-repo
WORK_DIR="$(mktemp -d)"

git clone --depth=1 --branch "$SOURCE_REF" "$SOURCE_REPO_URL" "$WORK_DIR/ralph-harness"
SOURCE_REPO="$WORK_DIR/ralph-harness"

while IFS= read -r path; do
  [[ -z "$path" || "$path" == \#* ]] && continue
  mkdir -p "$TARGET_REPO/$(dirname "$path")"
  rsync -a "$SOURCE_REPO/src/$path" "$TARGET_REPO/$path"
done < "$SOURCE_REPO/src/upgrade-manifest.txt"

python3 "$SOURCE_REPO/scripts/migrate-installed-runtime.py" --repo "$TARGET_REPO"

rm -rf "$WORK_DIR"
```

Then refresh the managed Ralph block in `AGENTS.md`, update `.ralph/harness-version.json`, and run the verification checklist below.

## What Gets Overwritten Automatically

Upgrade only the paths listed in `src/upgrade-manifest.txt`:

- `AGENTS.md` only for the managed Ralph block between `<!-- RALPH-HARNESS:START -->` and `<!-- RALPH-HARNESS:END -->`
- `.codex/config.toml`
- `.codex/agents/`
- `.agents/skills/`
- `.ralph/runtime-contract.md`
- `.ralph/templates/`
- `.ralph/harness-version.json`

## What Must Be Preserved

Do not overwrite these project-owned areas during the manifest-copy phase:

- `.ralph/policy/`
- `.ralph/context/`
- `.ralph/reports/`
- `.ralph/logs/`
- product source files
- spec prose outside explicitly regenerated projection or lifecycle files

The migration phase may update only Ralph-owned live state and projections:

- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/workflow-state.md`
- `specs/INDEX.md`
- missing or stale `specs/<spec-key>/task-state.json`

## Managed `AGENTS.md` Block

The Ralph-owned section in an installed `AGENTS.md` must live between these markers:

```md
<!-- RALPH-HARNESS:START -->
... Ralph loader block ...
<!-- RALPH-HARNESS:END -->
```

If the target repository already has an `AGENTS.md`, preserve its non-Ralph content and replace only the managed block.

If no managed block exists yet, append one at the end of the file.

## Legacy Install, Agent Relocation, And Mixed-Version Migration

Older installs or partial upgrades may be missing one or more of:

- `.ralph/runtime-contract.md`
- `.ralph/harness-version.json`
- `.codex/agents/*.toml`
- legacy repo-root `agents/*.toml`
- `resume_spec_stack` or `interruption_state` in workflow state
- interrupt metadata and `task_state_path` in queue entries
- `specs/<spec-key>/task-state.json`
- current rendered `workflow-state.md` or `specs/INDEX.md`

Run the migration phase after copying the scaffold-owned surface:

```bash
python3 scripts/migrate-installed-runtime.py --repo /path/to/target-repo
```

The migration phase must:

- treat `.codex/agents/*.toml` as the canonical role-config location
- migrate legacy repo-root `agents/*.toml` into `.codex/agents/` when the legacy directory contains only Ralph-managed role configs
- remove the legacy repo-root `agents/` directory only after the canonical `.codex/agents/` targets exist
- stop with a repair error when repo-root `agents/` contains unknown extra files or the canonical `.codex/config.toml` targets still do not exist
- normalize `.ralph/state/workflow-state.json` to the current interrupt-capable shape
- normalize `.ralph/state/spec-queue.json` to the current schema and preemption policy
- backfill missing `task-state.json` files when inference from `tasks.md` and latest reports is clear
- regenerate `.ralph/state/workflow-state.md` and `specs/INDEX.md` from canonical JSON
- stop with a repair error when historic task lifecycle is ambiguous

## Repair Runbook For Drifted Repos

Use this when an installed repo already claims a newer harness version but live state is still mixed-version or drifted.

Typical symptoms include:

- Codex fails because `.codex/config.toml` resolves `agents/<role>.toml` inside `.codex/` but the repo still stores role configs at repo root
- `workflow-state.json` points at a task that `tasks.md` already marks complete
- `workflow-state.md` is missing current interrupt projection rows
- `spec-queue.json` still uses `preemption: emergency_only`
- queue entries are missing `task_state_path`

Repair steps:

1. refresh the scaffold-owned surface from `src/upgrade-manifest.txt`
2. run `python3 scripts/migrate-installed-runtime.py --repo /path/to/target-repo`
3. if migration blocks, repair the named spec so `tasks.md`, reports, and intended lifecycle agree
4. rerun migration
5. run `python3 scripts/check-installed-runtime-state.py --repo /path/to/target-repo`

The runtime is not truthful again until:

- workflow JSON and workflow Markdown agree
- spec queue JSON and `specs/INDEX.md` agree
- `task-state.json` agrees with `tasks.md`
- `workflow-state.json` no longer points at a task that `tasks.md` already marks complete

## What To Update During Upgrade

After copying the upgrade surface and running migration, update:

- the managed Ralph block in `AGENTS.md`
- `.ralph/harness-version.json`

Set at minimum:

- `version`
- `tag`
- `source_repo`
- `resolved_commit`
- `upgrade_contract_version`

For the current migration-aware contract, `upgrade_contract_version` must equal `3`.

## Verification After Upgrade

At the end of the upgrade, verify:

- every path listed in `src/upgrade-manifest.txt` exists in the target repo
- `.codex/config.toml` exists, parses, and enables Codex multi-agent
- `.codex/agents/*.toml` exist and parse
- `.ralph/runtime-contract.md` exists
- `.ralph/harness-version.json` exists, parses, and records the selected tag plus resolved commit
- `.ralph/harness-version.json` records `upgrade_contract_version` `3`
- `python3 scripts/check-installed-runtime-state.py --repo /path/to/target-repo` passes
- the managed Ralph block exists in `AGENTS.md`
- project-owned files under `.ralph/policy/`, `.ralph/context/`, `.ralph/reports/`, and `.ralph/logs/` were preserved unless a named migration step intentionally changed them
- install and upgrade contracts still agree with the current tagged release

## Final Result

After upgrade, the target repository should keep its project history but run on the latest released Ralph scaffold surface, with canonical live state that is safe for interrupt creation and normal queue resumption.
