# Learning Summary

## Promoted Truths

- Add promoted durable truths here.

## Promoted Rules

- Add promoted operational rules here.
- Before cutting a source-repo release, run a doctrine drift pass across the control plane, supporting docs, public skills, generated sub-agent instructions, and other release-facing surfaces so they match the latest contracts.
- Before cutting a new release, explicitly review all shipped role skills, public `ralph-*` skills, doctrine docs, adapter references, and control services for canonical-control-plane alignment.

## Promoted Anti-Patterns

- Add promoted anti-patterns to avoid here.
- Letting one doctrine surface keep generic `.ralph/state` or report-path wording after the canonical-control-plane model changes. That kind of drift causes workers to read or write the wrong state.
