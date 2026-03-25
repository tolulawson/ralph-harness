# Upgrade Guide

This guide explains how to upgrade an already-installed Ralph harness in a target repository.

`UPGRADING.md` is the canonical upgrade source of truth for this repository.

## Source Of Truth

The upgrade-safe scaffold source is:

- `src/` in [tolulawson/ralph-harness](https://github.com/tolulawson/ralph-harness) at tag `v0.9.0`

The canonical upgrade overwrite contract is:

- [src/upgrade-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.9.0/src/upgrade-manifest.txt)

The current harness version source is:

- [`VERSION`](https://github.com/tolulawson/ralph-harness/blob/v0.9.0/VERSION)

The installed harness metadata file is:

- [src/.ralph/harness-version.json](https://github.com/tolulawson/ralph-harness/blob/v0.9.0/src/.ralph/harness-version.json)

The upgrade authority order is:

1. [UPGRADING.md](https://github.com/tolulawson/ralph-harness/blob/v0.9.0/UPGRADING.md)
2. [src/upgrade-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.9.0/src/upgrade-manifest.txt)
3. [VERSION](https://github.com/tolulawson/ralph-harness/blob/v0.9.0/VERSION)
4. [src/.ralph/harness-version.json](https://github.com/tolulawson/ralph-harness/blob/v0.9.0/src/.ralph/harness-version.json)

## Goal

An upgrade now has two required phases:

1. refresh the scaffold-owned surface from `src/upgrade-manifest.txt`
2. migrate live runtime state into the current multi-spec, lease-safe shape

After upgrade, the target repository should:

- keep its project-specific policy, context, reports, logs, and spec prose
- keep its project-owned runtime overrides in `.ralph/policy/runtime-overrides.md`
- gain the latest scaffold-owned role configs, runtime skills, templates, and runtime contract
- gain the shipped `research` and `plan-check` roles plus the bounded same-batch research contract
- carry current live-state files for workflow, queue, lease, durable intents, projections, worktree coordination, and per-spec task lifecycle
- normalize legacy worker report pointers from root-level `.ralph/reports/<run-id>/<role>.md` paths into spec-scoped `.ralph/reports/<run-id>/<spec-key>/<role>.md` paths when ownership is unambiguous
- record the installed Ralph version tag, resolved commit, and migration-aware upgrade contract in `.ralph/harness-version.json`
- preserve or refresh the managed Ralph blocks in `AGENTS.md` and `CLAUDE.md`

An upgrade must not run over a healthy live orchestrator lease. If `.ralph/state/orchestrator-lease.json` still shows an active non-expired holder, stop and retry after the live run releases or times out. Expired or malformed held leases are treated as stale and should be recovered to `idle` during migration before shared-state rewrite continues.

## Default Reference

Use the latest stable semver tag by default. The current stable example in this guide is `v0.9.0`.

If exact reproducibility matters more than readability, pin to a specific commit SHA instead and still record the human-facing tag when known.

## Optional Helper Skill

No skill is required to upgrade the harness. This document is sufficient on its own.

If a user prefers a named helper entrypoint, this repository also exposes `ralph-upgrade` under `skills/`. That skill is optional and must follow this guide.

Other public `ralph-*` skills such as `ralph-interrupt` are outside the upgrade contract and are used only after the harness is already installed.

## Upgrade Modes

### Option 1: Ask your coding agent to upgrade the harness

From inside the target repository, ask your coding agent to upgrade from a tagged release:

```text
Use https://github.com/tolulawson/ralph-harness as the source repository.
Upgrade this repository's installed Ralph harness to tag v0.9.0 using UPGRADING.md as the authoritative guide.
Run the upgrade preflight first so direct edits to the installed .ralph/runtime-contract.md are detected before any scaffold-owned files are overwritten.
If the preflight reports drift in .ralph/runtime-contract.md, move those project-specific runtime rules into .ralph/policy/runtime-overrides.md before continuing.
Only overwrite the scaffold-owned paths listed in src/upgrade-manifest.txt.
Preserve project-owned files under .ralph/policy/, .ralph/context/, .ralph/reports/, and .ralph/logs/, and preserve spec prose unless a named migration step below says otherwise.
Refresh the managed Ralph blocks inside AGENTS.md and CLAUDE.md instead of replacing the whole files.
Run the live-runtime migration phase from UPGRADING.md so workflow-state, spec-queue, lease state, worker claims, durable intents, task-state, projection files, worktree metadata, and the runtime adapter packs are upgraded together.
If .ralph/state/orchestrator-lease.json still shows a healthy held lease, stop instead of upgrading over live orchestration.
If migration cannot infer historic task lifecycle safely, stop and report the ambiguous spec instead of guessing.
Update .ralph/harness-version.json so it records version 0.9.0, tag v0.9.0, the source repo, the resolved commit used for this upgrade, upgrade_contract_version 8, the scaffold runtime-contract baseline hash, the canonical runtime-overrides path, the installed runtime adapters, and the preserved branch prefix.
Run the upgrade verification checklist from UPGRADING.md before finishing.
```

### Option 2: Copy the upgrade surface manually

From the parent directory of the target repository:

```bash
SOURCE_REPO_URL=https://github.com/tolulawson/ralph-harness
SOURCE_REF=v0.9.0
TARGET_REPO=/path/to/target-repo
WORK_DIR="$(mktemp -d)"

git clone --depth=1 --branch "$SOURCE_REF" "$SOURCE_REPO_URL" "$WORK_DIR/ralph-harness"
SOURCE_REPO="$WORK_DIR/ralph-harness"

python3 "$SOURCE_REPO/scripts/check-upgrade-surface.py" --repo "$TARGET_REPO"

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
- `CLAUDE.md` only for the managed Ralph block between `<!-- RALPH-HARNESS:START -->` and `<!-- RALPH-HARNESS:END -->`
- `.codex/agents/`
- `.claude/agents/`
- `.claude/commands/`
- `.cursor/rules/`
- `.agents/skills/`
- `.ralph/runtime-contract.md`
- `.ralph/templates/`
- `.ralph/harness-version.json`

## What Must Be Preserved

Do not overwrite these project-owned areas during the manifest-copy phase:

- user-owned values inside `.codex/config.toml`, such as `sandbox_mode`, model preferences, or custom agent entries
- `.ralph/policy/`
- `.ralph/context/`
- `.ralph/reports/`
- `.ralph/logs/`
- product source files
- spec prose outside explicitly regenerated projection or lifecycle files

The migration phase may update only Ralph-owned live state and projections, plus merge Ralph-required changes into `.codex/config.toml` without clobbering user-owned settings:

- `.codex/config.toml`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/orchestrator-lease.json`
- `.ralph/state/worker-claims.json`
- `.ralph/state/orchestrator-intents.jsonl`
- `.ralph/state/workflow-state.md`
- `specs/INDEX.md`
- missing or stale `specs/<spec-key>/task-state.json`

Before the manifest-copy phase, run the upgrade preflight:

```bash
python3 scripts/check-upgrade-surface.py --repo /path/to/target-repo
```

That preflight must:

- compare the installed `.ralph/runtime-contract.md` against the canonical baseline recorded in `.ralph/harness-version.json`
- stop for manual review instead of guessing when no canonical baseline can be determined
- stop when the base runtime contract was edited directly
- direct the operator to move project-specific runtime rules into `.ralph/policy/runtime-overrides.md` before retrying

## Managed `AGENTS.md` Block

The Ralph-owned section in an installed `AGENTS.md` must live between these markers:

```md
<!-- RALPH-HARNESS:START -->
... Ralph loader block ...
<!-- RALPH-HARNESS:END -->
```

If the target repository already has an `AGENTS.md` or `CLAUDE.md`, preserve non-Ralph content and replace only the managed Ralph block.

If no managed block exists yet, append one at the end of the file.

## Legacy Install, Agent Relocation, And Mixed-Version Migration

Older installs or partial upgrades may be missing one or more of:

- `.ralph/runtime-contract.md`
- `.ralph/policy/runtime-overrides.md`
- `.ralph/harness-version.json`
- `.codex/agents/*.toml`
- legacy repo-root `agents/*.toml`
- `.ralph/state/orchestrator-lease.json`
- `.ralph/state/worker-claims.json`
- `.ralph/state/orchestrator-intents.jsonl`
- `resume_spec_stack` or `interruption_state` in workflow state
- interrupt metadata and `task_state_path` in queue entries
- multi-spec scheduler metadata such as `active_spec_ids`, `depends_on_spec_ids`, worktree fields, or admission state
- `specs/<spec-key>/task-state.json`
- current rendered `workflow-state.md` or `specs/INDEX.md`

Run the migration phase after copying the scaffold-owned surface:

```bash
python3 scripts/migrate-installed-runtime.py --repo /path/to/target-repo
```

The migration phase must:

- merge the installed `.codex/config.toml` with the scaffold config so user-owned settings survive while Ralph-required feature flags and managed role mappings stay current
- preserve user-owned `.codex/config.toml` values while enforcing Ralph-managed delegation safety caps (`agents.max_depth <= 2`)
- treat `.codex/agents/*.toml` as the canonical role-config location
- ensure all role configs use `sandbox_mode = "danger-full-access"`
- migrate legacy repo-root `agents/*.toml` into `.codex/agents/` when the legacy directory contains only Ralph-managed role configs
- remove the legacy repo-root `agents/` directory only after the canonical `.codex/agents/` targets exist
- stop with a repair error when repo-root `agents/` contains unknown extra files or the canonical `.codex/config.toml` targets still do not exist
- create `.ralph/policy/runtime-overrides.md` when it is missing so future project-specific runtime additions have a preserved home
- normalize `.ralph/state/workflow-state.json` to the current multi-spec scheduler shape
- normalize `.ralph/state/spec-queue.json` to the current schema, admission policy, and dependency model
- create or normalize `.ralph/state/orchestrator-lease.json` and `.ralph/state/orchestrator-intents.jsonl`
- stop immediately when `.ralph/state/orchestrator-lease.json` still shows a healthy non-expired holder for another live run
- recover stale held lease state back to `idle` when the lease is expired, malformed, or otherwise no longer healthy
- enforce the lease-plus-claims execution contract in runtime files, including the cross-runtime worker-claim registry
- backfill default worktree metadata, create `.ralph/worktrees/`, and reassign safely-derivable duplicate worktree names or paths onto unique `.ralph/worktrees/<spec-key>` slots
- stop with a repair error when multiple specs already claim the same branch name or when worktree collisions are not safely derivable
- normalize legacy spec-owned worker report pointers into spec-scoped report paths by copying the historic report file into `.ralph/reports/<run-id>/<spec-key>/<role>.md` when ownership is clear
- stop with a repair error when the same legacy worker report path is claimed by multiple specs
- backfill missing `task-state.json` files when inference from `tasks.md` and latest reports is clear
- normalize per-spec research metadata and task-state requirement or verification metadata to the current schema
- regenerate `.ralph/state/workflow-state.md` and `specs/INDEX.md` from canonical JSON
- stop with a repair error when historic task lifecycle is ambiguous

## Repair Runbook For Drifted Repos

Use this when an installed repo already claims a newer harness version but live state is still mixed-version or drifted.

Typical symptoms include:

- Codex fails because `.codex/config.toml` resolves `agents/<role>.toml` inside `.codex/` but the repo still stores role configs at repo root
- an upgrade reset a user-tuned `.codex/config.toml` setting such as `sandbox_mode`
- `workflow-state.json` points at a task that `tasks.md` already marks complete
- `workflow-state.md` is missing current multi-spec projection rows
- `spec-queue.json` still uses `preemption: emergency_only`
- queue entries are missing `task_state_path`
- queue entries are missing `depends_on_spec_ids` or worktree metadata
- `.ralph/state/orchestrator-lease.json` still claims a held lease long after the last orchestrator run died
- multiple specs claim the same `branch_name`, `worktree_name`, or `worktree_path`
- multiple specs still point at the same legacy root-level worker report file

Repair steps:

1. refresh the scaffold-owned surface from `src/upgrade-manifest.txt`
2. inspect `.ralph/state/orchestrator-lease.json`; if it is healthy and still held, stop the live run first instead of upgrading over it
3. run `python3 scripts/migrate-installed-runtime.py --repo /path/to/target-repo`
4. if migration blocks, repair the named spec so `tasks.md`, reports, intended lifecycle, and branch ownership agree
5. rerun migration
6. run `python3 scripts/check-installed-runtime-state.py --repo /path/to/target-repo`

The runtime is not truthful again until:

- workflow JSON and workflow Markdown agree
- spec queue JSON and `specs/INDEX.md` agree
- `task-state.json` agrees with `tasks.md`
- `workflow-state.json` no longer points at a task that `tasks.md` already marks complete
- `.ralph/state/orchestrator-lease.json` is either idle or held by a currently healthy live run
- every spec has a unique `branch_name`, `worktree_name`, and `worktree_path`
- spec-owned worker report pointers use spec-scoped paths when the source reports existed and ownership was clear

## What To Update During Upgrade

After copying the upgrade surface and running migration, update:

- the managed Ralph blocks in `AGENTS.md` and `CLAUDE.md`
- `.ralph/harness-version.json`

Set at minimum:

- `version`
- `tag`
- `source_repo`
- `resolved_commit`
- `upgrade_contract_version`
- `runtime_contract_baseline_sha256`
- `runtime_overrides_path`
- `runtime_adapters`
- `branch_prefix`

For the current migration-aware contract, `upgrade_contract_version` must equal `8`.

## Verification After Upgrade

At the end of the upgrade, verify:

- every path listed in `src/upgrade-manifest.txt` exists in the target repo
- `.codex/config.toml` exists, parses, and enables Codex multi-agent
- `.codex/agents/*.toml` exist and parse
- `.claude/agents/` exists
- `.claude/commands/` exists
- `.cursor/rules/` exists
- `.ralph/runtime-contract.md` exists
- `.ralph/policy/runtime-overrides.md` exists and preserves project-specific runtime additions
- `.ralph/harness-version.json` exists, parses, and records the selected tag plus resolved commit
- `.ralph/harness-version.json` records `upgrade_contract_version` `8`
- `.ralph/harness-version.json` records the current `.ralph/runtime-contract.md` baseline hash and the canonical runtime-overrides path
- `.ralph/harness-version.json` records the installed runtime adapters and the preserved branch prefix
- `python3 scripts/check-installed-runtime-state.py --repo /path/to/target-repo` passes
- `.codex/config.toml` preserves user-owned settings while containing the current Ralph-managed feature flag and role mappings
- `.codex/config.toml` enforces `agents.max_depth <= 2`
- `.codex/agents/*.toml` all use `sandbox_mode = "danger-full-access"`
- `.ralph/state/worker-claims.json` exists, parses, and carries the shared claim registry
- runtime contract and orchestrator skill both enforce the lease-plus-claims execution model
- queue entries now carry research metadata, and existing task-state files are normalized to the current schema
- `.ralph/state/orchestrator-lease.json` is not left in a stale held state
- no two specs claim the same `branch_name`, `worktree_name`, or `worktree_path`
- legacy worker reports have been normalized into spec-scoped report paths when the upgrade could attribute them safely
- the managed Ralph blocks exist in `AGENTS.md` and `CLAUDE.md`
- project-owned files under `.ralph/policy/`, `.ralph/context/`, `.ralph/reports/`, and `.ralph/logs/` were preserved unless a named migration step intentionally changed them
- install and upgrade contracts still agree with the current tagged release

## Final Result

After upgrade, the target repository should keep its project history but run on the latest released Ralph scaffold surface, with canonical live state that is safe for interrupt creation and normal queue resumption.
