---
name: learning
description: Classify candidate learnings, append them to the learning log, and promote stable truths or facts into the canonical harness context files when justified by evidence.
---

# Learning

## Use When

- A role report includes candidate learnings.
- The harness needs to decide whether an observation is a truth, fact, rule, anti-pattern, preference, or one-off observation.
- The orchestrator is promoting stable learnings into canonical context.

## Inputs

- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- `.ralph/context/learning-log.jsonl`
- current role report
- relevant evidence from specs, reports, verification output, or repo inspection

## Classification

Classify each candidate as one of:

- `truth`
- `fact`
- `rule`
- `anti_pattern`
- `preference`
- `observation`

## Promotion Rules

- Write explicit human instructions and durable repo rules to `project-truths.md`.
- Write optional structured facts that actually apply to the project to `project-facts.json`.
- Write promoted stable learnings to `learning-summary.md`.
- Append weak, one-off, or still-uncertain items only to `learning-log.jsonl`.
- Do not invent facts for categories that are not relevant to the project.

## Evidence Rules

- Attach exact artifact or command evidence whenever possible.
- Distinguish confirmed truths from recommendations.
- If evidence is weak, keep the item as a log entry instead of promoting it.

## Stop Condition

Stop once the candidate learnings have been classified and the appropriate append or promotion action is clear.
