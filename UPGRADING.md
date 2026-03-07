# Upgrade Guide

This guide explains how to upgrade an already-installed Ralph harness in a target repository.

`UPGRADING.md` is the canonical upgrade source of truth for this repository.

## Source Of Truth

The upgrade-safe scaffold source is:

- `src/` in [tolulawson/ralph-harness](https://github.com/tolulawson/ralph-harness) at tag `v0.1.0`

The canonical upgrade overwrite contract is:

- [src/upgrade-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/src/upgrade-manifest.txt)

The current harness version source is:

- [`VERSION`](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/VERSION)

The installed harness metadata file is:

- [src/.ralph/harness-version.json](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/src/.ralph/harness-version.json)

The upgrade authority order is:

1. [UPGRADING.md](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/UPGRADING.md)
2. [src/upgrade-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/src/upgrade-manifest.txt)
3. [VERSION](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/VERSION)
4. [src/.ralph/harness-version.json](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/src/.ralph/harness-version.json)

## Goal

An upgrade should refresh only the Ralph-owned scaffold surface while preserving the target repository's project-specific runtime and history.

After upgrade, the target repository should:

- keep its project-specific policy, context, specs, tasks, reports, and logs
- gain the latest scaffold-owned role configs, runtime skills, templates, and runtime contract
- record the installed Ralph version tag and resolved commit in `.ralph/harness-version.json`
- preserve or refresh the managed Ralph block in `AGENTS.md`

## Default Reference

Use the latest stable semver tag by default. The current stable example in this guide is `v0.1.0`.

If exact reproducibility matters more than readability, pin to a specific commit SHA instead and still record the human-facing tag when known.

## Optional Helper Skill

No skill is required to upgrade the harness. This document is sufficient on its own.

If a user prefers a named helper entrypoint, this repository also exposes `ralph-upgrade` under `skills/`. That skill is optional and must follow this guide.

## Upgrade Modes

### Option 1: Ask Codex to upgrade the harness

From inside the target repository, ask Codex to upgrade from a tagged release:

```text
Use https://github.com/tolulawson/ralph-harness as the source repository.
Upgrade this repository's installed Ralph harness to tag v0.1.0 using UPGRADING.md as the authoritative guide.
Only overwrite the scaffold-owned paths listed in src/upgrade-manifest.txt.
Preserve project-owned files under .ralph/policy/, .ralph/context/, .ralph/state/, tasks/, specs/, .ralph/reports/, and .ralph/logs/ unless a named migration step explicitly targets them.
Refresh the managed Ralph block inside AGENTS.md instead of replacing the whole file.
Update .ralph/harness-version.json so it records version 0.1.0, tag v0.1.0, the source repo, and the resolved commit used for this upgrade.
Run the upgrade verification checklist from UPGRADING.md before finishing.
```

### Option 2: Copy the upgrade surface manually

From the parent directory of the target repository:

```bash
SOURCE_REPO_URL=https://github.com/tolulawson/ralph-harness
SOURCE_REF=v0.1.0
TARGET_REPO=/path/to/target-repo
WORK_DIR="$(mktemp -d)"

git clone --depth=1 --branch "$SOURCE_REF" "$SOURCE_REPO_URL" "$WORK_DIR/ralph-harness"
SOURCE_REPO="$WORK_DIR/ralph-harness"

while IFS= read -r path; do
  [[ -z "$path" || "$path" == \#* ]] && continue
  mkdir -p "$TARGET_REPO/$(dirname "$path")"
  rsync -a "$SOURCE_REPO/src/$path" "$TARGET_REPO/$path"
done < "$SOURCE_REPO/src/upgrade-manifest.txt"

rm -rf "$WORK_DIR"
```

Then refresh the managed Ralph block in `AGENTS.md`, update `.ralph/harness-version.json`, and run the verification checklist below.

## What Gets Overwritten Automatically

Upgrade only the paths listed in `src/upgrade-manifest.txt`:

- `AGENTS.md` only for the managed Ralph block between `<!-- RALPH-HARNESS:START -->` and `<!-- RALPH-HARNESS:END -->`
- `.codex/`
- `agents/`
- `.agents/skills/`
- `.ralph/runtime-contract.md`
- `.ralph/templates/`
- `.ralph/harness-version.json`

## What Must Be Preserved

Do not overwrite these project-owned runtime areas during a normal upgrade:

- `.ralph/policy/`
- `.ralph/context/`
- `.ralph/state/`
- `tasks/`
- `specs/`
- `.ralph/reports/`
- `.ralph/logs/`

Only change them when an explicit migration step in this guide requires it.

## Managed `AGENTS.md` Block

The Ralph-owned section in an installed `AGENTS.md` must live between these markers:

```md
<!-- RALPH-HARNESS:START -->
... Ralph loader block ...
<!-- RALPH-HARNESS:END -->
```

If the target repository already has an `AGENTS.md`, preserve its non-Ralph content and replace only the managed block.

If no managed block exists yet, append one at the end of the file.

## Legacy Install Migration

Older installs may be missing one or more of:

- `.ralph/runtime-contract.md`
- `.ralph/harness-version.json`
- the managed `AGENTS.md` block markers
- `specs/<spec-key>/task-state.json`

When upgrading a legacy install:

1. add `.ralph/runtime-contract.md`
2. add `.ralph/harness-version.json`
3. wrap or replace the Ralph loader section in `AGENTS.md` with the managed block
4. leave existing `.ralph/state/`, `tasks/`, `specs/`, reports, and logs untouched
5. create `specs/<spec-key>/task-state.json` only when the next planning or task-generation pass refreshes that spec

## What To Update During Upgrade

After copying the upgrade surface, update:

- the managed Ralph block in `AGENTS.md`
- `.ralph/harness-version.json`

Set at minimum:

- `version`
- `tag`
- `source_repo`
- `resolved_commit`
- `upgrade_contract_version`

## Verification After Upgrade

At the end of the upgrade, verify:

- every path listed in `src/upgrade-manifest.txt` exists in the target repo
- `.codex/config.toml` exists, parses, and enables Codex multi-agent
- `agents/*.toml` exist and parse
- `.ralph/runtime-contract.md` exists
- `.ralph/harness-version.json` exists, parses, and records the selected tag plus resolved commit
- the managed Ralph block exists in `AGENTS.md`
- `.ralph/policy/`, `.ralph/context/`, `.ralph/state/`, `tasks/`, `specs/`, `.ralph/reports/`, and `.ralph/logs/` were preserved unless a named migration step intentionally changed them
- install and upgrade contracts still agree with the current tagged release

## Final Result

After upgrade, the target repository should keep its project history but run on the latest released Ralph scaffold surface, with a durable record of which tag and commit it is using.
