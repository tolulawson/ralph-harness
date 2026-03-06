# Installation Guide

This guide explains how an LLM or human operator should install the Codex-native Ralph harness into a target repository.

## Source Of Truth

The installable scaffold source is:

- [src/](/Users/tolu/Desktop/dev/ralph-harness/src)

The canonical copy contract is:

- [src/install-manifest.txt](/Users/tolu/Desktop/dev/ralph-harness/src/install-manifest.txt)

Do not install from the repository root. The root contains this repository’s live dogfood runtime history.

## Goal

After installation, the target repository should contain:

- the Codex loader
- the harness constitution
- the Codex control plane
- repo-local role skills
- seed runtime state, queue, logs, reports, and templates
- project-specific policy
- starter task tracking files
- a starter spec register

## Installable Skills

This repository exposes four distributable source skills under `skills/`:

- `ralph-install`
- `ralph-prd`
- `ralph-plan`
- `ralph-execute`

Use:

- `ralph-install` to install the scaffold from `src/`
- `ralph-prd` to generate or update the project PRD directly
- `ralph-plan` to create the epoch map, numbered spec queue, and planning artifacts directly
- `ralph-execute` to resume an already-installed harness in a target repository

## Installation Modes

### Option 1: Ask Codex to install the harness

This is the intended workflow.

If a third-party skill installer is available, install `ralph-install` first and then invoke it explicitly in the target repo.

From inside the target repository, ask Codex to use `src/` as the source template:

```text
Use /Users/tolu/Desktop/dev/ralph-harness/src as the scaffold source.
Install the Codex-native harness into this repository using src/install-manifest.txt as the copy contract.
Preserve the existing AGENTS.md if one already exists and append a Ralph harness section that tells Codex to read .ralph/constitution.md, .ralph/policy/project-policy.md, .ralph/state/workflow-state.json, .ralph/state/spec-queue.json, and the latest report.
Copy only the manifest-listed control-plane files, runtime skills, seed state files, and templates.
Do not copy the source repo's dogfood runtime logs, reports, PRD, or numbered spec history.
Adapt the constitution and project policy for this repo, preserve existing code, create the project PRD, decompose it into epochs and numbered specs, and seed the initial FIFO spec queue.
```

### Option 2: Copy the scaffold manually

From the parent directory of the target repository:

```bash
rsync -av \
  --exclude '.git' \
  /Users/tolu/Desktop/dev/ralph-harness/src/ \
  /path/to/target-repo/
```

Then review [src/install-manifest.txt](/Users/tolu/Desktop/dev/ralph-harness/src/install-manifest.txt) and adapt the target repository before first use.

## What Gets Copied

Copy only the manifest-listed scaffold paths from `src/`:

- `AGENTS.md`
- `.codex/`
- `agents/`
- `.agents/skills/`
- `.ralph/constitution.md`
- `.ralph/policy/`
- `.ralph/state/`
- `.ralph/templates/`
- `.ralph/logs/`
- `.ralph/reports/`
- `.ralph/summaries/`
- `tasks/todo.md`
- `tasks/lessons.md`
- `specs/INDEX.md`

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

Append a short Ralph harness section that says, in substance:

- this repo uses the Ralph harness
- Codex should read `.ralph/constitution.md`
- then read `.ralph/policy/project-policy.md`
- then read `.ralph/state/workflow-state.json`
- then read `.ralph/state/spec-queue.json`
- then read the latest report referenced by `last_report_path`

The root `AGENTS.md` in the target repo should remain a loader, not the full harness doctrine.

## What To Reset For The Target Repository

After copying from `src/`, rewrite:

- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/workflow-state.md`
- `specs/INDEX.md`
- `tasks/todo.md`

Set at minimum:

- target project name
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
2. merge or append the AGENTS loader instructions if the project already has an `AGENTS.md`
3. preserve the target repo’s existing product code
4. adapt `.ralph/constitution.md` and `.ralph/policy/project-policy.md`
5. rewrite the workflow state and spec queue files for the target project
6. create the project PRD
7. create the epoch map and numbered spec queue
8. create the first numbered spec, plan, and task list
9. append the initial events and reports

## Verification After Installation

At the end of setup, verify:

- every manifest-listed `src/` path exists in the target repo
- `.codex/config.toml` exists and parses
- `agents/*.toml` exist and parse
- `.ralph/constitution.md` exists and matches the intended harness doctrine for the target project
- `.ralph/state/workflow-state.json` exists and matches the target project
- `.ralph/state/spec-queue.json` exists and matches the target project
- `.ralph/state/workflow-state.md` mirrors the JSON state
- `specs/INDEX.md` mirrors the queue semantically
- the target repo did not receive this source repo’s dogfood PRD, numbered spec history, reports, or event log

## Final Result

After installation, the target repository should be ready for Codex to:

- resume from disk
- choose the next spec from the FIFO queue
- run one focused worker at a time
- preserve state, queue, logs, and reports
- develop features and bug fixes through the same structured loop
- advance specs only after review, verification, and PR completion
