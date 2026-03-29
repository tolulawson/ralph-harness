# Project Truths

## Repo Truths

- Add explicit project facts and invariants here when they are confirmed.

## Do

- Add durable instructions the harness should follow for this project.

## Do Not

- Add project-specific prohibitions here.

## Avoid

- Add anti-patterns and risky behaviors to avoid here.

## Architecture Invariants

- Add invariants that should not be violated here.

## Operational Expectations

- Add runtime, release, verification, and workflow expectations here.
- Before publishing a Ralph release from this repository, audit the control-plane doctrine, supporting docs, public skills, generated sub-agent instructions, and related release surfaces for drift from the latest contracts and worktree or bootstrap rules.
- Before every new release from this source repository, review all shipped role skills, public `ralph-*` skills, doctrine files, adapter references, and control services so they all express the same canonical-control-plane ownership model.
- Treat doctrine drift between skills, docs, and control services as a release blocker because misaligned control-plane guidance can produce invalid runtime state.
