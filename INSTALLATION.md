# Installation Guide

This guide explains how an LLM or human operator should install the Codex-native Ralph harness into a target repository.

`INSTALLATION.md` is the canonical install source of truth for this repository.

## Source Of Truth

The installable scaffold source is:

- `src/` in [tolulawson/ralph-harness](https://github.com/tolulawson/ralph-harness) at tag `v0.1.0`

The canonical copy contract is:

- [src/install-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/src/install-manifest.txt)

The canonical generated-runtime contract is:

- [src/generated-runtime-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/src/generated-runtime-manifest.txt)

The current harness version source is:

- [`VERSION`](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/VERSION)

The install authority order is:

1. [INSTALLATION.md](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/INSTALLATION.md)
2. [src/install-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/src/install-manifest.txt)
3. [src/generated-runtime-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/src/generated-runtime-manifest.txt)
4. [VERSION](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/VERSION)

Do not install from the repository root. The root contains this repository’s live dogfood runtime history.

## Goal

After installation, the target repository should contain:

- the Codex loader
- the harness constitution
- the runtime contract
- the Codex control plane
- repo-local role skills
- neutral seed runtime state and templates
- generated runtime tracking files, logs, and report directories
- project-specific policy
- a starter spec register

## Optional Helper Skill

No skill is required to install the harness. This document is sufficient on its own.

If a user prefers a named helper entrypoint, this repository also exposes `ralph-install` under `skills/`. That skill is optional and must follow this guide.

Other public `ralph-*` skills are outside the install contract and are not needed to install the harness. Use `ralph-upgrade` only after the harness is already installed.

## Installation Modes

### Option 1: Ask Codex to install the harness

This is the intended workflow.

From inside the target repository, ask Codex to use `src/` as the source template:

```text
Use https://github.com/tolulawson/ralph-harness as the scaffold source repository.
Use tag v0.1.0 from that repository unless the user explicitly requests another release.
Use the scaffold under src/ in that repository.
Install the Codex-native harness into this repository using src/install-manifest.txt as the copy contract.
Preserve the existing AGENTS.md if one already exists and replace only the managed Ralph block between <!-- RALPH-HARNESS:START --> and <!-- RALPH-HARNESS:END -->.
The managed Ralph block must tell Codex to read .ralph/constitution.md, .ralph/runtime-contract.md, .ralph/policy/project-policy.md, .ralph/context/project-truths.md, .ralph/context/project-facts.json, .ralph/context/learning-summary.md, .ralph/state/workflow-state.json, .ralph/state/spec-queue.json, the latest report, and only a recent tail of .ralph/context/learning-log.jsonl when diagnosing or promoting learnings.
Copy only the manifest-listed control-plane files, runtime skills, neutral seed state files, and templates.
Then create the generated runtime files listed in src/generated-runtime-manifest.txt.
Do not copy the source repo's dogfood runtime logs, reports, PRD, or numbered spec history.
Adapt the constitution, runtime contract pointers, project policy, and copied knowledge files for this repo, preserve existing code, create the project PRD, decompose it into epochs and numbered specs, seed the initial FIFO spec queue, and update .ralph/harness-version.json with tag v0.1.0 and the resolved commit.
```

### Option 2: Copy the scaffold manually

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
done < "$SOURCE_REPO/src/install-manifest.txt"

rm -rf "$WORK_DIR"
```

Then create the runtime files listed in [src/generated-runtime-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/src/generated-runtime-manifest.txt), refresh the managed Ralph block in `AGENTS.md`, update `.ralph/harness-version.json`, and adapt the target repository before first use.

## Optional Skill-Driven Entry

If `ralph-install` is available, you may invoke it as a convenience entrypoint.

That skill is not required for installation and does not replace this guide. It must execute the workflow defined here.

## What Gets Copied

Copy only the manifest-listed scaffold paths from `src/`:

- `AGENTS.md`
- `.codex/`
- `agents/`
- `.agents/skills/`
- `.ralph/constitution.md`
- `.ralph/runtime-contract.md`
- `.ralph/harness-version.json`
- `.ralph/context/`
- `.ralph/policy/`
- `.ralph/state/`
- `.ralph/templates/`
- `specs/INDEX.md`

## What Gets Generated After Copy

After copying the scaffold, create the runtime records listed in [src/generated-runtime-manifest.txt](https://github.com/tolulawson/ralph-harness/blob/v0.1.0/src/generated-runtime-manifest.txt):

- `tasks/todo.md`
- `tasks/lessons.md`
- `.ralph/logs/events.jsonl`
- `.ralph/reports/`
- `.ralph/summaries/`

## What Must Not Be Copied

Do not copy these root dogfood runtime paths into target repos:

- `/.ralph/logs/events.jsonl`
- `/.ralph/reports/bootstrap-20260305/`
- `/.ralph/state/workflow-state.json`
- `/.ralph/state/spec-queue.json`
- `/.ralph/state/workflow-state.md`
- `/tasks/prd-ralph-harness.md`
- `/specs/001-self-bootstrap-harness/`

Those belong only to this repository’s own live runtime.

## Existing `AGENTS.md` Handling

If the target repository already has an `AGENTS.md`, do not replace it wholesale.

## Canonical AGENTS Loader Snippet

The Ralph-owned block in the installed `AGENTS.md` must live between these markers:

```md
<!-- RALPH-HARNESS:START -->
... Ralph loader block ...
<!-- RALPH-HARNESS:END -->
```

That managed block should say, in substance:

- this repo uses the Ralph harness
- Codex should read `.ralph/constitution.md`
- then read `.ralph/runtime-contract.md`
- then read `.ralph/policy/project-policy.md`
- then read `.ralph/context/project-truths.md`
- then read `.ralph/context/project-facts.json`
- then read `.ralph/context/learning-summary.md`
- then read `.ralph/state/workflow-state.json`
- then read `.ralph/state/spec-queue.json`
- then read the latest report referenced by `last_report_path`
- then read only a recent tail of `.ralph/context/learning-log.jsonl` when diagnosing or promoting learnings

The root `AGENTS.md` in the target repo should remain a loader, not the full harness doctrine.

## What To Reset For The Target Repository

After copying from `src/`, rewrite:

- `.ralph/harness-version.json`
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
- target project name
- explicit project truths that are already known
- any applicable structured project facts that can be verified at install time
- an empty or target-initialized learning summary and learning log
- active epoch
- active spec
- current phase
- current task
- next action
- queue policy assumptions when the project needs overrides
- git, PR, and verification expectations

## What Codex Should Do During Setup

When an LLM installs this harness into a new or existing project, it should:

1. copy the manifest-listed scaffold from `src/`
2. create the generated runtime files from `src/generated-runtime-manifest.txt`
3. merge or replace only the managed AGENTS loader block if the project already has an `AGENTS.md`
4. preserve the target repo’s existing product code
5. adapt `.ralph/constitution.md`, `.ralph/runtime-contract.md`, `.ralph/policy/project-policy.md`, and the copied `.ralph/context/` files for the target project
6. rewrite the workflow state and spec queue files for the target project
7. update `.ralph/harness-version.json` with tag `v0.1.0` and the resolved source commit
8. seed explicit truths in `.ralph/context/project-truths.md`
9. seed any known structured facts in `.ralph/context/project-facts.json` and leave unknown or irrelevant facts absent or null
10. initialize `.ralph/context/learning-summary.md` and `.ralph/context/learning-log.jsonl` for the target project
11. create the project PRD
12. create the epoch map and numbered spec queue
13. create the first numbered spec, plan, task list, and `task-state.json`
14. append the initial events and reports

## Canonical Install Checklist

An install is correct only if it does all of the following:

1. copies only the scaffold paths listed in `src/install-manifest.txt`
2. creates the generated runtime records listed in `src/generated-runtime-manifest.txt`
3. preserves an existing `AGENTS.md` and replaces only the managed Ralph block from this guide instead of replacing the whole file
4. adapts `.ralph/constitution.md`, `.ralph/runtime-contract.md`, `.ralph/policy/project-policy.md`, and copied `.ralph/context/` files for the target project
5. rewrites scaffold seed state into target-project state
6. records tag `v0.1.0` plus the resolved source commit in `.ralph/harness-version.json`
7. creates the first real project PRD, epoch map, spec queue, and first numbered spec artifacts
8. avoids copying this repository's root dogfood runtime files into the target repo

## Verification After Installation

At the end of setup, verify:

- every manifest-listed `src/` path exists in the target repo
- `.codex/config.toml` exists, parses, and enables Codex multi-agent
- `agents/*.toml` exist and parse
- `.ralph/constitution.md` exists and matches the intended harness doctrine for the target project
- `.ralph/runtime-contract.md` exists and matches the installed runtime doctrine
- `.ralph/harness-version.json` exists, parses, and records tag `v0.1.0` plus the resolved source commit
- `.ralph/context/project-truths.md` exists and contains the target project's initial explicit truths or placeholders adapted for that repo
- `.ralph/context/project-facts.json` exists, parses, and contains only relevant structured facts for the target repo
- `.ralph/context/learning-summary.md` exists and is initialized for the target repo
- `.ralph/context/learning-log.jsonl` exists and is valid JSONL
- `.ralph/state/workflow-state.json` exists and matches the target project
- `.ralph/state/spec-queue.json` exists and matches the target project
- `.ralph/state/workflow-state.md` matches the JSON state
- `specs/INDEX.md` matches the queue semantically
- `specs/<spec-key>/task-state.json` exists for seeded specs and matches `tasks.md` semantically
- the target repo did not receive this source repo’s dogfood PRD, numbered spec history, reports, or event log

## Final Result

After installation, the target repository should be ready for Codex to:

- resume from disk
- choose the next spec from the FIFO queue
- run one focused worker at a time
- preserve state, queue, logs, and reports
- develop features and bug fixes through the same structured loop
- advance specs only after review, verification, and PR completion
